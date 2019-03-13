import click

from vcs.client import Client


@click.group()
def main():
    """Version Control System"""
    pass


@main.command()
def init():
    """Initialize the repository"""
    Client.init()


@main.command()
@click.argument('files', nargs=-1, type=click.Path())
def add(files):
    """Add files to be indexed"""
    for file in files:
        Client.add(file)


@main.command()
@click.option('--message', '-m', help='Commit message')
def commit(message):
    """Commit files"""
    click.echo(Client.commit('User', message))


@main.command()
@click.argument('commit_sha', nargs=1, type=click.STRING)
def reset(commit_sha):
    """Reset last commit"""
    Client.reset(commit_sha)
