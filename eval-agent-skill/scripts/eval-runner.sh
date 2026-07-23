#!/bin/bash
# Run an eval corpus against a tenant pod's openclaw agent.
#
# Usage: eval-runner.sh <output_dir> [model_id]
#
# Required env (or pass via env file):
#   EVAL_INSTANCE_ID   tenant instance UUID (e.g. e9c2ebdf-18a6-...)
#   EVAL_NAMESPACE     k8s namespace (default openclaw-system)
#   EVAL_CORPUS        absolute path to corpus.json (see references/eval-corpus-schema.md)
#
# Optional env:
#   EVAL_TIMEOUT_S     per-prompt timeout in seconds (default 240)
#   EVAL_GCLOUD_PATH   path prefix for gcloud SDK bin (default /opt/homebrew/share/google-cloud-sdk/bin)
#
# Each prompt gets a fresh UUID session-id (so context doesn't leak between
# prompts). For each prompt we save:
#   <out_dir>/<prompt_id>.cli.json       — full openclaw agent --json output
#   <out_dir>/<prompt_id>.session.jsonl  — gateway session log (toolCalls etc.)
#   <out_dir>/<prompt_id>.session-id     — the UUID (for re-querying the pod)

set -u

OUT_DIR="${1:?need output dir}"
MODEL="${2:-}"

INSTANCE_ID="${EVAL_INSTANCE_ID:?set EVAL_INSTANCE_ID env var to the tenant instance UUID}"
NS="${EVAL_NAMESPACE:-openclaw-system}"
CORPUS="${EVAL_CORPUS:?set EVAL_CORPUS env var to corpus.json path}"
TIMEOUT_S="${EVAL_TIMEOUT_S:-240}"
GCLOUD_BIN="${EVAL_GCLOUD_PATH:-/opt/homebrew/share/google-cloud-sdk/bin}"

POD="tenant-$INSTANCE_ID"

mkdir -p "$OUT_DIR"

# Auth setup for kubectl/gcloud (skip if already configured)
export USE_GKE_GCLOUD_AUTH_PLUGIN=True
case ":$PATH:" in
  *":$GCLOUD_BIN:"*) : ;;
  *) export PATH="$GCLOUD_BIN:$PATH" ;;
esac

# Verify pod is reachable
if ! kubectl get pod "$POD" -n "$NS" >/dev/null 2>&1; then
  echo "[runner] FATAL: pod $POD not found in namespace $NS" >&2
  exit 1
fi

# Push corpus to pod (idempotent)
kubectl cp "$CORPUS" "$NS/$POD:/tmp/eval-corpus.json" >/dev/null

# Iterate
N=$(python3 -c "import json; print(len(json.load(open('$CORPUS'))['prompts']))")
echo "[runner] corpus=$CORPUS  prompts=$N  out=$OUT_DIR  model_override=${MODEL:-default}"

for i in $(seq 0 $((N-1))); do
  PROMPT_ID=$(python3 -c "import json; print(json.load(open('$CORPUS'))['prompts'][$i]['id'])")
  PROMPT_TEXT=$(python3 -c "import json; print(json.load(open('$CORPUS'))['prompts'][$i]['prompt'])")
  SESSION_ID=$(python3 -c "import uuid; print(uuid.uuid4())")

  echo "[runner] [$((i+1))/$N] $PROMPT_ID  (session=${SESSION_ID:0:8}...)"

  MODEL_ARG=""
  if [ -n "$MODEL" ]; then MODEL_ARG="--model $MODEL"; fi

  # The shell quoting here matters: we want PROMPT_TEXT to land inside the
  # pod's outer single-quoted shell verbatim, including any single quotes
  # in the prompt. Bash escape via "'\''" is required.
  ESCAPED_PROMPT=$(printf '%s' "$PROMPT_TEXT" | sed "s/'/'\\\\''/g")

  kubectl exec "$POD" -n "$NS" -- sh -c "
    timeout $TIMEOUT_S openclaw agent --session-id '$SESSION_ID' --message '$ESCAPED_PROMPT' $MODEL_ARG --json > /tmp/eval-run.json 2>/dev/null
    cp /tmp/eval-run.json /tmp/eval-run-$PROMPT_ID.json
    echo SESSION_FILE=/root/.openclaw/agents/main/sessions/$SESSION_ID.jsonl
  " 2>/dev/null

  # Pull stdout JSON + session JSONL out of pod
  kubectl cp "$NS/$POD:/tmp/eval-run-$PROMPT_ID.json" "$OUT_DIR/$PROMPT_ID.cli.json" 2>/dev/null
  kubectl cp "$NS/$POD:/root/.openclaw/agents/main/sessions/$SESSION_ID.jsonl" "$OUT_DIR/$PROMPT_ID.session.jsonl" 2>/dev/null

  echo "$SESSION_ID" > "$OUT_DIR/$PROMPT_ID.session-id"
done

echo "[runner] done — analyze with: python3 \$(dirname \$0)/eval-analyze.py $OUT_DIR"
