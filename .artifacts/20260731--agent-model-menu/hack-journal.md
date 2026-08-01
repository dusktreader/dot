# Trim agent model menus

Record the low-risk policy change that removes premium review variants and requires human approval before Sol.


## Change

- Removed all work Opus specialist variants.
- Kept work Luna for normal planning, execution, and investigation.
- Kept work Sonnet only for reviews.
- Kept Sol variants only as explicit human-approved premium escalations.
- Mirrored the work menu for personal work using OpenCode models, with GLM-5 for reviews.
- Removed Terra from the staged-policy validator's approved menus.


## Files changed

- `.agents/agents/principal.md`
- `.config/opencode/agents/`
- `tools/validate_staged_agent_policies.py`
- `tests/test_validate_staged_agent_policies.py`


## Verification

- `uv run pytest tests/test_validate_staged_agent_policies.py --no-cov`: 74 passed.
- `uv run ruff check tools/validate_staged_agent_policies.py tests/test_validate_staged_agent_policies.py`: passed.
- `node ~/.agents/tools/check-markdown-format.mjs .agents/agents/principal.md`: passed.
- `git diff --check`: passed.
