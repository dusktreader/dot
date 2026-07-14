# End-to-End Validation Guide

This guide provides a comprehensive validation checklist to ensure the two-repository split,
credential migration, and complete isolation between dot (personal) and work-dot (work) layers
is working correctly.

## Pre-Validation Setup

Before running validation, ensure both repositories are bootstrapped:

```shell
# Personal dot layer (should already be installed)
dt --version

# Work-dot layer
cd ~/src/mhe/work-dot
wdt --version
wdt configure  # First-time setup
```

## Validation Checklist

### 1. Credential Isolation ✓

**Objective**: Verify that personal and work credentials are completely separate and cannot
be accessed across layers.

```shell
# Set a personal credential
dt creds set test_personal_key
# (Enter: "personal_test_value" when prompted)

# Set a work credential
wdt creds set test_work_key
# (Enter: "work_test_value" when prompted)

# Verify isolation
dt creds fetch test_personal_key
# Expected: "personal_test_value"
dt creds fetch test_work_key
# Expected: Error (key not found in personal store)

wdt creds fetch test_work_key
# Expected: "work_test_value"
wdt creds fetch test_personal_key
# Expected: Error (key not found in work store)

# Check credential file locations (should be different)
ls -la ~/.config/typerdrive/dot_settings.json
ls -la ~/.config/typerdrive/work_settings.json
```

### 2. Git Configuration Isolation ✓

**Objective**: Verify that git config switches correctly based on repository location.

```shell
# In personal repo (~/.config/typerdrive/dot_settings.json)
cd ~/src/dusktreader/dot
git config user.email
# Expected: personal email (likely @dusktreader.dev or similar)
git config --local user.email
# Expected: (empty - using global)

# Check github user (should be "dusktreader" from main .gitconfig)
git config github.user
# Expected: dusktreader

# In work repo (should load .gitconfig.work)
cd ~/src/mhe/work-dot
git config user.email
# Expected: tucker.beck@mheducation.com

# Check github user (should be "Tucker-Beck_mcgraw" from .gitconfig.work)
git config github.user
# Expected: Tucker-Beck_mcgraw (or similar work-specific user)

# Verify includeIf is set in main .gitconfig
grep -A2 "includeIf.*mhe" ~/.gitconfig
# Expected:
# [includeIf "gitdir:~/src/mhe/"]
#     path = ~/.gitconfig.work
```

### 3. CLI Tool Isolation ✓

**Objective**: Verify that dt and wdt CLIs are independent and use correct settings.

```shell
# List available dt commands (personal layer)
dt --help | grep -E "creds|configure"
# Expected: Shows "creds" and "configure" commands

# List available wdt commands (work layer)
wdt --help | grep -E "creds|configure"
# Expected: Shows "creds" and "configure" commands

# Verify they use different settings
dt creds fetch jira_api_key
# Expected: Returns personal Jira key (or error if not set)

wdt creds fetch jira_api_key
# Expected: Returns work Jira key (different value or both set/both unset independently)
```

### 4. Bootstrap Installation ✓

**Objective**: Verify that wdt configure properly installs work configuration files.

```shell
# Clean slate test (optional - only if you want to test full bootstrap)
rm -rf ~/.workrc ~/.gitconfig.work

# Run wdt configure
wdt configure

# Verify files are installed
ls -la ~/.workrc
# Expected: File exists with work environment config

ls -la ~/.gitconfig.work
# Expected: File exists with MHE git config

# Verify .workrc contents
cat ~/.workrc | head -5
# Expected: Shows work environment exports and aliases
```

### 5. Output Prefixing ✓

**Objective**: Verify that wdt output in dt configure is properly prefixed with [work].

```shell
# Run dt configure with wdt invocation (if there are work-specific steps)
# This may require setup on your system - check dt configure --help

# Look for [work] prefix in any work-dot output
# Expected: If wdt is invoked during dt configure, output should have [work] prefix
```

### 6. Credential Seeding ✓

**Objective**: Verify that fresh wdt configure seeds credentials with placeholders.

```shell
# In a fresh setup (or check existing)
wdt configure 2>&1 | grep -i "placeholder\|secret"
# Expected: Shows notices about unseeded keys (e.g., "Secret 'jira_api_key' not set...")

# Check that placeholders exist
wdt creds fetch jira_api_key
# Expected: May return PLACEHOLDER_JIRA_API_KEY or the actual set value
```

### 7. Settings Schema ✓

**Objective**: Verify that Settings models are correct for both layers.

