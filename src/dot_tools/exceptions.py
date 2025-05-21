from typerdrive import TyperdriveError


class DotError(TyperdriveError):
    pass


class GitError(DotError):
    pass


class JiraError(DotError):
    pass
