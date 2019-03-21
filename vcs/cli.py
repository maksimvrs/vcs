import click

from vcs.client import Client
from vcs.exceptions import CustomException


@click.group()
def main():
    """Version Control System"""
    pass


@main.command()
def init():
    """Initialize the repository"""
    try:
        Client.init()
    except CustomException as e:
        click.echo(e)


@main.command()
@click.argument('files', nargs=-1, type=click.Path())
def add(files):
    """Add files to be indexed"""
    try:
        for file in files:
            Client.add(file)
    except CustomException as e:
        click.echo(e)


@main.command()
@click.option('--message', '-m', help='Commit message')
@click.option('--tag', '-t', help='Tag')
def commit(message, tag):
    """Commit files"""
    try:
        click.echo(Client.commit('User', message, tag))
    except CustomException as e:
        click.echo(e)


@main.command()
@click.argument('commit_sha', nargs=1, type=click.STRING)
def reset(commit_sha):
    """Reset last commit"""
    try:
        Client.reset(commit_sha)
    except CustomException as e:
        click.echo(e)


@main.command()
def log():
    """Reset last commit"""
    try:
        for commit_log in Client.log():
            click.echo('-' * 30)
            click.echo('Commit: ' + commit_log[0])
            click.echo('Author: ' + commit_log[1])
            click.echo('Message: ' + commit_log[2])
            if commit_log[3] is not None:
                click.echo('Tag: ' + commit_log[3])
            click.echo('-' * 30)
    except CustomException as e:
        click.echo(e)
