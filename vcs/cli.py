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
        click.echo('Error: ' + str(e))


@main.command()
@click.argument('files', nargs=-1, type=click.Path())
def add(files):
    """Add files to be indexed"""
    try:
        for file in files:
            Client.add(file)
    except CustomException as e:
        click.echo('Error: ' + str(e))


@main.command()
@click.option('--message', '-m', help='Commit message')
@click.option('--tag', '-t', help='Tag')
def commit(message, tag):
    """Commit files"""
    try:
        click.echo(Client.commit('User', message, tag))
    except CustomException as e:
        click.echo('Error: ' + str(e))


@main.command()
@click.argument('commit_sha', nargs=1, type=click.STRING)
def reset(commit_sha):
    """Reset last commit"""
    try:
        Client.reset(commit_sha)
    except CustomException as e:
        click.echo('Error: ' + str(e))


@main.command()
@click.argument('name', nargs=1, type=click.STRING)
def branch(name):
    """Create new branch"""
    try:
        Client.branch(name)
    except CustomException as e:
        click.echo('Error: ' + str(e))


@main.command()
@click.argument('branch', nargs=1, type=click.STRING)
def checkout(branch):
    """Switch to branch"""
    try:
        Client.checkout(branch)
    except CustomException as e:
        click.echo('Error: ' + str(e))


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
        click.echo('Error: ' + str(e))


@main.command()
@click.argument('branch', nargs=1, type=click.STRING)
def merge(branch):
    """Merge branch to current"""
    try:
        Client.merge(branch, choise_merge)
    except CustomException as e:
        click.echo('Error: ' + str(e))


@main.command()
@click.argument('branch', nargs=1, type=click.STRING)
def rebase(branch):
    """Rebase branch to current"""
    try:
        Client.rebase(branch, choise_merge)
    except CustomException as e:
        click.echo('Error: ' + str(e))


@main.command()
@click.argument('branch', nargs=1, type=click.STRING)
@click.argument('commit', nargs=1, type=click.STRING)
def cherry_pick(branch, commit):
    """Cherry-pick commit from branch to current"""
    try:
        Client.cherry_pick(branch, commit, choise_merge)
    except CustomException as e:
        click.echo('Error: ' + str(e))


def choise_merge(original, first, second):
    """
    :original: (branch name, value)
    :first: (branch name, value)
    :second: (branch name, value)
    :return: 0 - original, 1 - first, 2 - second
    """
    click.echo('Original version ' + original[0] + '(0):')
    click.echo('-----------------')
    click.echo(original[1])
    click.echo('-----------------')
    click.echo('First version ' + first[0] + '(1):')
    click.echo('-----------------')
    click.echo(first[1])
    click.echo('-----------------')
    click.echo('Second version ' + second[0] + '(2):')
    click.echo('-----------------')
    click.echo(second[1])
    click.echo('-----------------')
    answer = None
    while not (answer == 0 or answer == 1 or answer == 2):
        answer = click.prompt('Enter version number (0/1/2)', default=1)
    return answer
