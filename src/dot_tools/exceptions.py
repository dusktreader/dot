from typing import Any
from typerdrive import TyperdriveError


class DotError(TyperdriveError):
    @classmethod
    def die(cls, *format_args: Any, message: str = "DIED", **format_kwargs: Any):
        raise cls(message, *format_args, **format_kwargs)


class GitError(DotError):
    pass


class JiraError(DotError):
    pass
