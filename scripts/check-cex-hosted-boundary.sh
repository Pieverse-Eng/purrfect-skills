#!/usr/bin/env bash
# Fail closed on the hosted OKX/Bitget CEX skill boundary.
#
# This would fail the 017cd481 layout:
# - okx-cex/SKILL.md sent every command through vendor/_shared/preflight.md
#   (which runs `okx upgrade`) and routed install intent to okx-cex-skill-mp
# - bitget/SKILL.md was the official file and claimed provider-agnostic
#   exchange intents
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$ROOT_DIR"

errors=0

fail() {
	echo "ERROR: $*" >&2
	errors=1
}

frontmatter() {
	awk 'BEGIN { p = 0 } /^---[[:space:]]*$/ { p++; next } p == 1 { print } p >= 2 { exit }' "$1"
}

section() {
	local file="$1"
	local heading="$2"
	awk -v heading="$heading" '
		BEGIN { p = 0 }
		$0 == heading { p = 1; next }
		p && /^## / { exit }
		p { print }
	' "$file"
}

# --- OKX hosted pin / official-only -----------------------------------------

okx_router="okx-cex/SKILL.md"
[[ -f "$okx_router" ]] || fail "missing $okx_router"

if [[ -f "$okx_router" ]]; then
	if ! grep -Fq 'Do not install packages at runtime' "$okx_router"; then
		fail "$okx_router must forbid runtime package installs"
	fi

	if ! grep -Eiq 'never run `okx upgrade`|do not run `okx upgrade`|never run okx upgrade|do not run okx upgrade' "$okx_router"; then
		fail "$okx_router must explicitly forbid \`okx upgrade\`"
	fi

	if grep -Fq 'Shared credential checks live in' "$okx_router"; then
		fail "$okx_router must not send hosted commands through official preflight"
	fi

	routing="$(section "$okx_router" '## Routing')"
	if awk -F'|' '
		/^\|/ && $0 !~ /^\|[[:space:]]*-+/ {
			dest = $(NF > 1 ? NF - 1 : NF)
			if (dest ~ /preflight\.md/ || dest ~ /okx-cex-skill-mp/) found = 1
		}
		END { exit found ? 0 : 1 }
	' <<<"$routing"; then
		fail "$okx_router Routing table must not route to preflight.md or okx-cex-skill-mp"
	fi
	for required_route in okx-cex-auth okx-cex-market okx-cex-trade okx-cex-portfolio; do
		if ! grep -Fq "$required_route" <<<"$routing"; then
			fail "$okx_router Routing table is missing $required_route"
		fi
	done

	if ! grep -Eiq 'reference-only|reference only|upstream reference' "$okx_router"; then
		fail "$okx_router must mark marketplace/preflight as reference-only"
	fi
fi

# --- Bitget qualified triggers ----------------------------------------------

bitget_router="bitget/SKILL.md"
bitget_official="bitget/vendor/bitget/SKILL.md"
[[ -f "$bitget_router" ]] || fail "missing $bitget_router"
[[ -f "$bitget_official" ]] || fail "missing official $bitget_official"

if [[ -f "$bitget_router" && -f "$bitget_official" ]]; then
	if cmp -s "$bitget_router" "$bitget_official"; then
		fail "bitget/SKILL.md must be a platform router, not the official file"
	fi

	if ! grep -Fq 'Do not install packages at runtime' "$bitget_router"; then
		fail "$bitget_router must forbid runtime package installs"
	fi

	fm="$(frontmatter "$bitget_router")"
	if [[ -z "$fm" ]]; then
		fail "$bitget_router is missing YAML frontmatter"
	fi

	# Provider-agnostic phrases from the official Bitget frontmatter.
	while IFS= read -r phrase; do
		[[ -n "$phrase" ]] || continue
		if grep -Fqi -- "$phrase" <<<"$fm"; then
			fail "$bitget_router frontmatter claims provider-agnostic intent: $phrase"
		fi
	done <<'PHRASES'
check my open orders
place a market sell
BTC现在多少钱
even when the user doesn't say
even without the exchange name
Always invoke this skill before attempting any exchange
these are Bitget operations even without the exchange name
查看我的账户
下一个限价单
PHRASES

	if ! grep -Eiq 'bitget' <<<"$fm"; then
		fail "$bitget_router frontmatter must be Bitget-qualified"
	fi

	# Official file stays byte-for-byte, including the aggressive triggers.
	for phrase in "check my open orders" "place a market sell" "BTC现在多少钱" "even when the user doesn't say"; do
		if ! grep -Fqi -- "$phrase" "$bitget_official"; then
			fail "$bitget_official no longer contains official trigger phrase: $phrase"
		fi
	done
fi

if [[ "$errors" -ne 0 ]]; then
	echo "CEX hosted-boundary check failed." >&2
	exit 1
fi

echo "CEX hosted-boundary check passed."
