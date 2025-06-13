import sys
from contextlib import contextmanager

from loguru import logger
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.live import Live
from rich.tree import Tree
from rich.panel import Panel

branch_stack: list[Tree] = []

@contextmanager
def spinner(text: str):
    progress = Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"))
    progress.add_task(text)

    live: Live | None = None
    if len(branch_stack) == 0:
        root_tree = Tree(progress)
        branch_stack.append(root_tree)
        live = Live(Panel(root_tree), transient=True)
        live.start()
    else:
        branch_stack.append(branch_stack[-1].add(progress))

    yield

    branch_stack.pop()
    if len(branch_stack) > 0:
        branch_stack[-1].children = []
    if live:
        live.stop()


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
            # TODO: would be fun to include a time elapsed here
