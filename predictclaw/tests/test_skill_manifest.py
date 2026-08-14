from __future__ import annotations

import json

from conftest import get_predict_root, parse_skill_frontmatter


def test_skill_manifest_openclaw_contract() -> None:
    skill_path = get_predict_root() / "SKILL.md"
    frontmatter, body = parse_skill_frontmatter(skill_path)

    assert frontmatter["name"] == "predictclaw"
    assert "description" in frontmatter

    openclaw = frontmatter["metadata"]["openclaw"]
    assert openclaw["emoji"]
    assert openclaw["homepage"] == "https://predict.fun"
    assert "uv" in openclaw["requires"]["bins"]
    assert "node" in openclaw["requires"]["bins"]
    assert "erc-mandated-mcp" not in openclaw["requires"]["bins"]
    assert "env" not in openclaw["requires"]

    assert "primaryEnv" not in openclaw
    assert "install" in openclaw
    install_entries = openclaw["install"]
    assert any(
        entry["kind"] == "brew" and entry["formula"] == "uv"
        for entry in install_entries
    )
    assert any(
        entry["kind"] == "brew" and entry["formula"] == "node"
        for entry in install_entries
    )
    assert all(entry.get("package") != "@erc-mandated/mcp" for entry in install_entries)

    assert "{baseDir}" in body
    assert "~/.openclaw/skills/predictclaw/" in body
    assert "only canonical user config root" in body.lower()
    assert "development-only artifact" in body.lower()
    assert "skills.entries.predictclaw.env" in body


def test_skill_manifest_uses_openclaw_single_line_metadata_json() -> None:
    skill_path = get_predict_root() / "SKILL.md"
    text = skill_path.read_text()
    frontmatter_text = text.split("---\n", 2)[1]

    metadata_lines = [
        line for line in frontmatter_text.splitlines() if line.startswith("metadata:")
    ]
    assert len(metadata_lines) == 1
    assert metadata_lines[0].startswith("metadata: {")
    assert '"openclaw"' in metadata_lines[0]


def test_default_path_has_no_mcp_binary_or_raw_private_key_requirement() -> None:
    predict_root = get_predict_root()
    skill_path = predict_root / "SKILL.md"
    frontmatter, _body = parse_skill_frontmatter(skill_path)
    openclaw = frontmatter["metadata"]["openclaw"]

    assert "erc-mandated-mcp" not in openclaw["requires"]["bins"]
    assert "node" in openclaw["requires"]["bins"]
    assert "env" not in openclaw["requires"]
    assert all(entry.get("package") != "@erc-mandated/mcp" for entry in openclaw["install"])

    helper = predict_root / "node" / "erc_mandated_sdk_helper.mjs"
    assert helper.exists()

    package_json = json.loads((predict_root / "node" / "package.json").read_text())
    assert package_json["dependencies"]["@erc-mandated/sdk"] == "0.3.1"

    template = (predict_root / "template.env").read_text()
    assert "PREDICT_WALLET_MODE=read-only" in template
    for line in template.splitlines():
        if "_PRIVATE_KEY=" in line and "=" in line:
            value = line.split("=", 1)[1].strip()
            assert value == "", f"raw private key must be empty in template.env: {line}"


def test_openclaw_install_examples_are_valid() -> None:
    skill_path = get_predict_root() / "SKILL.md"
    _frontmatter, body = parse_skill_frontmatter(skill_path)

    assert "cd {baseDir} && uv sync" in body
    assert "cp template.env .env" in body
    assert "npm install" in body
    assert "manual install" in body.lower()
    assert "read-only" in body.lower()
    assert "eoa" in body.lower()
    assert "predict-account" in body.lower()
    assert "mandated-vault" in body.lower()
    assert "wallet deposit" in body
    assert "wallet withdraw" in body
    assert "PREDICT_WALLET_MODE" in body
    assert "WALLET_API_URL" in body
    assert "WALLET_API_TOKEN" in body
    assert "INSTANCE_ID" in body
    assert "ERC_MANDATED_VAULT_ADDRESS" in body
    assert "ERC_MANDATED_FACTORY_ADDRESS" in body
    assert "ERC_MANDATED_VAULT_ASSET_ADDRESS" in body
    assert "ERC_MANDATED_VAULT_NAME" in body
    assert "ERC_MANDATED_VAULT_SYMBOL" in body
    assert "ERC_MANDATED_VAULT_AUTHORITY" in body
    assert "ERC_MANDATED_VAULT_SALT" in body
    assert "ERC_MANDATED_MCP_COMMAND" not in body
    assert "ERC_MANDATED_CONTRACT_VERSION" in body
    assert "ERC_MANDATED_CHAIN_ID" in body
    assert "manual-only" in body
    assert "vault contract policy authorizes" in body.lower()
    assert "unsupported-in-mandated-vault-v1" in body
    assert "vault-to-predict-account" in body
    assert "unsupported-predict-account-execution" in body


