"""Credentials management sub-commands for personal layer."""

from typing import Annotated, cast
import typer
from loguru import logger
from pydantic import SecretStr
from typerdrive import SettingsManager

from dot_tools.settings import Settings


cli = typer.Typer(help="Manage personal credentials via fetch and set", invoke_without_command=True)


def _is_placeholder_or_empty(value: str | SecretStr | None) -> bool:
    """Check if a value is empty or looks like a placeholder."""
    if isinstance(value, SecretStr):
        value = value.get_secret_value()
    if not value:
        return True
    return value.startswith("PLACEHOLDER_")


@cli.callback()
def main(ctx: typer.Context):
    """
    Manage personal credentials via fetch and set sub-commands.

    To retrieve a credential, use: dt creds fetch <key>
    To set a credential, use: dt creds set <key> <value>
    """
    # Show help on bare invocation and exit
    if ctx.invoked_subcommand is None:
        print(ctx.get_help())


@cli.command()
def fetch(
    key: Annotated[str, typer.Argument(help="Name of the credential to fetch")],
):
    """
    Fetch a personal secret value to stdout for scripting.

    WARNING: This prints a secret value to stdout. Callers must not log, echo,
    or otherwise capture this output without understanding the security implications.
    Use only in secure environments and scripts.
    """
    try:
        sm = SettingsManager(Settings)
        settings = cast(Settings, sm.settings_instance)
        
        # Access nested credentials sub-model
        if not hasattr(settings.credentials, key):
            print(f"error: credential '{key}' not found in personal settings", file=__import__("sys").stderr)
            raise typer.Exit(code=1)
        
        value = getattr(settings.credentials, key)
        
        # Validate the value
        if _is_placeholder_or_empty(value):
            print(f"error: credential '{key}' is empty or not configured", file=__import__("sys").stderr)
            raise typer.Exit(code=1)
        
        # Print to stdout with no surrounding text
        print(value.get_secret_value() if isinstance(value, SecretStr) else value)
        
    except Exception as e:
        if isinstance(e, typer.Exit):
            raise
        logger.error(f"Failed to fetch credential: {e}")
        print(f"error: {e}", file=__import__("sys").stderr)
        raise typer.Exit(code=1)


@cli.command()
def set(
    key: Annotated[str, typer.Argument(help="Name of the credential to set")],
    value: Annotated[str, typer.Argument(help="Value to set")],
):
    """
    Set a personal secret value in the settings store.

    WARNING: This command does not echo the value or any derivation to stdout
    or stderr on success, only a non-revealing acknowledgement. This allows
    operators to paste values interactively without worrying about terminal
    transcript leaks.
    """
    try:
        sm = SettingsManager(Settings)
        
        # Validate that the key exists in credentials sub-model
        credentials_fields = Settings.model_fields.get("credentials")
        if credentials_fields is None:
            raise ValueError("No credentials sub-model found in Settings")
        
        # Get the nested credentials model class
        creds_model = credentials_fields.annotation
        if not hasattr(creds_model, "model_fields"):
            raise ValueError("Credentials sub-model is not a Pydantic model")
        
        if key not in creds_model.model_fields:
            print(f"error: unknown credential key '{key}'", file=__import__("sys").stderr)
            raise typer.Exit(code=1)
        
        # Get current credentials and update the specific key
        current_creds = cast(Settings, sm.settings_instance).credentials
        updated_creds_dict = current_creds.model_dump(mode="json")
        updated_creds_dict[key] = value
        updated_creds = creds_model(**updated_creds_dict)
        
        # Update and save
        sm.update(credentials=updated_creds)
        sm.save()
        
        # Print non-revealing acknowledgement
        print(f"credential '{key}' updated")
        
    except typer.Exit:
        raise
    except Exception as e:
        logger.error(f"Failed to set credential: {e}")
        print(f"error: {e}", file=__import__("sys").stderr)
        raise typer.Exit(code=1)
