import click

from dot_tools.git_tools import GitManager
from dot_tools.misc_tools import setup_logging


@click.command()
def main():
    """
    Get the name of the current branch
    """
    git_man = GitManager()

    print(git_man.current_branch)


if __name__ == '__main__':
    main()
