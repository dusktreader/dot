"""Validate an isolated complete agent-policy staging tree."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path


_ZEN_DISPATCH = re.compile(
    r"^(?!.*\b(?:do not|don't|not)\b.*opencode/).*(?:work-project.*opencode/|opencode/.*work-project).*$",
    re.IGNORECASE | re.MULTILINE,
)
_PRINCIPAL_OWNERSHIP = re.compile(
    r"(?:principal.{0,120}(?:own|decid|control).{0,120}(?:risk|escalat)|"
    r"(?:risk|escalat).{0,120}(?:own|decid|control).{0,120}principal)",
    re.IGNORECASE | re.DOTALL,
)
_SPECIALIST_ROLES = (
    "architect-planner",
    "architect-reviewer",
    "engineer-planner",
    "engineer-task-planner",
    "engineer-investigator",
    "engineer-executor",
    "engineer-reviewer",
)
_WORK_MODELS = {
    "luna": "github-copilot/gpt-5.6-luna",
    "sol": "github-copilot/gpt-5.6-sol",
}
_WORK_NON_REVIEW_ROLES = tuple(role for role in _SPECIALIST_ROLES if "reviewer" not in role)
_WORK_REVIEW_ROLES = tuple(role for role in _SPECIALIST_ROLES if "reviewer" in role)
_PERSONAL_MODELS = {
    "luna": "opencode/gpt-5.6-luna",
    "sol": "opencode/gpt-5.6-sol",
}
_PERSONAL_NON_REVIEW_ROLES = tuple(role for role in _SPECIALIST_ROLES if "reviewer" not in role)
_PERSONAL_REVIEW_ROLES = tuple(role for role in _SPECIALIST_ROLES if "reviewer" in role)
_LIFECYCLE_REQUIREMENTS = {
    ".agents/skills/run-feature/SKILL.md": (
        "agent worktree",
        "agent branch",
        "before any artifact",
        "exclusive squash integration",
        "stale-parent",
        "locally indefinitely",
    ),
    ".agents/skills/run-task/SKILL.md": (
        "agent worktree",
        "agent branch",
        "before any artifact",
        "exclusive squash integration",
        "stale-parent",
        "locally indefinitely",
    ),
    ".agents/skills/run-hack/SKILL.md": (
        "current branch",
        "no worktree",
        "no Git lifecycle",
        "only one artifact",
    ),
    ".agents/skills/run-bug-fix/SKILL.md": (
        "agent worktree",
        "agent branch",
        "before investigation",
        "exact variant",
        "implementation journal",
        "final QA exactly once",
        "exclusive squash integration",
        "stale-parent",
        "locally indefinitely",
    ),
    ".agents/skills/run-fix/SKILL.md": (
        "agent worktree",
        "agent branch",
        "before reading or writing fix artifacts",
        "fail closed",
        "exact variant",
        "exclusive squash integration",
        "stale parent",
        "locally indefinitely",
    ),
    ".agents/skills/run-hotfix/SKILL.md": (
        "agent worktree",
        "agent branch",
        "before investigation",
        "exact variant",
        "hotfix journal",
        "one lightweight review",
        "exclusive squash integration",
        "stale parent",
        "locally indefinitely",
    ),
    ".agents/skills/review-pr/SKILL.md": (
        "agent worktree",
        "agent branch",
        "stale-parent",
        "remove only the agent worktree",
        "locally indefinitely",
        "never delete it automatically",
        "only explicit human cleanup may delete",
        "direct the user to run-pr",
    ),
}
_UNSAFE_MUTATION = re.compile(
    r"\b(?:silently|automatically|without explicit (?:human )?(?:approval|decision))\b.{0,80}"
    r"\b(?:rebase|merge|discard|overwrite)\b",
    re.IGNORECASE | re.DOTALL,
)
_BRANCH_WORKFLOWS = (
    ".agents/skills/run-feature/SKILL.md",
    ".agents/skills/run-task/SKILL.md",
    ".agents/skills/run-bug-fix/SKILL.md",
    ".agents/skills/run-fix/SKILL.md",
    ".agents/skills/run-hotfix/SKILL.md",
)
_TEMPORARY_BRANCH_WORKFLOWS = (*_BRANCH_WORKFLOWS, ".agents/skills/review-pr/SKILL.md")
_SHARED_WORKTREE_SKILLS = (
    ".agents/skills/create-agent-worktree/SKILL.md",
    ".agents/skills/cleanup-agent-worktree/SKILL.md",
)
_SHARED_SKILL_CONTRACTS = {
    ".agents/skills/create-agent-worktree/SKILL.md": (
        "parent worktree",
        "parent branch",
        "immutable parent base",
        "workflow identifier",
        "<repo-root>/.worktrees/<agent-branch>",
        "Never use `git switch`",
        "zero-padded suffix",
    ),
    ".agents/skills/cleanup-agent-worktree/SKILL.md": (
        "git worktree remove",
        "git worktree list",
        "git branch --list",
        "creation result",
        "no temporary audit branch was created",
        "Audit branch deletion is forbidden",
        "Declined integration",
        "abandoned work",
    ),
}
_DUPLICATE_WORKTREE_PLUMBING = re.compile(
    r"\bgit (?:branch\s+(?!and\b|--list\b)|worktree (?:add|remove)\b)|"
    r"--agents-(?:feature|task|bug-fix|fix|hotfix|review)(?:-\d+)?|"
    r"(?:allocate|select)\s+(?:an?\s+)?(?:audit|branch)|"
    r"(?:allocate|select)\s+(?:an?\s+)?(?:numbered|zero-padded|suffix)",
    re.IGNORECASE,
)
_BRANCH_CONTRACT = (
    "local/audit only",
    "tell the human to invoke `run-pr`",
    "never pushes, creates a pull request, or merges into `main` or `master`",
    "stop and obtain explicit human approval before integration",
    "rebase the normal branch onto current main",
    "git merge --ff-only",
    "Never squash directly to main.",
)
_ORDERED_MAIN_INTEGRATION = re.compile(
    r"stop and obtain explicit human approval before integration.{0,500}"
    r"after approval rebase the\s+normal branch onto current main.{0,500}"
    r"(?:then use )?`?git merge --ff-only`?.{0,500}never squash directly to main",
    re.IGNORECASE | re.DOTALL,
)


def _has_unsafe_mutation(text: str) -> bool:
    """Return whether text permits an unqualified Git mutation.

    Evaluate each match against the current sentence rather than using a fixed-width
    lookbehind. This preserves the exemption for policy language such as
    ``The policy will never silently rebase`` regardless of how far ``never`` is
    from the matched unsafe action.
    """
    for sentence in re.split(r"(?<=[.!?])\s+|\n+", text):
        for match in _UNSAFE_MUTATION.finditer(sentence):
            if not re.search(r"\bnever\b", sentence[:match.start()], re.IGNORECASE):
                return True
    return False


def validate(staging_root: Path, manifest_path: Path) -> list[str]:
    """Return actionable validation failures for a staged policy set."""
    failures: list[str] = []
    manifest = json.loads(manifest_path.read_text())
    if manifest.get("staging_root") != str(staging_root):
        failures.append("manifest staging_root does not identify the requested staging tree")
    listed = [Path(item["staged_path"]) for item in manifest.get("files", [])]
    actual = sorted(
        path.relative_to(staging_root)
        for directory in (staging_root / ".agents", staging_root / ".config/opencode/agents")
        for path in directory.rglob("*")
        if path.is_file()
    )
    listed_set = set(listed)
    actual_set = set(actual)
    if listed_set != actual_set:
        failures.append(f"manifest inventory mismatch: missing={sorted(listed_set - actual_set)}, extra={sorted(actual_set - listed_set)}")
    for item in manifest.get("files", []):
        path = staging_root / item["staged_path"]
        if path.is_file():
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            if item.get("sha256") != digest:
                failures.append(f"manifest checksum mismatch: {item['staged_path']}")
    policy_text = {
        path: (staging_root / path).read_text(errors="replace")
        for path in actual
        if path.suffix in {".md", ".txt"}
    }
    text = "\n".join(policy_text.values())
    if re.search(r"\brun-implementation\b", text):
        failures.append("stale run-implementation workflow reference")
    dispatch_text = "\n".join(
        content for path, content in policy_text.items() if path.parts[:2] == (".agents", "agents")
    )
    if _ZEN_DISPATCH.search(dispatch_text):
        failures.append("Zen model appears in work-project dispatch policy")
    config_agents = staging_root / ".config/opencode/agents"
    expected_variants = {
        f"{role}--work-{suffix}.md": ("work", suffix, _WORK_MODELS[suffix])
        for role in _WORK_NON_REVIEW_ROLES
        for suffix in ("luna", "sol")
    } | {
        f"{role}--work-luna.md": ("work", "luna", _WORK_MODELS["luna"])
        for role in _WORK_REVIEW_ROLES
    } | {
        f"{role}--personal-{suffix}.md": ("personal", suffix, _PERSONAL_MODELS[suffix])
        for role in _PERSONAL_NON_REVIEW_ROLES
        for suffix in ("luna", "sol")
    } | {
        f"{role}--personal-luna.md": ("personal", "luna", _PERSONAL_MODELS["luna"])
        for role in _PERSONAL_REVIEW_ROLES
    }
    actual_variants = {path.name for path in config_agents.glob("*.md") if path.name != "principal.md"}
    missing = sorted(set(expected_variants) - actual_variants)
    extra = sorted(actual_variants - set(expected_variants))
    if missing:
        failures.append(f"missing model variants: {missing}")
    if extra:
        failures.append(f"unexpected or generic specialist agents: {extra}")
    for filename, (project_class, suffix, model) in expected_variants.items():
        path = config_agents / filename
        if not path.is_file():
            continue
        content = path.read_text()
        frontmatter, separator, body = content.partition("\n---\n")
        expected_name = filename.removesuffix(".md")
        if f"name: {expected_name}" not in frontmatter or "mode: subagent" not in frontmatter:
            failures.append(f"variant frontmatter is incorrect: {filename}")
        if f"model: {model}" not in frontmatter:
            failures.append(f"variant model does not match {project_class} suffix: {filename}")
        role = filename.removesuffix(".md").split("--", 1)[0]
        expected_body = f"Read and follow the agent description in ~/.agents/agents/{role}.md.\n"
        if not separator or body != expected_body:
            failures.append(f"variant body must contain only its canonical role reference: {filename}")
    if any("opencode/zen" in (config_agents / filename).read_text(errors="replace") for filename in expected_variants if (config_agents / filename).is_file()):
        failures.append("Zen model appears in work or personal specialist variants")
    principal_text = next(
        (content for path, content in policy_text.items() if path == Path(".agents/agents/principal.md")), ""
    )
    required_models = {
        "github-copilot/gpt-5.6-luna",
        "github-copilot/gpt-5.6-sol",
        "opencode/gpt-5.6-luna",
        "opencode/gpt-5.6-sol",
    }
    if "## Model selection" not in principal_text or not required_models.issubset(set(re.findall(r"`([^`]+)`", principal_text))):
        failures.append("principal model selection policy is incomplete")
    normalized_principal = re.sub(r"\s+", " ", principal_text).lower()
    for phrase in (
        "there are no opus variants",
        "requires explicit human permission before dispatch",
        "never dispatch a `--work-sol` or `--personal-sol` variant without explicit human permission",
        "including planning, execution, investigation, and independent review",
        "never dispatch an unlisted work variant",
        "never dispatch a work variant for personal work",
        "never dispatch an unlisted personal variant",
    ):
        if phrase.lower() not in normalized_principal:
            failures.append(f"principal model policy is missing: {phrase}")
    if re.search(r"(?:work|personal)-opus|claude-opus|gpt-5\.6-terra|deepseek-v4-flash|kimi-k2\.7-code", principal_text, re.IGNORECASE):
        failures.append("principal model policy still references a removed Opus or Terra variant")
    if "github-copilot/gpt-5.6-luna" not in (config_agents / "principal.md").read_text(errors="replace"):
        failures.append("staged principal agent must use github-copilot/gpt-5.6-luna")
    for path_name in (".agents/skills/run-feature/SKILL.md", ".agents/skills/run-task/SKILL.md"):
        content = policy_text.get(Path(path_name), "")
        if "principal's Model selection policy" not in content:
            failures.append(f"{path_name} does not require principal model selection for dispatch")
    for path_name in _SHARED_WORKTREE_SKILLS:
        path = Path(path_name)
        if path not in policy_text:
            failures.append(f"missing shared worktree skill: {path_name}")
            continue
        normalized_content = re.sub(r"\s+", " ", policy_text[path]).lower()
        for requirement in _SHARED_SKILL_CONTRACTS[path_name]:
            if requirement.lower() not in normalized_content:
                failures.append(f"{path_name} missing shared worktree contract: {requirement}")
    for path_name, requirements in _LIFECYCLE_REQUIREMENTS.items():
        content = policy_text.get(Path(path_name), "")
        if not content:
            failures.append(f"missing lifecycle policy: {path_name}")
            continue
        normalized_content = re.sub(r"\s+", " ", content).lower()
        for requirement in requirements:
            if requirement.lower() not in normalized_content:
                failures.append(f"{path_name} missing lifecycle requirement: {requirement}")
        if _has_unsafe_mutation(content):
            failures.append(f"{path_name} permits silent Git mutation")
    dispatch_paths = {
        path: content
        for path, content in policy_text.items()
        if path.parts[:3] in {
            (".agents", "skills", "run-feature"),
            (".agents", "skills", "run-task"),
            (".agents", "skills", "run-hack"),
            (".agents", "skills", "run-bug-fix"),
            (".agents", "skills", "run-fix"),
            (".agents", "skills", "run-hotfix"),
        }
    }
    for path, content in dispatch_paths.items():
        if re.search(r"Dispatch an `(?:architect|engineer)-[a-z-]+` subagent", content):
            failures.append(f"unvaried specialist dispatch in {path}")
    for path_name in (
        ".agents/skills/run-bug-fix/SKILL.md",
        ".agents/skills/run-fix/SKILL.md",
        ".agents/skills/run-hotfix/SKILL.md",
    ):
        content = policy_text.get(Path(path_name), "")
        if re.search(r"Dispatch an `(?:engineer|architect)-[a-z-]+`(?: subagent)?", content):
            failures.append(f"unvaried specialist dispatch in {path_name}")
    bug_fix = policy_text.get(Path(".agents/skills/run-bug-fix/SKILL.md"), "")
    if "bug report" not in bug_fix.lower() or "implementation plan" not in bug_fix.lower():
        failures.append("run-bug-fix is missing bug-report to implementation-plan attachment")
    fix = policy_text.get(Path(".agents/skills/run-fix/SKILL.md"), "")
    normalized_fix = re.sub(r"\s+", " ", fix).lower()
    for phrase in ("fail closed", "artifact directory is ambiguous", "modify no artifact or code", "agent-worktree view"):
        if phrase.lower() not in normalized_fix:
            failures.append(f"run-fix is missing fail-closed attachment control: {phrase}")
    hotfix = policy_text.get(Path(".agents/skills/run-hotfix/SKILL.md"), "")
    if "do not add an engineer-planner handoff" not in hotfix.lower():
        failures.append("run-hotfix adds or fails to prohibit a planner handoff")
    normalized_hotfix = re.sub(r"\s+", " ", hotfix).lower()
    for phrase in ("principal-authored minimal plan", "one lightweight review"):
        if phrase.lower() not in normalized_hotfix:
            failures.append(f"run-hotfix is missing streamlined gate control: {phrase}")
    if (
        "no extra human gate" not in normalized_hotfix
        and "no additional human approval gate" not in normalized_hotfix
        and "no additional human gate" not in normalized_hotfix
        and "any additional human approval gate" not in normalized_hotfix
    ):
        failures.append("run-hotfix is missing streamlined gate control: no extra human gate")
    task = policy_text.get(Path(".agents/skills/run-task/SKILL.md"), "")
    required_task_controls = {
        "human approval": r"human\s+(?:approval|approv)",
        "final QA exactly once": r"final QA exactly once",
        "independent reviewer": r"(?:independent|model-specific).*reviewer",
        "diff-first": r"diff-first",
        "never pushes": r"never pushes",
    }
    for phrase, pattern in required_task_controls.items():
        if not re.search(pattern, task, re.IGNORECASE | re.DOTALL):
            failures.append(f"run-task missing required control: {phrase}")
    for path_name in _TEMPORARY_BRANCH_WORKFLOWS:
        content = policy_text.get(Path(path_name), "")
        normalized_content = re.sub(r"\s+", " ", content).lower()
        for requirement in (
            "remove only the agent worktree",
            "locally indefinitely",
            "never delete it automatically",
            "only explicit human cleanup may delete",
        ):
            if requirement not in normalized_content:
                failures.append(f"{path_name} missing retained temporary branch policy: {requirement}")
        if re.search(r"git branch -[dD]\s+.*--agents", content, re.IGNORECASE):
            failures.append(f"{path_name} includes automatic temporary branch deletion")
        if "create-agent-worktree" not in content or "cleanup-agent-worktree" not in content:
            failures.append(f"{path_name} missing shared worktree reference")
        shared_references_removed = re.sub(r"`?(?:create|cleanup)-agent-worktree`?", "", content)
        if _DUPLICATE_WORKTREE_PLUMBING.search(shared_references_removed):
            failures.append(f"{path_name} includes duplicate worktree plumbing")
    for path_name in _BRANCH_WORKFLOWS:
        content = policy_text.get(Path(path_name), "")
        normalized_content = re.sub(r"\s+", " ", content).lower()
        for requirement in _BRANCH_CONTRACT:
            if requirement.lower() not in normalized_content:
                failures.append(f"{path_name} missing branch contract: {requirement}")
        if re.search(r"^(?!.*never use).*\bgit switch\b", content, re.IGNORECASE | re.MULTILINE):
            failures.append(f"{path_name} permits git switch outside its human-worktree prohibition")
        if re.search(r"\bgit push\b|\bgh pr (?:create|edit)\b", content, re.IGNORECASE):
            failures.append(f"{path_name} includes publication mechanics")
        if not _ORDERED_MAIN_INTEGRATION.search(content):
            failures.append(f"{path_name} lacks ordered approval, rebase, and fast-forward main integration")
    run_pr = policy_text.get(Path(".agents/skills/run-pr/SKILL.md"), "")
    for requirement in (
        "explicitly invokes `run-pr`",
        "Reject `main`, `master`, and any branch whose name contains `--agents`",
        "clean normal feature or task branch",
        "Confirm the authenticated `gh` account",
        "confirm the intended remote",
        "target base",
        "ambiguous, ask the human",
        "Never force-push.",
        "Push the normal branch",
        "gh pr create",
        "Return the pull request URL.",
    ):
        if requirement.lower() not in re.sub(r"\s+", " ", run_pr).lower():
            failures.append(f"run-pr missing required control: {requirement}")
    review_pr = policy_text.get(Path(".agents/skills/review-pr/SKILL.md"), "")
    if re.search(r"\bgit push\b", review_pr, re.IGNORECASE):
        failures.append("review-pr includes a push command")
    if "direct the user to run-pr" not in review_pr.lower():
        failures.append("review-pr does not direct publication to run-pr")
    review_setup = ("Perform all comment triage artifacts, fixes, commits, and QA in `{agent-worktree}`",)
    for requirement in review_setup:
        if requirement.lower() not in re.sub(r"\s+", " ", review_pr).lower():
            failures.append(f"review-pr missing worktree setup control: {requirement}")
    hack = policy_text.get(Path(".agents/skills/run-hack/SKILL.md"), "")
    if not re.search(r"^name:\s*run-hack\s*$", hack, re.MULTILINE) or not re.search(r"^description:\s*.+", hack, re.MULTILINE):
        failures.append("run-hack frontmatter identity is incorrect")
    for phrase in ("only one artifact", "never creates or switches branches", "never commits", "never pushes", "never creates a PR"):
        if phrase.lower() not in hack.lower():
            failures.append(f"run-hack missing prohibition: {phrase}")
    ownership_text = f"{principal_text}\n{text}"
    role_evidence = "orchestrator" in principal_text.lower() and re.search(r"\b(?:risk|escalat)", text, re.I)
    if not _PRINCIPAL_OWNERSHIP.search(ownership_text) and not role_evidence:
        failures.append("missing principal ownership of risk or escalation")
    promotion = manifest.get("promotion", {})
    if not promotion.get("approval_required") or not promotion.get("atomic_replacement") or not promotion.get("rollback_required") or not promotion.get("restart_required"):
        failures.append("promotion manifest lacks approval, atomic replacement, rollback, or restart requirements")
    return failures


def main() -> int:
    """Validate command-line staging arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--staging-root", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    args = parser.parse_args()
    failures = validate(args.staging_root, args.manifest)
    if failures:
        for failure in failures:
            print(f"ERROR: {failure}")
        return 1
    print(f"Validated complete staged policy set: {args.staging_root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
