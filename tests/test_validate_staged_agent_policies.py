import json
import hashlib
import re
from pathlib import Path
import shutil

import pytest

from tools.validate_staged_agent_policies import validate


def write_fixture(tmp_path: Path, text: str | None = None) -> tuple[Path, Path]:
    root = tmp_path / "staging"
    staging = Path("/Users/tucker.beck/agent-workflow-staging")
    staging_config = staging / ".config/opencode/agents"
    config_files = [path.relative_to(staging) for path in staging_config.glob("*.md")]
    paths_to_copy = [
        Path(".agents/agents/principal.md"),
        Path(".agents/skills/run-feature/SKILL.md"),
        Path(".agents/skills/run-task/SKILL.md"),
        Path(".agents/skills/run-hack/SKILL.md"),
        Path(".agents/skills/run-bug-fix/SKILL.md"),
        Path(".agents/skills/run-fix/SKILL.md"),
        Path(".agents/skills/run-hotfix/SKILL.md"),
        *config_files,
    ]
    for relative in paths_to_copy:
        destination = root / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(staging / relative, destination)
    if text is not None:
        (root / ".agents/agents/principal.md").write_text(text)
    paths = paths_to_copy
    manifest = root / "manifest.json"
    manifest.write_text(json.dumps({
        "staging_root": str(root),
        "files": [{"staged_path": str(path), "sha256": hashlib.sha256((root / path).read_bytes()).hexdigest()} for path in paths],
        "promotion": {
            "approval_required": True, "atomic_replacement": True,
            "rollback_required": True, "restart_required": "OpenCode",
        },
    }))
    return root, manifest


def test_validator_accepts_complete_fixture(tmp_path: Path) -> None:
    root, manifest = write_fixture(tmp_path)
    assert validate(root, manifest) == []


def test_validator_requires_all_work_claude_variants(tmp_path: Path) -> None:
    root, manifest = write_fixture(tmp_path)
    variant = root / ".config/opencode/agents/architect-planner--work-haiku.md"
    variant.unlink()
    assert "architect-planner--work-haiku.md" in "\n".join(validate(root, manifest))


def test_validator_requires_personal_luna_variants(tmp_path: Path) -> None:
    root, manifest = write_fixture(tmp_path)
    variant = root / ".config/opencode/agents/architect-planner--personal-luna.md"
    variant.unlink()
    assert "architect-planner--personal-luna.md" in "\n".join(validate(root, manifest))


def test_validator_rejects_personal_sonnet_variants(tmp_path: Path) -> None:
    root, manifest = write_fixture(tmp_path)
    luna = root / ".config/opencode/agents/architect-planner--personal-luna.md"
    sonnet = root / ".config/opencode/agents/architect-planner--personal-sonnet.md"
    luna.rename(sonnet)
    failures = validate(root, manifest)
    assert any("personal Sonnet" in failure for failure in failures)


def test_validator_reports_inventory_stale_reference_and_promotion_failures(tmp_path: Path) -> None:
    root, manifest = write_fixture(tmp_path, "run-implementation")
    manifest.write_text(json.dumps({"staging_root": str(root), "files": [], "promotion": {}}))
    failures = validate(root, manifest)
    assert any("inventory" in failure for failure in failures)
    assert any("run-implementation" in failure for failure in failures)
    assert any("promotion" in failure for failure in failures)


@pytest.mark.parametrize(
    "text",
    [
        "Historical note: do not use opencode/zen for work-project dispatch.",
        "The string opencode/zen appears in documentation unrelated to dispatch.",
    ],
)
def test_validator_ignores_non_dispatch_model_mentions(tmp_path: Path, text: str) -> None:
    root, manifest = write_fixture(tmp_path)
    principal = root / ".agents/agents/principal.md"
    principal.write_text(principal.read_text() + f"\n{text}")
    manifest_data = json.loads(manifest.read_text())
    manifest_data["files"][0]["sha256"] = hashlib.sha256(principal.read_bytes()).hexdigest()
    manifest.write_text(json.dumps(manifest_data))
    assert validate(root, manifest) == []


def test_validator_requires_structured_principal_ownership(tmp_path: Path) -> None:
    root, manifest = write_fixture(tmp_path, "The principal participates in reviews.")
    assert "missing principal ownership" in "\n".join(validate(root, manifest))


