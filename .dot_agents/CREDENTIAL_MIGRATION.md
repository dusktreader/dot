# Credential Migration Guide

This guide documents how to migrate from the legacy credential file approach to the new
`dt creds` and `wdt creds` command-line interface.

## Overview

Previously, credentials were stored in a single `~/.agents/credentials.json` file that
was shared across all contexts. The new system separates credentials into two independent
stores:

- **Personal credentials** (dot): Managed via `dt creds fetch/set`
- **Work credentials** (work-dot): Managed via `wdt creds fetch/set`

This separation ensures work and personal credentials never mix and can be managed
independently.

## Migration Steps

### Step 1: Identify Your Credentials

List all credentials currently in `~/.agents/credentials.json`:

```shell
cat ~/.agents/credentials.json | jq keys
```

Categorize them:
- **Personal**: Credentials used for personal projects (GitHub personal, personal APIs, etc.)
- **Work**: Credentials related to McGraw Hill (Jira API key, work GitHub account, etc.)

### Step 2: Migrate Personal Credentials

For each personal credential:

```shell
dt creds set <credential_name>
# Enter the value when prompted
```

Example:
```shell
dt creds set jira_api_key
# (paste personal Jira API key when prompted)
```

### Step 3: Migrate Work Credentials

Bootstrap work-dot first:

```shell
wdt configure
```

Then set work credentials:

```shell
wdt creds set <credential_name>
# Enter the value when prompted
```

Example:
```shell
wdt creds set jira_api_key
# (paste MHE Jira API key when prompted)
```

### Step 4: Verify Migration

Verify each credential can be retrieved:

```shell
# Personal
dt creds fetch jira_api_key

# Work
wdt creds fetch jira_api_key
```

Both should return the correct values without echoing to terminal.

### Step 5: Delete Legacy Credential File

Once all credentials have been migrated and verified:

```shell
rm ~/.agents/credentials.json
```

## Retrieving Credentials in Scripts

### Personal Context

In dot tools or scripts using dt CLI:

```bash
JIRA_KEY=$(dt creds fetch jira_api_key)
# Use $JIRA_KEY for personal Jira API calls
```

### Work Context

In work-dot tools or scripts using wdt CLI:

```bash
JIRA_KEY=$(wdt creds fetch jira_api_key)
# Use $JIRA_KEY for MHE Jira API calls
```

## Credential Storage

- **Personal credentials**: `~/.config/typerdrive/dot_settings.json`
- **Work credentials**: `~/.config/typerdrive/work_settings.json`

Both files are user-readable but should not be committed to version control.
Add them to `.gitignore` if you're syncing configuration:

```
# .gitignore
~/.config/typerdrive/dot_settings.json
~/.config/typerdrive/work_settings.json
```

## Troubleshooting

### Credential Not Found

If `dt creds fetch <key>` or `wdt creds fetch <key>` returns an error:

1. Verify the credential exists:
   ```shell
   dt creds fetch <key>  # Check personal store
   wdt creds fetch <key> # Check work store
   ```

2. If it's truly missing, set it:
   ```shell
   dt creds set <key>
   ```

### Settings File Corruption

If either settings file becomes corrupted, delete it and reconfigure:

```shell
# For personal
rm ~/.config/typerdrive/dot_settings.json
dt creds set jira_api_key
# (re-set all personal credentials)

# For work
rm ~/.config/typerdrive/work_settings.json
wdt creds set jira_api_key
# (re-set all work credentials)
```

## Environment Setup

After migration, ensure your shell initialization loads the appropriate CLI tool
for each context:

### For dt (personal):
```shell
# Assuming dot is in ~/src/dusktreader/dot
export PATH="~/src/dusktreader/dot/.venv/bin:$PATH"
```

### For wdt (work):
```shell
# Assuming work-dot is in ~/src/mhe/work-dot
export PATH="~/src/mhe/work-dot/.venv/bin:$PATH"
```

Or add both to your shell profile's PATH initialization.
