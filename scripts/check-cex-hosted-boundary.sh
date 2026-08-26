#!/usr/bin/env bash
# Fail closed on the hosted OKX/Bitget CEX skill boundary.
#
# This would fail the 017cd481 layout:
# - okx-cex/SKILL.md sent every command through vendor/_shared/preflight.md
#   (which runs `okx upgrade`) and routed install intent to okx-cex-skill-mp
# Bitget ships the official body directly with only a provider-qualified
# frontmatter description; it must not claim unnamed exchange requests.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$ROOT_DIR"

errors=0

fail() {
	echo "ERROR: $*" >&2
	errors=1
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

	auth="$(section "$okx_router" '## Hosted authentication (authoritative)')"
	for env_var in OKX_API_KEY OKX_SECRET_KEY OKX_PASSPHRASE; do
		if ! grep -Fq "$env_var" <<<"$auth"; then
			fail "$okx_router hosted authentication is missing $env_var"
		fi
	done
	if ! grep -Fq 'even when' <<<"$auth" || ! grep -Fq 'okx config show --json' <<<"$auth"; then
		fail "$okx_router must make complete hosted credentials authoritative over empty CLI profiles"
	fi
	for forbidden in 'okx config init' 'okx auth status' 'okx auth login' '--profile'; do
		if ! grep -Fq -- "$forbidden" <<<"$auth"; then
			fail "$okx_router must define the hosted API-key boundary for $forbidden"
		fi
	done
	if ! grep -Eiq 'printing|echoing|logging|exposing' <<<"$auth"; then
		fail "$okx_router must forbid exposing hosted credential values"
	fi
	if ! grep -Eiq 'only some|partial' <<<"$auth" || ! grep -Fq 'Pieverse Agent page' <<<"$auth"; then
		fail "$okx_router must stop on partial credentials and direct users to the Agent page"
	fi
fi

# --- Bitget official direct package -----------------------------------------

bitget_skill="bitget/SKILL.md"
[[ -f "$bitget_skill" ]] || fail "missing official $bitget_skill"

if [[ -d "bitget/vendor" ]]; then
	fail "Bitget official files must live directly under bitget/, not bitget/vendor/"
fi

if [[ -f "$bitget_skill" ]]; then
	bitget_frontmatter="$(awk 'BEGIN { p = 0 } /^---[[:space:]]*$/ { p++; next } p == 1 { print } p >= 2 { exit }' "$bitget_skill")"
	for phrase in "Use when the user asks" "Bitget Exchange" "bgc CLI"; do
		if ! grep -Fqi -- "$phrase" <<<"$bitget_frontmatter"; then
			fail "$bitget_skill frontmatter is missing provider-qualified trigger: $phrase"
		fi
	done
	for phrase in "even when the user doesn't say" "even without the exchange name" "Always invoke this skill before attempting any exchange"; do
		if grep -Fqi -- "$phrase" <<<"$bitget_frontmatter"; then
			fail "$bitget_skill frontmatter claims unnamed exchange requests: $phrase"
		fi
	done
fi

if [[ "$errors" -ne 0 ]]; then
	echo "CEX hosted-boundary check failed." >&2
	exit 1
fi

echo "CEX hosted-boundary check passed."
