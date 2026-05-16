#!/usr/bin/env python3
"""Pretty-print a single openclaw session's tool-call trace.

Usage:
    python3 inspect-session.py <session.jsonl>

Shows assistant↔tool exchanges in order. Useful for diagnosing why a specific
prompt failed — read the actual sequence of toolCall + toolResult to see if
the agent picked the right tool, what input it sent, what came back.
"""
import json
import sys


def emit(role_label, body):
    print(f'\n[{role_label}]')
    print(body)


def main():
    if len(sys.argv) != 2:
        print('usage: inspect-session.py <session.jsonl>', file=sys.stderr)
        sys.exit(2)
    path = sys.argv[1]
    n_user = n_assistant = n_tool_call = n_tool_result = 0
    for ln in open(path):
        ln = ln.strip()
        if not ln:
            continue
        try:
            o = json.loads(ln)
        except Exception:
            continue
        if o.get('type') != 'message':
            continue
        msg = o.get('message', {})
        role = msg.get('role', '?')
        content = msg.get('content')

        if role == 'user' and isinstance(content, list):
            for c in content:
                if c.get('type') == 'text':
                    emit('user', c.get('text', '')[:600])
                    n_user += 1

        elif role == 'assistant' and isinstance(content, list):
            for c in content:
                t = c.get('type')
                if t == 'thinking':
                    emit('assistant·thinking', c.get('thinking', '')[:600])
                elif t == 'text':
                    emit('assistant·text', c.get('text', '')[:600])
                    n_assistant += 1
                elif t == 'toolCall':
                    name = c.get('name', '?')
                    inp = json.dumps(c.get('input'), ensure_ascii=False) if c.get('input') else '{}'
                    is_mcp = 'purrfect' in name or '__' in name
                    mark = '⭐ MCP' if is_mcp else 'shell'
                    emit(f'tool·call ({mark})', f'{name}  {inp[:400]}')
                    n_tool_call += 1

        elif role == 'toolResult' and isinstance(content, list):
            for c in content:
                if c.get('type') == 'text':
                    txt = c.get('text', '')
                    emit('tool·result', f'({len(txt)}c) {txt[:400]}')
                    n_tool_result += 1

    print()
    print('=' * 80)
    print(f'turns: user={n_user}  assistant_text={n_assistant}  tool_calls={n_tool_call}  tool_results={n_tool_result}')


if __name__ == '__main__':
    main()
