"""Run from a Hermes checkout with scripts/run_tests.sh <this-file> -j 1.

The real Hermes loader is the contract under test; no network, credentials,
installed user Skills, or model provider are involved.
"""

import json
import re
import shutil
from pathlib import Path
from types import SimpleNamespace

import pytest

SOURCE = Path(__file__).resolve().parents[2]
NAMES = ("pawpilot-paper-trading", "pawpilot-trading-coach")
SECTIONS = (
    "When to Use", "Prerequisites", "How to Run", "Quick Reference",
    "Procedure", "Pitfalls", "Verification",
)


@pytest.fixture
def native_loader(tmp_path, monkeypatch):
    monkeypatch.setenv("HERMES_HOME", str(tmp_path / "home"))
    import tools.skills_tool as skill_tools
    from tools.execution_scope import proposal_only_scope
    from tools.registry import registry

    monkeypatch.setattr(skill_tools, "SKILLS_DIR", tmp_path / "skills")
    monkeypatch.setattr("agent.skill_utils.get_external_skills_dirs", lambda: [])
    monkeypatch.setattr(skill_tools, "_get_disabled_skill_names", lambda: set())
    monkeypatch.setattr(skill_tools, "_is_skill_disabled", lambda name: name in skill_tools._get_disabled_skill_names())
    for name in ("paper_read", "paper_prepare_card"):
        monkeypatch.setitem(registry._tools, name, SimpleNamespace(toolset="api_host_tools"))
    # This probe exercises authored content/loading; native restricted-mode
    # policy and malicious fixtures are tested separately in Hermes itself.
    monkeypatch.setenv("SKILL_SECURITY_GATE_ENABLED", "false")
    skill_tools._SKILLS_CACHE.clear()
    for name in NAMES:
        shutil.copytree(SOURCE / name, skill_tools.SKILLS_DIR / name)
    with proposal_only_scope(True, host_tools={"paper_read", "paper_prepare_card"}):
        yield skill_tools
    skill_tools._SKILLS_CACHE.clear()


@pytest.mark.parametrize("name", NAMES)
def test_native_authoring_catalogue_and_complete_references(name, native_loader, monkeypatch):
    from agent.skill_utils import extract_skill_conditions
    from agent.prompt_builder import _skill_should_show

    source = (SOURCE / name / "SKILL.md").read_text()
    metadata, body = native_loader._parse_frontmatter(source)
    assert metadata["name"] == name
    assert re.fullmatch(r"\d+\.\d+\.\d+", metadata["version"])
    description = metadata["description"]
    assert len(description) <= 60, "Hermes catalogue descriptions must fit 60 characters"
    assert description.endswith(".") and description.count(".") == 1
    assert metadata["author"].startswith("David Zhou (@David-0x221Eight)")
    assert body.splitlines()[0].endswith(" Skill")
    assert re.findall(r"^## (.+)$", body, re.MULTILINE) == list(SECTIONS)
    required = extract_skill_conditions(metadata)
    assert _skill_should_show(required, {"paper_read", "paper_prepare_card"}, set())
    assert not _skill_should_show(required, set(), set())
    if name == "pawpilot-paper-trading":
        assert not _skill_should_show(required, {"paper_read"}, set())

    listing = json.loads(native_loader.skills_list())
    entry = next(item for item in listing["skills"] if item["name"] == name)
    assert entry["description"] == description
    loaded = json.loads(native_loader.skill_view(name))
    assert loaded["success"] is True, loaded
    assert body.strip() in loaded["content"]
    references = re.findall(r"\]\((references/[^)]+)\)", body)
    assert references
    assert set(references) == {
        str(path.relative_to(SOURCE / name)) for path in (SOURCE / name / "references").glob("*.md")
    }
    for reference in references:
        result = json.loads(native_loader.skill_view(name, file_path=reference))
        assert result["success"] is True, result
        assert result["content"] == (SOURCE / name / reference).read_text()
    monkeypatch.setattr(native_loader, "_get_disabled_skill_names", lambda: {name})
    assert name not in [item["name"] for item in json.loads(native_loader.skills_list())["skills"]]
    assert not json.loads(native_loader.skill_view(name))["success"]