def test_codebase_has_no_legacy_mcp_or_raw_key_execution_surface() -> None:
    predict_root = get_predict_root()
    forbidden = {
        "_SubprocessMcpClient",
        "ERC_MANDATED_MCP_COMMAND",
        "PREDICT_EOA_PRIVATE_KEY",
        "PREDICT_PRIVY_PRIVATE_KEY",
        "ERC_MANDATED_AUTHORITY_PRIVATE_KEY",
        "ERC_MANDATED_EXECUTOR_PRIVATE_KEY",
        "ERC_MANDATED_BOOTSTRAP_PRIVATE_KEY",
    }

    for root_name in ("lib", "scripts"):
        root = predict_root / root_name
        for path in root.rglob("*.py"):
            text = path.read_text()
            for token in forbidden:
                assert token not in text, (
                    f"{path.relative_to(predict_root)} must not reference {token}"
                )


def test_readme_has_no_raw_key_or_legacy_frontmatter_claim() -> None:
    predict_root = get_predict_root()
    readme = predict_root / "README.md"
    assert readme.exists()

    text = readme.read_text()
    forbidden = (
        "PREDICT_EOA_PRIVATE_KEY",
        "PREDICT_PRIVY_PRIVATE_KEY",
        "ERC_MANDATED_AUTHORITY_PRIVATE_KEY",
        "ERC_MANDATED_EXECUTOR_PRIVATE_KEY",
        "ERC_MANDATED_BOOTSTRAP_PRIVATE_KEY",
        "_PRIVATE_KEY=",
        "executor/authority/bootstrap private keys",
    )
    for token in forbidden:
        assert token not in text, f"README.md must not reference {token}"

    assert "declares only the external runtimes" in text
    assert "conditionally used env surfaces" not in text


def test_docs_align_with_predict_account_fail_closed() -> None:
    predict_root = get_predict_root()
    skill = (predict_root / "SKILL.md").read_text()
    readme = (predict_root / "README.md").read_text()

    for path, text in (("SKILL.md", skill), ("README.md", readme)):
        assert "unsupported-predict-account-execution" in text, path
        assert "Predict Account trading" not in text, path
        assert "trading through EOA or Predict Account" not in text, path
        assert "remains the trading identity" not in text, path
        assert "funded-trading" not in text, path

    account_template = (predict_root / "template.predict-account.env").read_text()
    assert "Predict Account trading template" not in account_template
    assert "unsupported-predict-account-execution" in account_template


def test_no_stale_capability_claims_in_skill_files() -> None:
    predict_root = get_predict_root()
    forbidden = (
        "Overlay buy can proceed",
        "stays the trading identity",
        "remains the trading identity",
        "backfills the local .env",
        "backfills local .env",
    )
    excluded_dirs = {".venv", "node_modules", "__pycache__", "tests"}

    for path in sorted(predict_root.rglob("*")):
        if not path.is_file():
            continue
        if any(part in excluded_dirs for part in path.parts):
            continue
        try:
            text = path.read_text()
        except UnicodeDecodeError:
            continue
        for token in forbidden:
            assert token not in text, (
                f"{path.relative_to(predict_root)} contains stale capability claim: {token}"
            )


def test_references_configuration_has_no_raw_key_or_smoke_surface() -> None:
    predict_root = get_predict_root()
    reference = predict_root / "references" / "configuration.md"
    assert reference.exists()

    text = reference.read_text()
    assert "PREDICT_SMOKE_PRIVATE_KEY" not in text
    assert "PREDICT_SMOKE_PRIVY_PRIVATE_KEY" not in text
    assert "ERC_MANDATED_AUTHORITY_PRIVATE_KEY" not in text
    assert "ERC_MANDATED_EXECUTOR_PRIVATE_KEY" not in text
    assert "ERC_MANDATED_BOOTSTRAP_PRIVATE_KEY" not in text
    assert "ERC_MANDATED_MCP_COMMAND" not in text
