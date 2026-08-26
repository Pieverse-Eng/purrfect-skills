#!/usr/bin/env bash
# Fail closed when the OKX CEX router exposes runtime installation or upgrades.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$ROOT_DIR"

router="okx-cex/SKILL.md"
marketplace="vendor/okx-cex-skill-mp/SKILL.md"

fail() {
	printf 'ERROR: %s\n' "$*" >&2
	exit 1
}

[[ -f "$router" ]] || fail "missing $router"

grep -Fq 'Do not install or upgrade packages or skills at runtime' "$router" ||
	fail "$router must forbid runtime package and skill installation"
grep -Fq 'Never run `okx upgrade`' "$router" ||
	fail "$router must forbid okx CLI upgrades"
grep -Fq '`okx skill add --force`' "$router" ||
	fail "$router must forbid marketplace signature bypass"

operational_references="$({
	awk '
		$0 == "## References" { active = 1; next }
		active && /^## / { exit }
		active { print }
	' "$router"
})"

if grep -Fq "$marketplace" <<<"$operational_references"; then
	fail "$marketplace must not be an operational reference"
fi

reference_only="$({
	awk '
		$0 == "## Reference only" { active = 1; next }
		active && /^## / { exit }
		active { print }
	' "$router"
})"
grep -Fq "$marketplace" <<<"$reference_only" ||
	fail "$marketplace must be marked reference-only"

while IFS= read -r runtime_file; do
	case "$runtime_file" in
		*/okx-cex-skill-mp/SKILL.md) continue ;;
	esac

	if grep -Eq 'okx[[:space:]]+upgrade|okx[[:space:]]+skill[[:space:]]+(add|download)|npm[[:space:]]+install|brew[[:space:]]+install|apt(-get)?[[:space:]]+install' "$runtime_file"; then
		fail "$runtime_file contains a runtime install or upgrade command"
	fi
done < <(find okx-cex/vendor -type f \( -name '*.md' -o -name '*.sh' \) -print)

printf 'CEX runtime-boundary check passed.\n'
