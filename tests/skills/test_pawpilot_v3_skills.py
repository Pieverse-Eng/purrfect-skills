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
    tools._SKILLS_CACHE.clear()
    for name in OPERATIONS:
        shutil.copytree(SOURCE / name, tools.SKILLS_DIR / name)
    yield tools
    tools._SKILLS_CACHE.clear()

@pytest.mark.parametrize("name,required_tool", OPERATIONS.items())
def test_v3_routing_requires_the_actual_bound_operation(name, required_tool, loader):
    from agent.skill_utils import extract_skill_conditions
    from agent.prompt_builder import _skill_should_show
    metadata, _ = loader._parse_frontmatter((SOURCE / name / "SKILL.md").read_text())
    conditions = extract_skill_conditions(metadata)
    assert not _skill_should_show(conditions, {"terminal_read", "paper_prepare_card"}, {"api_host_tools"})
    assert _skill_should_show(conditions, {required_tool}, {"api_host_tools"})
    loaded = json.loads(loader.skill_view(name))
    assert loaded["success"], loaded
    assert loaded["content"] == (SOURCE / name / "SKILL.md").read_text()
    loader._SKILLS_CACHE.clear()