@pytest.mark.parametrize(
    ("relative", "needle"),
    [
        (".agents/skills/run-feature/SKILL.md", "before any artifact"),
        (".agents/skills/run-task/SKILL.md", "agent worktree"),
        (".agents/skills/run-hack/SKILL.md", "no Git lifecycle"),
    ],
)
def test_validator_rejects_missing_worktree_lifecycle_requirement(
    tmp_path: Path, relative: str, needle: str
) -> None:
    root, manifest = write_fixture(tmp_path)
    path = root / relative
    path.write_text(path.read_text().replace(needle, "removed lifecycle text"))
    assert any(relative in failure and "lifecycle requirement" in failure for failure in validate(root, manifest))


def test_validator_rejects_unvaried_dispatch(tmp_path: Path) -> None:
    root, manifest = write_fixture(tmp_path)
    path = root / ".agents/skills/run-task/SKILL.md"
    path.write_text(path.read_text() + "\nDispatch an `engineer-executor` subagent.\n")
    assert any("unvaried specialist dispatch" in failure for failure in validate(root, manifest))


@pytest.mark.parametrize(
    "text",
    [
        "The policy will never silently rebase or merge human work.",
        "Never silently rebase or merge human work.",
    ],
)
def test_validator_ignores_qualified_unsafe_mutation_language(tmp_path: Path, text: str) -> None:
    root, manifest = write_fixture(tmp_path)
    path = root / ".agents/skills/run-feature/SKILL.md"
    path.write_text(path.read_text() + f"\n{text}\n")
    failures = validate(root, manifest)
    assert not any("permits silent Git mutation" in failure for failure in failures)


def test_validator_rejects_unqualified_unsafe_mutation_language(tmp_path: Path) -> None:
    root, manifest = write_fixture(tmp_path)
    path = root / ".agents/skills/run-feature/SKILL.md"
    path.write_text(path.read_text() + "\nThe workflow will silently rebase human work.\n")
    failures = validate(root, manifest)
    assert any("permits silent Git mutation" in failure for failure in failures)


@pytest.mark.parametrize(
    ("relative", "needle"),
    [
        (".agents/skills/run-bug-fix/SKILL.md", "before investigation"),
        (".agents/skills/run-fix/SKILL.md", "fail closed"),
        (".agents/skills/run-hotfix/SKILL.md", "exclusive squash integration"),
    ],
)
def test_validator_rejects_missing_branch_workflow_lifecycle_requirement(
    tmp_path: Path, relative: str, needle: str
) -> None:
    root, manifest = write_fixture(tmp_path)
    path = root / relative
    path.write_text(re.sub(needle, "removed lifecycle text", path.read_text(), count=1, flags=re.IGNORECASE))
    assert any(relative in failure and "lifecycle requirement" in failure for failure in validate(root, manifest))


def test_validator_requires_run_fix_fail_closed_attachment(tmp_path: Path) -> None:
    root, manifest = write_fixture(tmp_path)
    path = root / ".agents/skills/run-fix/SKILL.md"
    path.write_text(re.sub("Fail closed", "Guess the project path", path.read_text(), count=1))
    assert any("fail-closed attachment control" in failure for failure in validate(root, manifest))


def test_validator_preserves_hotfix_streamlined_gate_and_no_planner(tmp_path: Path) -> None:
    root, manifest = write_fixture(tmp_path)
    path = root / ".agents/skills/run-hotfix/SKILL.md"
    path.write_text(path.read_text().replace("one lightweight review", "two reviews", 1))
    failures = validate(root, manifest)
    assert any("streamlined gate control" in failure for failure in failures)


@pytest.mark.parametrize("field", ["model", "hack", "task"])
def test_validator_rejects_missing_required_policy(tmp_path: Path, field: str) -> None:
    root, manifest = write_fixture(tmp_path)
    if field == "model":
        (root / ".agents/agents/principal.md").write_text("The principal owns risk and escalation.")
    elif field == "hack":
        path = root / ".agents/skills/run-hack/SKILL.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("---\nname: run-task\n---\n")
    else:
        path = root / ".agents/skills/run-task/SKILL.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("# task\n")
    assert validate(root, manifest)
