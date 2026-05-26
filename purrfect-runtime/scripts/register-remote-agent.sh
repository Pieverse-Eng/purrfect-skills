#!/usr/bin/env bash
set -euo pipefail

API_BASE="${PURRFECT_API_BASE:-https://purr.pieverse.io}"
AGENT_NAME="${1:-${AGENT_NAME:-}}"
MAX_ATTEMPTS="${MAX_ATTEMPTS:-6}"

if [ -z "$AGENT_NAME" ] || [ "$AGENT_NAME" = "YOUR_AGENT_NAME" ]; then
	echo "Set AGENT_NAME or pass the agent name as the first argument." >&2
	exit 1
fi

normalize_handle() {
	node - "$1" <<'NODE'
const input = (process.argv[2] || 'remote-agent').trim().toLowerCase().replace(/\.pie$/u, '')
const chars = []
let previousHyphen = false
for (const char of input) {
  const code = char.charCodeAt(0)
  const out = (code >= 97 && code <= 122) || (code >= 48 && code <= 57) ? char : '-'
  if (out === '-') {
    if (chars.length === 0 || previousHyphen) continue
    previousHyphen = true
  } else {
    previousHyphen = false
  }
  chars.push(out)
  if (chars.length >= 30) break
}
while (chars[chars.length - 1] === '-') chars.pop()
let handle = chars.join('')
if (handle.length < 5) handle = `agent-${handle || 'remote'}`
console.log(handle.slice(0, 30).replace(/-+$/u, ''))
NODE
}

json_code() {
	BODY="$1" node <<'NODE'
try {
  const body = JSON.parse(process.env.BODY || '{}')
  console.log(body.code || body.error || '')
} catch {
  console.log('')
}
NODE
}

validate_success() {
	BODY="$1" node <<'NODE'
const body = JSON.parse(process.env.BODY || '{}')
const d = body.data || {}
if (!d.agentId || !d.apiKey || !d.wallet || !d.handle || !d.renderedHandle) {
  console.error('registration response missing required identity fields')
  process.exit(1)
}
NODE
}

attempt=1
while [ "$attempt" -le "$MAX_ATTEMPTS" ]; do
	suffix=""
	if [ "$attempt" -gt 1 ]; then
		suffix="-$(openssl rand -hex 3 2>/dev/null || date +%s)"
	fi
	name="${AGENT_NAME}${suffix}"
	handle="$(normalize_handle "$name")"
	payload="$(node - "$name" "$handle" <<'NODE'
console.log(JSON.stringify({
  name: process.argv[2],
  handle: process.argv[3],
  chainType: 'ethereum'
}))
NODE
)"

	tmp="$(mktemp)"
	status="$(curl -sS -o "$tmp" -w "%{http_code}" -X POST "${API_BASE}/v1/agents/register" \
		-H "Content-Type: application/json" \
		-d "$payload")"
	body="$(cat "$tmp")"
	rm -f "$tmp"

	if [ "$status" = "200" ]; then
		validate_success "$body"
		printf '%s\n' "$body"
		exit 0
	fi

	case "$(json_code "$body")" in
		AGENT_NAME_TAKEN | HANDLE_TAKEN | HANDLE_RESERVED | HANDLE_RESERVATION_EXPIRED | handle_already_taken | handle_reserved | invalid_handle)
			attempt=$((attempt + 1))
			continue
			;;
		HANDLE_CLAIM_RETRYABLE)
			sleep "$attempt"
			attempt=$((attempt + 1))
			continue
			;;
		*)
			printf '%s\n' "$body" >&2
			exit 1
			;;
	esac
done

echo "registration failed after retries" >&2
exit 1
