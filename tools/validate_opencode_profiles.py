"""Validate tracked OpenCode profile and LiteLLM configuration shapes offline."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
import yaml

ALIASES = {"light", "standard", "premium"}
CAPABILITIES = {"coding", "analysis", "tools", "large-context"}
TIERS = {"light", "standard", "premium"}
PROFILES = {"personal": "profile:personal", "work": "profile:work"}
ROUTER_CONFIG_NAMES = {"personal": "personal", "work": "work"}
SECRET_PATTERN = re.compile(r"(?:sk-[A-Za-z0-9_-]{8,}|gh[pousr]_[A-Za-z0-9]{8,}|Bearer\s+[A-Za-z0-9._-]{8,})")


def _validate_profile(root: Path, profile: str) -> list[str]:
    failures: list[str] = []
    router_path = root / ".config/litellm" / f"{ROUTER_CONFIG_NAMES[profile]}.yaml"
    overlay_path = root / ".config/opencode/profiles" / f"{profile}.json"
    if not router_path.is_file():
        return [f"{profile}: missing router configuration {router_path}"]
    if not overlay_path.is_file():
        return [f"{profile}: missing OpenCode overlay {overlay_path}"]

    router = yaml.safe_load(router_path.read_text()) or {}
    overlay = json.loads(overlay_path.read_text())
    models = router.get("model_list", [])
    model_names = {item.get("model_name") for item in models if isinstance(item, dict)}
    if not ALIASES.issubset(model_names):
        failures.append(f"{profile}: missing logical aliases {sorted(ALIASES - model_names)}")
    if profile == "personal" and "personal-light-zen" not in model_names:
        failures.append("personal: missing approved Zen light fallback deployment")
    settings = router.get("router_settings", {})
    if settings.get("enable_tag_filtering") is not True or settings.get("tag_filtering_match_any") is not False:
        failures.append(f"{profile}: routing must require all capability, tier, and profile tags")
    if settings.get("tag_routing_prefix") != "route:":
        failures.append(f"{profile}: missing explicit route tag prefix")
    for item in models:
        params = item.get("litellm_params", {})
        tags = set(params.get("tags", []))
        if PROFILES[profile] not in tags:
            failures.append(f"{profile}: model {item.get('model_name')} lacks {PROFILES[profile]}")
        if not any(tag.startswith("tier:") for tag in tags):
            failures.append(f"{profile}: model {item.get('model_name')} lacks a tier tag")
        invalid_tiers = {tag.removeprefix("tier:") for tag in tags if tag.startswith("tier:")} - TIERS
        if invalid_tiers:
            failures.append(f"{profile}: model {item.get('model_name')} has invalid tiers {sorted(invalid_tiers)}")
        invalid_capabilities = {
            tag.removeprefix("capability:") for tag in tags if tag.startswith("capability:")
        } - CAPABILITIES
        if invalid_capabilities:
            failures.append(
                f"{profile}: model {item.get('model_name')} has invalid capabilities {sorted(invalid_capabilities)}"
            )
        if SECRET_PATTERN.search(json.dumps(item)):
            failures.append(f"{profile}: embedded credential in model configuration")
    if profile == "work":
        text = router_path.read_text().lower()
        if "opencode/" in text or "zen" in text:
            failures.append("work: Zen or OpenCode upstream appears in work router")
        if "fallbacks:" in text:
            failures.append("work: work router must not configure fallbacks")
    provider = overlay.get("provider", {}).get(profile, {})
    if provider.get("options", {}).get("baseURL") != "{env:OPENCODE_ROUTER_ENDPOINT}":
        failures.append(f"{profile}: overlay must use launcher-provided router endpoint")
    if SECRET_PATTERN.search(router_path.read_text()) or SECRET_PATTERN.search(overlay_path.read_text()):
        failures.append(f"{profile}: tracked configuration contains a credential-looking value")
    return failures


def validate(personal_root: Path, work_root: Path | None) -> list[str]:
    """Return configuration failures without starting a router or contacting a provider."""
    failures = _validate_profile(personal_root, "personal")
    if work_root is not None and work_root.is_dir():
        failures.extend(_validate_profile(work_root, "work"))
    return failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--personal-root", type=Path, required=True)
    parser.add_argument("--work-root", type=Path, required=True)
    args = parser.parse_args()
    failures = validate(args.personal_root, args.work_root)
    if failures:
        for failure in failures:
            print(f"ERROR: {failure}")
        return 1
    print("Validated personal and optional work OpenCode profiles")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
