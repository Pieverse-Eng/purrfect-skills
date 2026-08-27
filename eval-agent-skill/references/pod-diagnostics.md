# Phase 1 diagnostics — is the skill actually loaded?

The single most common eval blocker on the OpenClaw / Hermes platform: skill files are deployed in the container image but **not wired into the running agent**. Symptom: agent answers "I don't have a store" / fails to call `purrfect_*` tools / falls back to shell commands.

Run these checks in order. Each box that fails IS your first finding.

## Setup

```bash
export USE_GKE_GCLOUD_AUTH_PLUGIN=True
export PATH="/opt/homebrew/share/google-cloud-sdk/bin:$PATH"
INSTANCE_ID=<UUID>
POD=tenant-$INSTANCE_ID
NS=openclaw-system
```

## ☐ 1. Pod is Running and Ready

```bash
kubectl get pod $POD -n $NS
```

`READY 1/1, STATUS Running`. If `0/1` or `Pending` or `ContainerCreating`, the gateway hasn't booted yet — wait. If `CrashLoopBackOff`, check `kubectl describe pod $POD -n $NS | tail -30` for the failure reason.

## ☐ 2. Skill files are installed in the workspace

OpenClaw layout: `/root/.openclaw/workspace/skills/<slug>/`
Hermes layout: `/opt/data/skills/<slug>/`

```bash
kubectl exec $POD -n $NS -- ls -la /root/.openclaw/workspace/skills/<slug>/SKILL.md
```

If the file is missing, the boot path didn't install the skill. For the merchant skill, this means `start-openclaw.sh`'s `MERCHANT_USE_UPSTREAM_SKILL=true` branch didn't run — verify the merchant.env in ConfigMap actually has `MERCHANT_USE_UPSTREAM_SKILL=true`:

```bash
kubectl get configmap tenant-$INSTANCE_ID-config -n $NS -o jsonpath='{.data.merchant\.env}'
```

## ☐ 3. MCP server is registered in openclaw.json

```bash
kubectl exec $POD -n $NS -- python3 -c "
import json
d = json.load(open('/root/.openclaw/openclaw.json'))
print('mcp servers:', list((d.get('mcp') or {}).get('servers', {}).keys()))
"
```

The skill's MCP slug must appear in the list. If missing, either:
- Platform's `buildFullConfig` doesn't emit it for this skill (need a config-builder.ts change + allowlist in `merge-platform-config.py`), OR
- It WAS emitted but `merge-platform-config.py` stripped it on boot because the slug wasn't in `PLATFORM_MANAGED_MCP_SERVERS`.

For the merchant skill specifically, both are needed and live in the platform — see `docs/plans/2026-05-03-merchant-skill-eval-fix-proposal.md` in the platform repo.

## ☐ 4. MCP child process is running

```bash
kubectl exec $POD -n $NS -- sh -c 'ps aux | grep -E "mcp\.js|<slug>" | grep -v grep'
```

The gateway spawns MCP children on boot (eager) or first use (lazy, varies by skill). If the entry is in `mcp.servers` but no child is running, the gateway probably tried and the child crashed. Check the gateway log:

```bash
kubectl exec $POD -n $NS -- sh -c "tail -200 /tmp/openclaw/gateway.log | grep -oE '\"message\":\"[^\"]{1,200}\"' | grep -i 'bundle-mcp\|<slug>' | tail -20"
```

Common crash: `TypeError: Cannot open database because the directory does not exist` — the skill resolved a relative path against `process.cwd()` (= `/`) and didn't find its data dir. **Fix on the skill side** with `import.meta.url`-based path resolution. **Workaround in platform** with an absolute env var (e.g. `MERCHANT_DB`) in the openclaw.json mcp.servers entry.

## ☐ 5. Agent identity reflects the skill's role

```bash
kubectl exec $POD -n $NS -- head -20 /root/.openclaw/workspace/IDENTITY.md
```

If the file shows the empty template (`# IDENTITY.md - Who Am I? — Fill this in...`), the agent boots as a generic Pieverse assistant and will not recognize itself as the skill's role. For the merchant skill, this leads to "I don't have a store" responses.

Fix: the platform should overlay `IDENTITY.md` with role-specific framing when the skill is enabled. For the merchant skill see `buildMerchantIdentityFile` in `packages/api-server/src/services/config-builder.ts`. The framing matters — over-aggressive identity ("I AM the shopkeeper") regresses off-skill prompts; the recommended shape is "merchant helper hat" (the user is the merchant; the agent is the helper; the hat is dormant for non-merchant prompts).

## ☐ 6. Smoke test through the agent

```bash
SID=$(python3 -c "import uuid; print(uuid.uuid4())")
kubectl exec $POD -n $NS -- sh -c "
  timeout 90 openclaw agent --session-id '$SID' --message '<role-specific question>' --json
" > /tmp/smoke.json

kubectl cp $NS/$POD:/root/.openclaw/agents/main/sessions/$SID.jsonl /tmp/smoke.jsonl
python3 ~/.claude/skills/eval-agent-skill/scripts/inspect-session.py /tmp/smoke.jsonl
```

For the merchant skill, a good first-question is `我们店里有哪些产品？`. Expected: agent calls `purrfect_product_list` once (or its `__`-prefixed variant) and returns the products with prices. If `inspect-session.py` shows no purrfect_* tool calls but a confident-sounding answer, the agent is fabricating — that's a signal something in 2–4 above is broken.

## ☐ 7. Merchant data is seeded (only relevant for content-correctness eval)

If the eval is going to check `must_contain` substrings against the agent's answer, the underlying data must exist. For the merchant skill:

```bash
kubectl exec $POD -n $NS -- sh -c '
  cd /root/.openclaw/workspace/skills/purrfect-merchant-skill
  node src/index.js product list --json | head -3
  node -e "
    import(\"better-sqlite3\").then(({default:Db})=>{
      const db = new Db(\"data/merchant.db\");
      console.log(\"customers:\", db.prepare(\"SELECT COUNT(*) as n FROM customers\").get().n);
      console.log(\"orders:\", db.prepare(\"SELECT COUNT(*) as n FROM orders\").get().n);
      console.log(\"failed_settle:\", db.prepare(\"SELECT COUNT(*) as n FROM failed_settlements\").get().n);
    })
  "
'
```

If counts are 0, run the seed script (`scripts/seed-merchant.mjs`) before the eval.
