import os
from pathlib import Path

from typerdrive import SettingsManager

from dot_tools.settings import Settings


def dot_settings_manager() -> SettingsManager:
    state_home = os.environ.get("DOT_STATE_HOME")
    if not state_home:
        return SettingsManager(Settings)

    original_state_home = os.environ.get("XDG_STATE_HOME")
    os.environ["XDG_STATE_HOME"] = str(Path(state_home))
    try:
        return SettingsManager(Settings)
    finally:
        if original_state_home is None:
            os.environ.pop("XDG_STATE_HOME", None)
        else:
            os.environ["XDG_STATE_HOME"] = original_state_home
