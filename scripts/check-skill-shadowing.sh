#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$ROOT_DIR"

errors=0

if [[ -d ows/interactions ]]; then
	while IFS= read -r document; do
		echo "ERROR: OWS support document is outside a recognized support path: ${document#./}" >&2
		errors=1
	done < <(find ows/interactions -type f -name '*.md' -print | LC_ALL=C sort)
fi

top_level_skills=()
while IFS= read -r skill_file; do
	top_level_skills+=("${skill_file#./}")
done < <(
	find . -mindepth 2 -maxdepth 2 -type f -name SKILL.md -print \
		| sed 's#/SKILL.md$##' \
		| LC_ALL=C sort
)

for skill in "${top_level_skills[@]}"; do
	while IFS= read -r candidate; do
		echo "ERROR: ${candidate#./} shadows top-level skill $skill/SKILL.md" >&2
		errors=1
	done < <(
		find . -type f -name "$skill.md" \
			-not -path './.git/*' \
			-not -path '*/references/*' \
			-not -path '*/templates/*' \
			-not -path '*/assets/*' \
			-not -path '*/scripts/*' \
			-print \
			| LC_ALL=C sort
	)
done

if [[ -d ows/references/interactions ]]; then
	while IFS= read -r document; do
		relative_path="${document#ows/}"
		if ! grep -Fq "]($relative_path)" ows/SKILL.md; then
			echo "ERROR: $document is not linked from ows/SKILL.md" >&2
			errors=1
		fi
	done < <(find ows/references/interactions -maxdepth 1 -type f -name '*.md' -print | LC_ALL=C sort)
fi

if [[ "$errors" -ne 0 ]]; then
	echo "Skill shadowing check failed." >&2
	exit 1
fi

echo "Skill shadowing check passed (${#top_level_skills[@]} top-level skills)."
