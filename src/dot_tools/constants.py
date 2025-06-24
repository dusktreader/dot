from enum import Enum


class Status(Enum):
    CHECK = ("", "yellow")
    CONFIRM = ("", "green")
    FAIL = ("", "red")
    MISSING = ("", "magenta")

