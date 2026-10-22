"""Load the authored v3 Skills through the actual Hermes loader.

Run from a Hermes checkout with scripts/run_tests.sh <this-file> -j 1.
No model, account credentials, or external service is used.
"""
import json
import shutil
from pathlib import Path

import pytest

SOURCE = Path(__file__).resolve().parents[2]
OPERATIONS = {
    "pawpilot-terminal": "pawpilot_task_status",
    "pawpilot-paper-trade-prepare": "pawpilot_paper_trade_prepare",
    "pawpilot-paper-trade-check": "pawpilot_paper_trade_check",
    "pawpilot-paper-trade-plan": "pawpilot_paper_trade_plan_save",
    "pawpilot-paper-trade-review": "pawpilot_paper_trade_review",
    "pawpilot-paper-trade-practice": "pawpilot_paper_trade_invite",
    "pawpilot-position-deep-research": "pawpilot_position_research",
}

@pytest.fixture
def loader(tmp_path, monkeypatch):
    monkeypatch.setenv("HERMES_HOME", str(tmp_path / "home"))
    monkeypatch.setenv("SKILL_SECURITY_GATE_ENABLED", "false")
    import tools.skills_tool as tools
    monkeypatch.setattr(tools, "SKILLS_DIR", tmp_path / "skills")
    monkeypatch.setattr("agent.skill_utils.get_external_skills_dirs", lambda: [])
    monkeypatch.setattr(tools, "_get_disabled_skill_names", lambda: set())
    monkeypatch.setattr(tools, "_is_skill_disabled", lambda name: name in tools._get_disabled_skill_names())
    from tools.registry import ToolRegistry, registry
    proxies = ToolRegistry()
    for tool in OPERATIONS.values():
        proxies.register(name=tool, toolset="api_host_tools",
                         schema={"name": tool, "parameters": {"type": "object", "properties": {}}},
                         handler=lambda *args, **kwargs: pytest.fail("Viewing a Skill must not execute it"))
        monkeypatch.setitem(registry._tools, tool, proxies._tools[tool])
    tools._SKILLS_CACHE.clear()
    for name in OPERATIONS:
        shutil.copytree(SOURCE / name, tools.SKILLS_DIR / name)
    yield tools
    tools._SKILLS_CACHE.clear()

@pytest.mark.parametrize("name,required_tool", OPERATIONS.items())
def test_v3_routing_requires_the_actual_bound_operation(name, required_tool, loader):
    from gateway.interactive_messages import current_message_scope
    assert not json.loads(loader.skill_view(name))["success"]
    with current_message_scope(lambda *args: None, {
        "version": 2, "execution_policy": "pawpilot", "host_tools": [required_tool],
    }):
        listing = json.loads(loader.skills_list())
        assert [item["name"] for item in listing["skills"]] == [name]
        loaded = json.loads(loader.skill_view(name))
        assert loaded["success"], loaded
        assert loaded["content"] == (SOURCE / name / "SKILL.md").read_text()
    assert not json.loads(loader.skill_view(name))["success"]
