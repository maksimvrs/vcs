import click

from vcs.local_interface import LocalInterface


@click.group()
def main():
    """Version Control System"""
    pass


@main.command()
def init():
    """Initialize the repository"""
    LocalInterface.init()


@main.command()
@click.argument('files', nargs=-1, type=click.Path())
def add(files):
    """Add files to be indexed"""
    for file in files:
        LocalInterface.add(file)


@main.command()
@click.option('--message', '-m', help='Commit message')
def commit(message):
    """Commit files"""
    LocalInterface.commit('User', message)


@main.command()
@click.argument('commit')
def reset(commit_sha):
    """Reset last commit"""
    LocalInterface.reset(commit_sha)


if __name__ == '__main__':
    main()
