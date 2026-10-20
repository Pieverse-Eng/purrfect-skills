#!/usr/bin/env python3
"""Score an eval run directory against the corpus and print a verdict report.

Usage:
    EVAL_CORPUS=/path/to/corpus.json python3 eval-analyze.py <run_dir>

Or compare two runs (e.g. baseline vs after-fix):
    EVAL_CORPUS=/path/to/corpus.json python3 eval-analyze.py <run_dir_a> <run_dir_b>

Verdicts per prompt:
    ✅ PASS              tool used a `must_use` candidate AND must_contain fully satisfied AND no violations
    ✅ PASS (fallback)   content fully satisfied AND no violations, but tool path was a fallback (e.g. shell)
    🟡 PARTIAL          some content match, no violations, no abort/preamble
    ❌ FAIL (abort)     openclaw error marker in payloads
    ❌ FAIL (preamble)  agent emitted "let me check…" with very low output tokens — work was promised but never delivered
    ❌ FAIL (violation) must_not_contain matched
    ❌ FAIL             no tool call AND no content match

Aggregate metrics: PASS/PARTIAL/FAIL counts, avg/median duration, avg/total input+output tokens, MCP-call rate.
"""
import json
import os
import statistics
import sys
from pathlib import Path

CORPUS_ENV = 'EVAL_CORPUS'


def load_corpus():
    path = os.environ.get(CORPUS_ENV)
    if not path:
        sys.stderr.write(f'set {CORPUS_ENV} env var to corpus.json path\n')
        sys.exit(2)
    return json.load(open(path)), path


def load_cli(p):
    try:
        return json.load(open(p))
    except Exception as e:
        return {'_error': str(e)}


def load_session(p):
    if not os.path.exists(p):
        return []
    rows = []
    for ln in open(p):
        ln = ln.strip()
        if not ln:
            continue
        try:
            rows.append(json.loads(ln))
        except Exception:
            pass
    return rows


def extract_response_text(cli):
    if '_error' in cli:
        return f'[CLI ERROR: {cli["_error"]}]'
    payloads = (cli.get('result') or {}).get('payloads') or []
    return '\n\n'.join(p.get('text', '') for p in payloads if p.get('text'))


def extract_tool_calls(session):
    out = []
    for row in session:
        if row.get('type') != 'message':
            continue
        msg = row.get('message', {})
        if msg.get('role') != 'assistant':
            continue
        for c in (msg.get('content') or []):
            if not isinstance(c, dict):
                continue
            if c.get('type') == 'toolCall':
                out.append({
                    'name': c.get('name', '?'),
                    'input_preview': json.dumps(c.get('input'), ensure_ascii=False)[:200] if c.get('input') else '',
                })
    return out


def score_tool(expected, actual):
    """expected: list like ['purrfect_product_list', 'exec:product list', '!purrfect_'].
       Items prefixed with '!' are FORBIDDEN (must not appear).
       Items with 'kind:pat' match a tool by kind (e.g. exec) where input contains pat.
       Returns (status, detail).
    """
    forbidden = [e[1:] for e in expected if e.startswith('!')]
    allowed = [e for e in expected if not e.startswith('!')]

    # Forbidden check — applies regardless of allowed
    for call in actual:
        for f in forbidden:
            if f in call['name'] or f in call['input_preview']:
                return ('violation', f'forbidden tool used: {call["name"]} (matches !{f})')

    if not allowed:
        # off-skill prompt — any non-forbidden activity is fine
        return ('match', 'off-skill: no forbidden tools used')

    for exp in allowed:
        if ':' in exp:
            kind, pat = exp.split(':', 1)
            for call in actual:
                if call['name'] == kind and pat in call['input_preview']:
                    return ('match', f'used {kind} matching "{pat}"')
        else:
            for call in actual:
                if call['name'] == exp or call['name'].endswith('__' + exp):
                    return ('match', f'used MCP tool {exp}')
    if actual:
        return ('partial', f'used tools {[c["name"] for c in actual]} but none matched expected')
    return ('none', 'no tools used')


def score_text(text, must_contain, must_not_contain):
    text_lower = text.lower()
    matched = sum(1 for s in must_contain if s.lower() in text_lower)
    violations = [s for s in must_not_contain if s.lower() in text_lower]
    return matched, len(must_contain), violations


def analyze_run(run_dir, corpus):
    rows = []
    for p in corpus['prompts']:
        pid = p['id']
        cli = load_cli(run_dir / f'{pid}.cli.json')
        session = load_session(run_dir / f'{pid}.session.jsonl')

        text = extract_response_text(cli)
        tool_calls = extract_tool_calls(session)
        tool_status, tool_detail = score_tool(p.get('expects_tool', []), tool_calls)
        tc_match, tc_total, tc_violations = score_text(text, p.get('must_contain', []), p.get('must_not_contain', []))

        meta = ((cli.get('result') or {}).get('meta') or {})
        agent_meta = meta.get('agentMeta', {}) or {}
        usage = agent_meta.get('usage', {}) or {}

        preview_lc = text[:200].lower()
        agent_aborted = (
            "agent couldn't generate a response" in preview_lc
            or 'cli error' in preview_lc
            or '_error' in (cli or {})
        )
        preamble_only = bool(text.strip()) and (usage.get('output', 0) or 0) < 100 and any(
            p in text[:200] for p in ['让我', '我需要先', '让我去', "I'll check", 'let me', '我来查', '正在查询']
        )

        rows.append({
            'id': pid,
            'category': p.get('category'),
            'tool_status': tool_status,
            'tool_detail': tool_detail,
            'tool_calls_made': [c['name'] for c in tool_calls],
            'mcp_calls': sum(1 for c in tool_calls if 'purrfect' in c['name'] or '__' in c['name']),
            'text_match_n': tc_match,
            'text_match_total': tc_total,
            'text_violations': tc_violations,
            'preview': text[:200].replace('\n', ' '),
            'duration_ms': meta.get('durationMs'),
            'model': agent_meta.get('model'),
            'input_tokens': usage.get('input'),
            'output_tokens': usage.get('output'),
            'aborted': agent_aborted,
            'preamble_only': preamble_only,
        })
    return rows


