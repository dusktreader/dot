from collections import deque
import sys
from contextlib import contextmanager
from typing import Any, override, TYPE_CHECKING

from loguru import logger
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.live import Live
from rich.tree import Tree
from rich.panel import Panel

from dot_tools.constants import Status

if TYPE_CHECKING:
    from loguru import Record, Message
else:
    Record = Any
    Message = Any

branch_stack: list[Tree] = []
logger_stack: list[int] = []

class ProgressLogger(Progress):

    messages: deque[str]

    def __init__(self, *args: Any, **kwargs: Any):
        self.messages = deque(maxlen=10)
        super().__init__(*args, **kwargs)

    @override
    def get_renderables(self):
        for r in super().get_renderables():
            yield r
        for line in self.messages:
            yield line

    def handler(self, message: Message):
        status: Status | None = message.record["extra"].get("status")
        stripped_message = message.strip()
        if status:
            (symbol, color) = status.value
            self.messages.append(f"[{color}]{symbol} {stripped_message}[/{color}]")
        else:
            self.messages.append(f"  {stripped_message}")


spin_logger: int | None = None

def filter_spin_log(record: Record) -> bool:
    return not record.get("extra", {}).get("spin", False)


@contextmanager
def spinner(text: str, context_level: str = "INFO"):
    progress = ProgressLogger(SpinnerColumn(), TextColumn("[progress.description]{task.description}"))
    progress.add_task(text)
    global spin_logger
    if spin_logger:
        logger.remove(spin_logger)

    spin_logger = logger.add(progress.handler, filter=filter_spin_log, format="{message}")

    live: Live | None = None
    if len(branch_stack) == 0:
        root_tree = Tree(progress)
        branch_stack.append(root_tree)
        live = Live(Panel(root_tree), transient=True)
        live.start()
    else:
        branch_stack.append(branch_stack[-1].add(progress))

    logger.log(context_level, f"Commenced: {text}", spin=True)
    try:
        yield
    except Exception as err:
        logger.error(f"Failed: {text} - {err}", exc_info=sys.exc_info(), spin=True)
        raise
    else:
        logger.log(context_level, f"Completed: {text}", spin=True)
        # TODO: would be fun to include a time elapsed here
    finally:
        logger.remove(spin_logger)
        spin_logger = None

    branch_stack.pop()
    if len(branch_stack) > 0:
        branch_stack[-1].children = []
    if live:
        live.stop()
