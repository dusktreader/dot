import hashlib
import json
import re
import shutil
from pathlib import Path

import pytest

from tools.validate_staged_agent_policies import validate


def write_fixture(tmp_path: Path, text: str | None = None) -> tuple[Path, Path]:
    root = tmp_path / "staging"
    source = Path(__file__).parents[1]
    relative_files = [
        Path(".agents/agents/principal.md"),
        Path(".agents/skills/create-agent-worktree/SKILL.md"),
        Path(".agents/skills/cleanup-agent-worktree/SKILL.md"),
        Path(".agents/skills/run-feature/SKILL.md"),
        Path(".agents/skills/run-task/SKILL.md"),
        Path(".agents/skills/run-hack/SKILL.md"),
        Path(".agents/skills/run-bug-fix/SKILL.md"),
        Path(".agents/skills/run-fix/SKILL.md"),
        Path(".agents/skills/run-hotfix/SKILL.md"),
        Path(".agents/skills/run-pr/SKILL.md"),
        Path(".agents/skills/external-review/SKILL.md"),
        *[path.relative_to(source) for path in (source / ".config/opencode/agents").glob("*.md")],
    ]
    for relative in relative_files:
        destination = root / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source / relative, destination)
    if text is not None:
        (root / ".agents/agents/principal.md").write_text(text)
    manifest = root / "manifest.json"
    manifest.write_text(json.dumps({
        "staging_root": str(root),
        "files": [
            {"staged_path": str(path), "sha256": hashlib.sha256((root / path).read_bytes()).hexdigest()}
            for path in relative_files
        ],
        "promotion": {
            "approval_required": True,
            "atomic_replacement": True,
            "rollback_required": True,
            "restart_required": "OpenCode",
        },
    }))
    return root, manifest


def add_manifest_file(root: Path, manifest: Path, relative: Path) -> None:
    """Add a newly created fixture file to its manifest inventory."""
    manifest_data = json.loads(manifest.read_text())
    manifest_data["files"].append({
        "staged_path": str(relative),
        "sha256": hashlib.sha256((root / relative).read_bytes()).hexdigest(),
    })
    manifest.write_text(json.dumps(manifest_data))


def test_validator_accepts_shared_role_fixture(tmp_path: Path) -> None:
    root, manifest = write_fixture(tmp_path)
    assert validate(root, manifest) == []


def test_validator_requires_shared_worktree_skills(tmp_path: Path) -> None:
    root, manifest = write_fixture(tmp_path)
    (root / ".agents/skills/create-agent-worktree/SKILL.md").unlink()
    assert any("missing shared worktree skill" in failure for failure in validate(root, manifest))


@pytest.mark.parametrize(
    "relative",
    [
        ".agents/skills/run-feature/SKILL.md",
        ".agents/skills/run-task/SKILL.md",
        ".agents/skills/run-bug-fix/SKILL.md",
        ".agents/skills/run-fix/SKILL.md",
        ".agents/skills/run-hotfix/SKILL.md",
    ],
)
def test_validator_requires_shared_worktree_references(tmp_path: Path, relative: str) -> None:
    root, manifest = write_fixture(tmp_path)
    path = root / relative
    path.write_text(path.read_text().replace("create-agent-worktree", "missing-worktree-skill"))
    assert any(relative in failure and "shared worktree reference" in failure for failure in validate(root, manifest))


@pytest.mark.parametrize(
    ("relative", "plumbing"),
    [
        (".agents/skills/run-feature/SKILL.md", "git branch feature/example"),
        (".agents/skills/run-task/SKILL.md", "git worktree add /tmp/agent branch"),
        (".agents/skills/run-bug-fix/SKILL.md", "feature/example--agents-bug-fix"),
        (".agents/skills/run-fix/SKILL.md", "allocate an audit branch"),
        (".agents/skills/run-hotfix/SKILL.md", "select a zero-padded suffix"),
    ],
)
def test_validator_rejects_duplicate_worktree_plumbing(tmp_path: Path, relative: str, plumbing: str) -> None:
    root, manifest = write_fixture(tmp_path)
    path = root / relative
    path.write_text(path.read_text() + f"\n{plumbing}\n")
    assert any(relative in failure and "duplicate worktree plumbing" in failure for failure in validate(root, manifest))


@pytest.mark.parametrize(
    ("relative", "shared_reference"),
    [
        (".agents/skills/run-feature/SKILL.md", "cleanup-agent-worktree"),
        (".agents/skills/run-task/SKILL.md", "cleanup-agent-worktree"),
        (".agents/skills/run-bug-fix/SKILL.md", "cleanup-agent-worktree"),
        (".agents/skills/run-fix/SKILL.md", "cleanup-agent-worktree"),
        (".agents/skills/run-hotfix/SKILL.md", "cleanup-agent-worktree"),
    ],
)
def test_validator_rejects_wrong_shared_worktree_skill(
    tmp_path: Path, relative: str, shared_reference: str
) -> None:
    root, manifest = write_fixture(tmp_path)
    path = root / relative
    path.write_text(path.read_text().replace(shared_reference, "missing-worktree-skill"))
    assert any(relative in failure and "shared worktree reference" in failure for failure in validate(root, manifest))