def verdict(r):
    if r['aborted']:
        return '❌ FAIL (abort)'
    if r['preamble_only']:
        return '❌ FAIL (preamble)'
    if r['text_violations']:
        return '❌ FAIL (violation)'
    text_full = r['text_match_total'] == 0 or r['text_match_n'] == r['text_match_total']
    if text_full and r['tool_status'] == 'match':
        return '✅ PASS'
    if text_full and r['tool_status'] in ('partial', 'match'):
        return '✅ PASS (fallback)'
    if r['text_match_n'] > 0 or r['tool_status'] != 'none':
        return '🟡 PARTIAL'
    return '❌ FAIL'


def aggregate(rows):
    durs = [r['duration_ms'] for r in rows if r.get('duration_ms')]
    ins = [r['input_tokens'] for r in rows if r.get('input_tokens')]
    outs = [r['output_tokens'] for r in rows if r.get('output_tokens')]
    return {
        'n': len(rows),
        'pass': sum(1 for r in rows if 'PASS' in verdict(r)),
        'partial': sum(1 for r in rows if 'PARTIAL' in verdict(r)),
        'fail': sum(1 for r in rows if 'FAIL' in verdict(r)),
        'avg_dur_s': round(statistics.mean(durs) / 1000, 1) if durs else 0,
        'med_dur_s': round(statistics.median(durs) / 1000, 1) if durs else 0,
        'avg_in_tok': int(statistics.mean(ins)) if ins else 0,
        'total_in_tok': sum(ins),
        'total_out_tok': sum(outs),
        'mcp_call_rate': round(sum(r['mcp_calls'] for r in rows) / max(1, len(rows)), 1),
    }


def print_run(rows, run_dir, corpus_path):
    print('=' * 100)
    print(f'EVAL REPORT — corpus={corpus_path}  run={run_dir}')
    print('=' * 100)
    for r in rows:
        v = verdict(r)
        print(f"\n[{v}] {r['id']} ({r['category']})")
        print(f"  tool_status: {r['tool_status']:9}  | calls: {r['tool_calls_made']}")
        print(f"  text:        {r['text_match_n']}/{r['text_match_total']} hits  | violations: {r['text_violations'] or 'none'}")
        print(f"  perf:        {r['duration_ms']}ms  in={r['input_tokens']}  out={r['output_tokens']}  model={r['model']}")
        print(f"  preview:     {r['preview'][:160]}")
    agg = aggregate(rows)
    print()
    print('=' * 100)
    print(f"TOTAL: {agg['pass']} pass, {agg['partial']} partial, {agg['fail']} fail (of {agg['n']})")
    print(f"PERF:  avg_dur={agg['avg_dur_s']}s  med_dur={agg['med_dur_s']}s  avg_in={agg['avg_in_tok']}  total_in={agg['total_in_tok']}  mcp_calls/prompt={agg['mcp_call_rate']}")
    print('=' * 100)
    return agg


def diff_runs(rows_a, rows_b, name_a='A', name_b='B'):
    by_id_a = {r['id']: r for r in rows_a}
    by_id_b = {r['id']: r for r in rows_b}
    print()
    print('=' * 100)
    print(f"PER-PROMPT DIFF: {name_a} -> {name_b}")
    print('=' * 100)
    print(f"{'PROMPT':35} {name_a:25} {name_b:25}  Δ")
    print('-' * 100)
    for pid in by_id_a:
        va = verdict(by_id_a[pid])[:23]
        vb = verdict(by_id_b.get(pid, {}))[:23]
        delta = '✅+' if 'PASS' in vb and 'PASS' not in va else ('❌-' if 'FAIL' in vb and 'FAIL' not in va else '   ')
        print(f"{pid:35} {va:25} {vb:25}  {delta}")
    agg_a = aggregate(rows_a)
    agg_b = aggregate(rows_b)
    print()
    print(f"{'metric':14} {name_a:>10} {name_b:>10}  Δ")
    for k in ('pass', 'partial', 'fail', 'avg_dur_s', 'avg_in_tok', 'total_in_tok', 'mcp_call_rate'):
        d = agg_b[k] - agg_a[k]
        pct = 100 * d / agg_a[k] if agg_a[k] else 0
        print(f"{k:14} {agg_a[k]:>10} {agg_b[k]:>10}  {d:+}  ({pct:+.0f}%)")


def main():
    if len(sys.argv) < 2:
        print('usage: EVAL_CORPUS=corpus.json eval-analyze.py <run_dir> [<run_dir_b>]')
        sys.exit(2)
    corpus, corpus_path = load_corpus()
    run_a = Path(sys.argv[1])
    rows_a = analyze_run(run_a, corpus)
    print_run(rows_a, run_a, corpus_path)
    if len(sys.argv) >= 3:
        run_b = Path(sys.argv[2])
        rows_b = analyze_run(run_b, corpus)
        print_run(rows_b, run_b, corpus_path)
        diff_runs(rows_a, rows_b, name_a=run_a.name, name_b=run_b.name)


if __name__ == '__main__':
    main()
