import sys
from contextlib import contextmanager

from loguru import logger
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
from rich.live import Live
from rich.tree import Tree
from rich.panel import Panel

live: Live | None = None
progress_tree: Tree = Tree("Tasks")
branch_stack: list[Tree] = [progress_tree]

@contextmanager
def spinner(text: str):
    global live
    global progress_tree
    if live is None:
        live = Live(progress_tree)
    #progress = Progress(SpinnerColumn(), BarColumn(), TextColumn("[progress.description]{task.description}"), transient=True)
    #branch_stack.append(branch_stack[-1].add(Panel.fit(progress)))
    #branch_stack.append(branch_stack[-1].add(Panel.fit("FUCK")))
    progress_tree = progress_tree.add(Panel("Fuck!"))
    live.update(progress_tree)
    yield
    # branch_stack.pop()
    # branch_stack[-1].children = []
    # if len(branch_stack) == 1:
    #     live = None


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
