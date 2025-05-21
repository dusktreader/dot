import tomllib
from pathlib import Path

from loguru import logger
from typerdrive import log_error

from dot_tools.exceptions import DotError

DEFAULT_LINE_LENGTH = 120


def find_pyproject_toml() -> Path | None:
    path = Path.cwd()
    logger.debug(f"Looking for pyproject.toml in {path}")
    while True:
        possible_path = path / "pyproject.toml"
        if possible_path.exists():
            logger.debug(f"Found pyproject.toml at {possible_path}")
            return possible_path
        if path == path.parent:
            logger.debug(f"Bottomed out at {path}. pyproject.toml not found")
            return None
        path = path.parent


def get_config_line_length() -> int:

    with DotError.handle_errors(
        "Failed to extract line length from config",
        re_raise=False,
        do_except=log_error,
    ):
        logger.debug("Finding pyproject.toml")
        pyproject_toml: Path | None = find_pyproject_toml()
        if pyproject_toml is None:
            logger.debug("No pyproject.toml found. Using default of {DEFAULT_LINE_LENGTH}")
            return DEFAULT_LINE_LENGTH

        logger.debug(f"Found at {pyproject_toml}")

        config = tomllib.loads(pyproject_toml.read_text())
        logger.debug("Extracted project config")

        tool_config = config["tool"]
        logger.debug(f"Tool config extracted as {tool_config}")

        logger.debug("Looking for ruff line length")
        ruff_config = tool_config.get("ruff")
        if ruff_config:
            logger.debug(f"Found and extracted ruff config as {ruff_config=}")
            line_length = ruff_config["line-length"]
            logger.debug(f"Line length extracted as {line_length}")
            return line_length

        logger.debug("Looking for black line length")
        black_config = tool_config.get("black")
        if black_config:
            logger.debug(f"Found and extracted black config as {black_config=}")
            line_length = black_config["line-length"]
            logger.debug(f"Line length extracted as {line_length}")
            return line_length

    logger.debug(f"No line length found in config. Using default of {DEFAULT_LINE_LENGTH}")
    return DEFAULT_LINE_LENGTH
