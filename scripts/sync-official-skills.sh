#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
REGISTRY_PATH="$ROOT_DIR/vendor-skills-registry.json"

MODE="apply"
PROVIDER_FILTER=""

usage() {
	cat <<'EOF'
Usage:
  scripts/sync-official-skills.sh [--provider <id>] [--apply|--check]

Options:
  --provider <id>  Sync only one provider from registry
  --apply          Copy upstream files into target paths (default)
  --check          Verify target files match upstream pinned commit (no writes)
EOF
}

while [[ $# -gt 0 ]]; do
	case "$1" in
		--provider)
			[[ $# -ge 2 ]] || { echo "ERROR: --provider requires a value" >&2; exit 1; }
			PROVIDER_FILTER="$2"
			shift 2
			;;
		--apply)
			MODE="apply"
			shift
			;;
		--check)
			MODE="check"
			shift
			;;
		-h|--help)
			usage
			exit 0
			;;
		*)
			echo "ERROR: unknown argument: $1" >&2
			usage
			exit 1
			;;
	esac
done

for cmd in git jq mktemp cmp; do
	command -v "$cmd" >/dev/null 2>&1 || {
		echo "ERROR: missing required command: $cmd" >&2
		exit 1
	}
done

[[ -f "$REGISTRY_PATH" ]] || {
	echo "ERROR: registry not found: $REGISTRY_PATH" >&2
	exit 1
}

if [[ -n "$PROVIDER_FILTER" ]]; then
	PROVIDERS_JSON="$(jq -c --arg id "$PROVIDER_FILTER" '.providers[] | select(.id == $id)' "$REGISTRY_PATH")"
else
	PROVIDERS_JSON="$(jq -c '.providers[]' "$REGISTRY_PATH")"
fi

[[ -n "$PROVIDERS_JSON" ]] || {
	echo "ERROR: no providers matched registry filter" >&2
	exit 1
}

TMP_ROOT="$(mktemp -d)"
trap 'rm -rf "$TMP_ROOT"' EXIT

drift_found=0
provider_count=0
file_count=0

while IFS= read -r provider; do
	[[ -n "$provider" ]] || continue
	provider_count=$((provider_count + 1))

	id="$(jq -r '.id' <<<"$provider")"
	repo="$(jq -r '.repo' <<<"$provider")"
	commit="$(jq -r '.commit' <<<"$provider")"

	echo "==> provider: $id"
	echo "    repo: $repo"
	echo "    commit: $commit"

	provider_tmp="$TMP_ROOT/$id"
	git clone --quiet --depth=1 "$repo" "$provider_tmp"
	if [[ "$commit" != "null" && -n "$commit" ]]; then
		git -C "$provider_tmp" fetch --quiet --depth=1 origin "$commit"
		git -C "$provider_tmp" checkout --quiet "$commit"
	fi

	while IFS= read -r skill; do
		[[ -n "$skill" ]] || continue
		name="$(jq -r '.name' <<<"$skill")"
		upstream_path="$(jq -r '.upstreamPath' <<<"$skill")"
		target_path="$(jq -r '.targetPath' <<<"$skill")"

		src="$provider_tmp/$upstream_path"
		dst="$ROOT_DIR/$target_path"
		file_count=$((file_count + 1))

		[[ -f "$src" ]] || {
			echo "ERROR: upstream file not found for $id/$name: $upstream_path" >&2
			exit 1
		}

		if [[ "$MODE" == "check" ]]; then
			if [[ ! -f "$dst" ]]; then
				echo "DRIFT: missing file $target_path"
				drift_found=1
				continue
			fi
			if ! cmp -s "$src" "$dst"; then
				echo "DRIFT: content mismatch $target_path"
				drift_found=1
			else
				echo "OK: $target_path"
			fi
		else
			mkdir -p "$(dirname "$dst")"
			cp "$src" "$dst"
			echo "SYNCED: $target_path"
		fi
	done < <(jq -c '.skills[]' <<<"$provider")
done < <(printf '%s\n' "$PROVIDERS_JSON")

if [[ "$MODE" == "check" ]]; then
	if [[ "$drift_found" -ne 0 ]]; then
		echo "CHECK FAILED: official skill drift detected"
		exit 2
	fi
	echo "CHECK OK: no drift ($provider_count provider(s), $file_count file(s))"
else
	echo "SYNC OK: copied $file_count file(s) from $provider_count provider(s)"
fi
