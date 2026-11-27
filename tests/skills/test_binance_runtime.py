"""Real Skill loading must bind managed credentials without gating public reads.

Run through the Hermes checkout's scripts/run_tests.sh with one worker.
Fake credentials and a native local child only; no exchange or model requests.
"""
import importlib.util
import json
from pathlib import Path
import shutil
import sys

import pytest

SOURCE = Path(__file__).resolve().parents[2]


@pytest.fixture
def loader(tmp_path, monkeypatch):
    monkeypatch.setenv("HERMES_HOME", str(tmp_path / "home"))
    monkeypatch.setenv("SKILL_SECURITY_GATE_ENABLED", "false")
    from tools import skills_tool
    from tools.env_passthrough import clear_env_passthrough
    monkeypatch.setattr(skills_tool, "SKILLS_DIR", tmp_path / "skills")
    monkeypatch.setattr("agent.skill_utils.get_external_skills_dirs", lambda: [])
    monkeypatch.setattr(skills_tool, "_get_disabled_skill_names", lambda: set())
    monkeypatch.setattr(skills_tool, "_is_skill_disabled", lambda name: False)
    monkeypatch.setattr(skills_tool, "_secret_capture_callback", lambda *args: pytest.fail("Public reads must not prompt for exchange credentials"))
    shutil.copytree(SOURCE / "binance", skills_tool.SKILLS_DIR / "binance")
    clear_env_passthrough()
    skills_tool._SKILLS_CACHE.clear()
    yield skills_tool
    clear_env_passthrough()
    skills_tool._SKILLS_CACHE.clear()


def test_binance_public_skill_loads_without_exchange_credentials(loader, monkeypatch):
    monkeypatch.delenv("BINANCE_API_KEY", raising=False)
    monkeypatch.delenv("BINANCE_SECRET_KEY", raising=False)
    loaded = json.loads(loader.skill_view("binance"))
    assert loaded["success"], loaded
    assert loaded["setup_needed"] is False
    assert loaded["missing_required_environment_variables"] == []


def test_binance_skill_load_delivers_session_material_to_actual_child(loader, tmp_path, monkeypatch):
    from agent.secret_scope import set_secret_scope, reset_secret_scope
    from tools.environments.local import LocalEnvironment
    monkeypatch.setenv("BINANCE_API_KEY", "cex-session-managed")
    monkeypatch.setenv("BINANCE_SECRET_KEY", "cex-session-managed")
    assert json.loads(loader.skill_view("binance"))["success"]
    # The middleware is an optional Platform consumer. Find the enclosing
    # Platform checkout rather than importing a developer's installed plugin.
    source = next(parent / "hermes-plugins" / "cex-credential-sessions" for parent in SOURCE.parents if (parent / "hermes-plugins" / "cex-credential-sessions").is_dir())
    spec = importlib.util.spec_from_file_location("binance_runtime_fixture", source / "__init__.py", submodule_search_locations=[str(source)])
    module = importlib.util.module_from_spec(spec)
    monkeypatch.setitem(sys.modules, spec.name, module)
    spec.loader.exec_module(module)
    reads = []

    def factory(**options):
        def request(group, version):
            reads.append((group, version))
            common = dict(instanceId=options["instance_id"], group=group, version="a" * 64)
            if version is None:
                return dict(**common, record=dict(format="cex-credentials-v1", version="a" * 64, ciphertext="opaque"))
            return dict(**common, issuedAt=1800000000000, expiresAt=1800001800000, credentials=dict(key="k" * 64, secret="s" * 64))
        return module.Provider(**options, request=request, now=lambda: 1800000000000)

    middleware = module.CredentialMiddleware(lambda: {"groups": ["binance"], "versions": {"binance": "a" * 64}}, factory)
    scope = set_secret_scope({"INSTANCE_ID": "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa", "WALLET_API_URL": "https://platform.test", "WALLET_API_TOKEN": "fake-own-token"})
    environment = LocalEnvironment(cwd=str(tmp_path), timeout=10)
    try:
        command = 'test "$BINANCE_API_KEY" = ' + 'k' * 64 + ' && test "$BINANCE_SECRET_KEY" = ' + 's' * 64 + ' && printf managed-child-ok'
        result = middleware(tool_name="terminal", args={"command": command}, next_call=lambda args: environment.execute(args["command"]))
        assert "managed-child-ok" in json.dumps(result), result
        assert len(reads) == 2
    finally:
        environment.cleanup()
        reset_secret_scope(scope)
        middleware.close()
