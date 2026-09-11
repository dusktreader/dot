"""Validate an isolated staged agent-policy tree and shared routing inventory."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

_ZEN_DISPATCH = re.compile(
    r"^(?!.*\b(?:do not|don't|not)\b.*(?:opencode/zen|zen)).*(?:work-project|profile:work).*(?:opencode/zen|zen).*$",
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
_CAPABILITIES = {"coding", "analysis", "tools", "large-context"}
_TIERS = {"light", "standard", "premium"}
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
    ".agents/skills/run-hack/SKILL.md": ("current branch", "no worktree", "no Git lifecycle", "only one artifact"),
    ".agents/skills/run-bug-fix/SKILL.md": (
        "agent worktree",
        "agent branch",
        "before investigation",
        "shared `engineer-investigator` role",
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
        "shared `engineer-executor` role",
        "exclusive squash integration",
        "stale parent",
        "locally indefinitely",
    ),
    ".agents/skills/run-hotfix/SKILL.md": (
        "agent worktree",
        "agent branch",
        "before investigation",
        "shared `engineer-investigator` role",
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
    r"\b(?:silently|automatically|without explicit (?:human )?(?:approval|decision))\b.{0,80}\b(?:rebase|merge|discard|overwrite)\b",
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
_MODEL_SPECIFIC_DISPATCH = re.compile(
    r"model-specific|(?:architect|engineer)-[a-z-]+--(?:work|personal)-|\{work\|personal\}",
    re.IGNORECASE,
)


def _has_unsafe_mutation(text: str) -> bool:
    """Return whether text permits an unqualified Git mutation."""
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
    listed = {Path(item["staged_path"]) for item in manifest.get("files", [])}
    actual = {
        path.relative_to(staging_root)
        for directory in (staging_root / ".agents", staging_root / ".config/opencode/agents")
        for path in directory.rglob("*")
        if path.is_file()
    }
    if listed != actual:
        failures.append(f"manifest inventory mismatch: missing={sorted(listed - actual)}, extra={sorted(actual - listed)}")
    for item in manifest.get("files", []):
        path = staging_root / item["staged_path"]
        if path.is_file() and item.get("sha256") != hashlib.sha256(path.read_bytes()).hexdigest():
            failures.append(f"manifest checksum mismatch: {item['staged_path']}")

    policy_text = {
        path: (staging_root / path).read_text(errors="replace")
        for path in actual
        if path.suffix in {".md", ".txt"}
    }
    text = "\n".join(policy_text.values())
    if re.search(r"\brun-implementation\b", text):
        failures.append("stale run-implementation workflow reference")
    dispatch_text = "\n".join(content for path, content in policy_text.items() if path.parts[:2] == (".agents", "agents"))
    if _ZEN_DISPATCH.search(dispatch_text):
        failures.append("Zen model appears in work-project dispatch policy")

    config_agents = staging_root / ".config/opencode/agents"
    actual_roles = {path.stem for path in config_agents.glob("*.md")}
    missing_roles = sorted(set(_SPECIALIST_ROLES) - actual_roles)
    extra_variants = sorted(role for role in actual_roles if "--" in role)
    if missing_roles:
        failures.append(f"missing shared specialist agents: {missing_roles}")
    if extra_variants:
        failures.append(f"profile-specific specialist agents are forbidden: {extra_variants}")
    for role in _SPECIALIST_ROLES:
        path = config_agents / f"{role}.md"
        if not path.is_file():
            continue
        content = path.read_text()
        if f"name: {role}" not in content or "mode: subagent" not in content:
            failures.append(f"shared role frontmatter is incorrect: {role}")
        expected_prompt = f'prompt: "{{file:~/.agents/agents/{role}.md}}"'
        if expected_prompt not in content:
            failures.append(f"shared role prompt is incorrect: {role}")

    principal_text = policy_text.get(Path(".agents/agents/principal.md"), "")
    normalized_principal = re.sub(r"\s+", " ", principal_text).lower()
    for phrase in ("## model selection", "standard", "tier:premium", "explicit human permission", "work profile", "personal profile"):
        if phrase not in normalized_principal:
            failures.append(f"principal model policy is missing: {phrase}")
    for phrase in ("principal", "profile", "tier", "explicit human permission", "premium"):
        if phrase not in normalized_principal:
            failures.append(f"principal policy is missing routing ownership: {phrase}")
    if not _PRINCIPAL_OWNERSHIP.search(principal_text):
        failures.append("missing principal ownership of risk or escalation")
    for phrase in ("profile:work", "profile:personal", "never select a personal profile for work", "never select a work profile for personal"):
        if phrase not in normalized_principal:
            failures.append(f"principal policy is missing profile boundary: {phrase}")
    if "opencode/zen" in principal_text.lower() and "work" in principal_text.lower() and "never" not in normalized_principal:
        failures.append("principal policy permits Zen for work")
    if _MODEL_SPECIFIC_DISPATCH.search(principal_text):
        failures.append("principal policy contains model-specific dispatch names")
    staged_principal = (config_agents / "principal.md").read_text(errors="replace")
    if 'prompt: "{file:~/.agents/agents/principal.md}"' not in staged_principal:
        failures.append("staged principal agent must use the shared principal prompt")
    if re.search(r"(?:work|personal)-opus|claude-opus|gpt-5\.6-terra|deepseek-v4-flash|kimi-k2\.7-code", principal_text, re.IGNORECASE):
        failures.append("principal model policy still references a removed model variant")

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

    for path_name in _SHARED_WORKTREE_SKILLS:
        path = Path(path_name)
        if path not in policy_text:
            failures.append(f"missing shared worktree skill: {path_name}")
            continue
        normalized_content = re.sub(r"\s+", " ", policy_text[path]).lower()
        for requirement in _SHARED_SKILL_CONTRACTS[path_name]:
            if requirement.lower() not in normalized_content:
                failures.append(f"{path_name} missing shared worktree contract: {requirement}")

    dispatch_paths = {
        path: content
        for path, content in policy_text.items()
        if path.parts[:3] in {
            (".agents", "skills", "run-feature"),
            (".agents", "skills", "run-task"),
            (".agents", "skills", "run-bug-fix"),
            (".agents", "skills", "run-fix"),
            (".agents", "skills", "run-hotfix"),
            (".agents", "skills", "run-hack"),
        }
    }
    for path, content in dispatch_paths.items():
        if _MODEL_SPECIFIC_DISPATCH.search(content):
            failures.append(f"model-specific dispatch name in {path}")
        if not re.search(r"shared `(?:architect|engineer)-[a-z-]+` role", content):
            failures.append(f"{path} is missing the generic shared role dispatch contract")

    for path_name in (".agents/skills/run-feature/SKILL.md", ".agents/skills/run-task/SKILL.md"):
        content = policy_text.get(Path(path_name), "")
        if "principal's routing policy" not in content:
            failures.append(f"{path_name} does not require principal routing policy for dispatch")

    bug_fix = policy_text.get(Path(".agents/skills/run-bug-fix/SKILL.md"), "")
    if "bug report" not in bug_fix.lower() or "implementation plan" not in bug_fix.lower():
        failures.append("run-bug-fix is missing bug-report to implementation-plan attachment")
    fix = policy_text.get(Path(".agents/skills/run-fix/SKILL.md"), "")
    normalized_fix = re.sub(r"\s+", " ", fix).lower()
    for phrase in ("fail closed", "artifact directory is ambiguous", "modify no artifact or code", "agent-worktree view"):
        if phrase.lower() not in normalized_fix:
            failures.append(f"run-fix is missing fail-closed attachment control: {phrase}")
    hotfix = policy_text.get(Path(".agents/skills/run-hotfix/SKILL.md"), "")
    if "do not dispatch a planner subagent" not in hotfix.lower() and "do not add an engineer-planner handoff" not in hotfix.lower():
        failures.append("run-hotfix adds or fails to prohibit a planner handoff")
    normalized_hotfix = re.sub(r"\s+", " ", hotfix).lower()
    for phrase in ("principal-authored minimal plan", "one lightweight review"):
        if phrase.lower() not in normalized_hotfix:
            failures.append(f"run-hotfix is missing streamlined gate control: {phrase}")
    if (
        "no additional human approval gate" not in normalized_hotfix
        and "any additional human approval gate" not in normalized_hotfix
        and "no extra human gate" not in normalized_hotfix
    ):
        failures.append("run-hotfix is missing streamlined gate control: no extra human gate")

    task = policy_text.get(Path(".agents/skills/run-task/SKILL.md"), "")
    required_task_controls = {
        "human approval": r"human\s+(?:approval|approv)",
        "final QA exactly once": r"final QA exactly once",
        "independent reviewer": r"independent.*reviewer",
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
    review_setup = "Perform all comment triage artifacts, fixes, commits, and QA in `{agent-worktree}`"
    if review_setup.lower() not in re.sub(r"\s+", " ", review_pr).lower():
        failures.append(f"review-pr missing worktree setup control: {review_setup}")
    hack = policy_text.get(Path(".agents/skills/run-hack/SKILL.md"), "")
    if not re.search(r"^name:\s*run-hack\s*$", hack, re.MULTILINE) or not re.search(r"^description:\s*.+", hack, re.MULTILINE):
        failures.append("run-hack frontmatter identity is incorrect")
    for phrase in ("only one artifact", "never creates or switches branches", "never commits", "never pushes", "never creates a PR"):
        if phrase.lower() not in hack.lower():
            failures.append(f"run-hack missing prohibition: {phrase}")
    ownership_text = f"{principal_text}\n{text}"
    if not _PRINCIPAL_OWNERSHIP.search(ownership_text):
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