@pytest.mark.parametrize(
    ("relative", "needle"),
    [
        (".agents/skills/create-agent-worktree/SKILL.md", "<repo>/.worktrees/"),
        (".agents/skills/cleanup-agent-worktree/SKILL.md", "git worktree list"),
        (".agents/skills/cleanup-agent-worktree/SKILL.md", "If `worktree_created` is false, do nothing."),
    ],
)
def test_validator_requires_shared_worktree_contract(tmp_path: Path, relative: str, needle: str) -> None:
    root, manifest = write_fixture(tmp_path)
    path = root / relative
    path.write_text(path.read_text().replace(needle, "removed contract"))
    assert any("shared worktree contract" in failure for failure in validate(root, manifest))


def test_validator_rejects_profile_specific_role(tmp_path: Path) -> None:
    root, manifest = write_fixture(tmp_path)
    extra = root / ".config/opencode/agents/engineer-executor--work-luna.md"
    extra.write_text((root / ".config/opencode/agents/engineer-executor.md").read_text())
    add_manifest_file(root, manifest, extra.relative_to(root))
    assert any("profile-specific" in failure for failure in validate(root, manifest))


def test_validator_rejects_zen_work_dispatch(tmp_path: Path) -> None:
    root, manifest = write_fixture(tmp_path)
    principal = root / ".agents/agents/principal.md"
    principal.write_text(principal.read_text() + "\nprofile:work routes opencode/zen.\n")
    data = json.loads(manifest.read_text())
    data["files"][0]["sha256"] = hashlib.sha256(principal.read_bytes()).hexdigest()
    manifest.write_text(json.dumps(data))
    assert any("Zen model" in failure for failure in validate(root, manifest))


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
        (".agents/skills/run-task/SKILL.md", "before any artifact"),
        (".agents/skills/run-hack/SKILL.md", "no Git lifecycle"),
    ],
)
def test_validator_rejects_missing_worktree_lifecycle_requirement(tmp_path: Path, relative: str, needle: str) -> None:
    root, manifest = write_fixture(tmp_path)
    path = root / relative
    path.write_text(re.sub(needle, "removed lifecycle text", path.read_text(), flags=re.IGNORECASE))
    assert any(relative in failure and "lifecycle requirement" in failure for failure in validate(root, manifest))


def test_validator_rejects_model_specific_dispatch_names(tmp_path: Path) -> None:
    root, manifest = write_fixture(tmp_path)
    path = root / ".agents/skills/run-bug-fix/SKILL.md"
    path.write_text(path.read_text() + "\nDispatch engineer-executor--work-luna.\n")
    assert any("model-specific dispatch" in failure for failure in validate(root, manifest))