```shell
# Test dt Settings
python3 -c "
from dot_tools.settings import Settings, CredentialsModel
s = Settings()
print(f'Personal credentials fields: {list(s.credentials.model_fields.keys())}')
"

# Test wdt Settings
python3 -c "
import sys
sys.path.insert(0, '~/src/mhe/work-dot/src')
from work_tools.settings import WorkSettings, CredentialsModel
s = WorkSettings()
print(f'Work credentials fields: {list(s.credentials.model_fields.keys())}')
"
```

### 8. No Credential Leaks ✓

**Objective**: Ensure credentials never appear in logs, error messages, or committed files.

```shell
# Search for credential values in git history
cd ~/src/dusktreader/dot
git log --all --full-history -S "PLACEHOLDER_" 2>/dev/null | head -5
# Expected: No matches (placeholders should not be committed)

cd ~/src/mhe/work-dot
git log --all --full-history -S "PLACEHOLDER_" 2>/dev/null | head -5
# Expected: No matches

# Check .gitignore for credential files
grep "typerdrive\|settings.json" .gitignore
# Expected: Should have entries to ignore credential files
```

### 9. Error Handling ✓

**Objective**: Verify that error messages are helpful and don't leak information.

```shell
# Try to fetch a non-existent key
dt creds fetch nonexistent_key 2>&1
# Expected: Clean error message like "Credential 'nonexistent_key' not found"
# Expected: No stack traces or sensitive information

wdt creds fetch nonexistent_key 2>&1
# Expected: Same clean error format

# Try to set with invalid key name
dt creds set "invalid key with spaces" 2>&1
# Expected: Error explaining valid key formats
```

### 10. Documentation ✓

**Objective**: Verify that all documentation is present and accurate.

```shell
# Check for migration guide
ls -la .dot_agents/CREDENTIAL_MIGRATION.md
# Expected: File exists

# Check for work-dot agent instructions
ls -la ~/src/mhe/work-dot/.agents/instructions/work.md
# Expected: File exists

# Verify instructions reference dt/wdt creds (not old credentials.json)
grep -c "dt creds\|wdt creds" .dot_agents/CREDENTIAL_MIGRATION.md
# Expected: > 0 (multiple references)
```

## Validation Results

Run this script to perform all validation checks:

```bash
#!/bin/bash
set -e

echo "=== Validating Two-Layer Split ==="
echo ""

# Run each validation
echo "✓ Checking credential isolation..."
dt creds fetch 2>&1 | grep -q "fetch" || echo "  dt creds fetch working"

echo "✓ Checking git config isolation..."
(cd ~/src/mhe/work-dot && git config user.email | grep -q mheducation) && echo "  Work git config OK"

echo "✓ Checking CLI tools..."
dt --version > /dev/null && echo "  dt CLI OK"
wdt --version > /dev/null && echo "  wdt CLI OK"

echo "✓ Checking documentation..."
[[ -f ~/.dot_agents/CREDENTIAL_MIGRATION.md ]] && echo "  Migration guide exists"
[[ -f ~/src/mhe/work-dot/.agents/instructions/work.md ]] && echo "  Work instructions exist"

echo ""
echo "=== All validations passed! ==="
```

## Troubleshooting

### Credential Files Not Found

```shell
# Credentials should exist at:
~/.config/typerdrive/dot_settings.json      # Personal
~/.config/typerdrive/work_settings.json     # Work

# If missing, they'll be created on first dt/wdt creds set command
```

### Git Config Not Switching

```shell
# Verify includeIf is in main .gitconfig
grep -n "includeIf" ~/.gitconfig

# Verify both config files exist
test -f ~/.gitconfig.dusktreader && echo "Personal config exists"
test -f ~/.gitconfig.work && echo "Work config exists"
```

### Settings Import Errors

```shell
# Verify Python path and imports
cd ~/src/dusktreader/dot && python3 -c "from dot_tools.settings import Settings; print('OK')"
cd ~/src/mhe/work-dot && python3 -c "from work_tools.settings import WorkSettings; print('OK')"
```

## Post-Validation

Once all validations pass:

1. Delete legacy credentials file if using old system:
   ```shell
   rm ~/.agents/credentials.json
   ```

2. Update your shell initialization to ensure both CLIs are in PATH:
   ```shell
   export PATH="~/src/dusktreader/dot/.venv/bin:~/src/mhe/work-dot/.venv/bin:$PATH"
   ```

3. Start using `dt creds` and `wdt creds` for credential management going forward.
