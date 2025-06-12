import sys
from contextlib import contextmanager

from loguru import logger
from rich.progress import Progress, SpinnerColumn, TextColumn


@contextmanager
def spinner(text: str):
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), transient=True) as progress:
        task = progress.add_task(description=f"{text}...", total=None)
        yield
        progress.update(task, completed=1.0)


@contextmanager
def report_block(text: str, context_level: str = "INFO"):
    with spinner(text):
        logger.log(context_level, f"Commenced: {text}")
        try:
            yield
        except Exception as err:
            logger.error(f"Failed: {text} - {err}", exc_info=sys.exc_info())
            raise
        else:
            logger.log(context_level, f"Completed: {text}")