def test_validator_rejects_model_specific_run_hack_dispatch_names(tmp_path: Path) -> None:
    root, manifest = write_fixture(tmp_path)
    path = root / ".agents/skills/run-hack/SKILL.md"
    path.write_text(path.read_text() + "\nDispatch engineer-executor--work-luna.\n")
    manifest_data = json.loads(manifest.read_text())
    for item in manifest_data["files"]:
        if item["staged_path"] == str(path.relative_to(root)):
            item["sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
    manifest.write_text(json.dumps(manifest_data))
    failures = validate(root, manifest)
    assert any("model-specific dispatch" in failure for failure in failures)


def test_validator_requires_generic_role_profile_and_tier_contract(tmp_path: Path) -> None:
    root, manifest = write_fixture(tmp_path)
    path = root / ".agents/skills/run-fix/SKILL.md"
    path.write_text(path.read_text().replace("shared `engineer-executor` role", "engineer-executor--work-luna", 1))
    failures = validate(root, manifest)
    assert any("model-specific dispatch" in failure for failure in failures)


def test_validator_rejects_incorrect_shared_role_prompt(tmp_path: Path) -> None:
    root, manifest = write_fixture(tmp_path)
    path = root / ".config/opencode/agents/engineer-executor.md"
    path.write_text(path.read_text().replace("~/.agents/agents/engineer-executor.md", "~/.agents/agents/wrong-role.md"))
    assert any("shared role prompt" in failure for failure in validate(root, manifest))


@pytest.mark.parametrize(
    ("relative", "needle"),
    [
        (".agents/skills/run-bug-fix/SKILL.md", "before investigation"),
        (".agents/skills/run-fix/SKILL.md", "fail closed"),
        (".agents/skills/run-hotfix/SKILL.md", r"one lightweight\s+review"),
        (
            ".agents/skills/external-review/SKILL.md",
            "Never push before the human approves the exact change, commit message, and response.",
        ),
        (".agents/skills/create-agent-worktree/SKILL.md", "immutable parent base"),
        (".agents/skills/cleanup-agent-worktree/SKILL.md", "git worktree list"),
    ],
)
def test_validator_rejects_omitted_staged_policy_controls(tmp_path: Path, relative: str, needle: str) -> None:
    root, manifest = write_fixture(tmp_path)
    path = root / relative
    path.write_text(re.sub(needle, "removed control", path.read_text(), count=1, flags=re.IGNORECASE))
    failures = validate(root, manifest)
    assert any(relative in failure for failure in failures)


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
        (".agents/skills/run-hotfix/SKILL.md", r"one lightweight\s+review"),
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
    path.write_text(re.sub(r"one lightweight\s+review", "two reviews", path.read_text(), count=1))
    failures = validate(root, manifest)
    assert any("streamlined gate control" in failure for failure in failures)


@pytest.mark.parametrize("field", ["model", "hack", "task"])
def test_validator_rejects_missing_required_policy(tmp_path: Path, field: str) -> None:
    root, manifest = write_fixture(tmp_path)
    if field == "model":
        (root / ".agents/agents/principal.md").write_text("The principal owns risk and escalation.")
    elif field == "hack":
        path = root / ".agents/skills/run-hack/SKILL.md"
        path.write_text("---\nname: run-task\n---\n")
    else:
        path = root / ".agents/skills/run-task/SKILL.md"
        path.write_text("# task\n")
    assert validate(root, manifest)


@pytest.mark.parametrize(
    "relative",
    [
        ".agents/skills/run-feature/SKILL.md",
        ".agents/skills/run-task/SKILL.md",
        ".agents/skills/run-bug-fix/SKILL.md",
        ".agents/skills/run-fix/SKILL.md",
        ".agents/skills/run-hotfix/SKILL.md",
    ],
)
def test_validator_requires_branch_contract(tmp_path: Path, relative: str) -> None:
    root, manifest = write_fixture(tmp_path)
    path = root / relative
    path.write_text(path.read_text().replace("run-pr", "external-review"))
    assert any(relative in failure and "branch contract" in failure for failure in validate(root, manifest))


def test_validator_rejects_publication_and_worktree_mutation_controls(tmp_path: Path) -> None:
    root, manifest = write_fixture(tmp_path)
    task = root / ".agents/skills/run-task/SKILL.md"
    task.write_text(task.read_text() + "\ngit push origin feature\ngit switch feature/example\n")
    failures = validate(root, manifest)
    assert any("publication mechanics" in failure for failure in failures)
    assert any("permits git switch" in failure for failure in failures)


@pytest.mark.parametrize(
    "relative",
    [
        ".agents/skills/run-feature/SKILL.md",
        ".agents/skills/run-task/SKILL.md",
        ".agents/skills/run-bug-fix/SKILL.md",
        ".agents/skills/run-fix/SKILL.md",
        ".agents/skills/run-hotfix/SKILL.md",
    ],
)
def test_validator_requires_run_pr_handoff(tmp_path: Path, relative: str) -> None:
    root, manifest = write_fixture(tmp_path)
    path = root / relative
    path.write_text(path.read_text().replace("run-pr", "external-review"))
    assert any(relative in failure and "branch contract" in failure for failure in validate(root, manifest))


def test_validator_preserves_principal_ownership_and_run_pr_controls(tmp_path: Path) -> None:
    root, manifest = write_fixture(tmp_path, "The principal participates in reviews.")
    failures = validate(root, manifest)
    assert any("principal ownership" in failure for failure in failures)

    run_pr = root / ".agents/skills/run-pr/SKILL.md"
    run_pr.write_text(run_pr.read_text().replace("Reject `main` and `master`", "Allow `main` and `master`", 1))
    assert any("run-pr missing required control" in failure for failure in validate(root, manifest))


def test_validator_rejects_external_review_force_push_and_missing_approval_gate(tmp_path: Path) -> None:
    root, manifest = write_fixture(tmp_path)
    external_review = root / ".agents/skills/external-review/SKILL.md"
    original = external_review.read_text()
    external_review.write_text(original + "\ngit push --force origin feature\n")
    assert any("external-review includes a force push" in failure for failure in validate(root, manifest))

    approval_gate = "Never push before the human approves the exact change, commit message, and response."
    external_review.write_text(original.replace(approval_gate, "Push before human approval."))
    assert any(approval_gate in failure for failure in validate(root, manifest))


@pytest.mark.parametrize(
    "relative",
    [
        ".agents/skills/run-feature/SKILL.md",
        ".agents/skills/run-task/SKILL.md",
        ".agents/skills/run-bug-fix/SKILL.md",
        ".agents/skills/run-fix/SKILL.md",
        ".agents/skills/run-hotfix/SKILL.md",
    ],
)
def test_validator_rejects_automatic_temporary_branch_deletion(tmp_path: Path, relative: str) -> None:
    root, manifest = write_fixture(tmp_path)
    path = root / relative
    path.write_text(path.read_text() + "\ngit branch -D feature/example--agents-task\n")
    assert any(relative in failure and "automatic temporary branch deletion" in failure for failure in validate(root, manifest))
