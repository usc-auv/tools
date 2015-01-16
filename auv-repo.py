#!/usr/bin/env python

import subprocess
import json
import re
import os

import click
from git import *


def git(*args):
    return subprocess.check_call(['git'] + list(args))


@click.group()
def cli():
    pass


@click.command()
@click.argument('repo')
def init(repo):
    if os.path.isdir('.manifest'):
        click.echo("Error: repo is already instantiated here.")
        exit()

    # if this regex doesn't match, assume we are dealing with a github repo
    if not re.match('git@|https://|git://', repo):
        repo = 'git@github.com:' + repo + '.git'

    git('clone', repo, '.manifest')
    with open('.manifest/manifest.json') as json_file:
        data = json.load(json_file)
        for project in data['projects']:
            git('clone', data['fetch'] + project['name'], project['path'])


@click.command()
def sync():
    if not os.path.isdir('.manifest'):
        click.echo("Error: repo is not instantiated here.")
        exit()

    click.echo('Checking for updates to manifest')
    os.chdir('.manifest')
    git('pull')
    os.chdir('..')
    for dirname in os.listdir('.'):
        if not dirname.startswith('.') and os.path.isdir(dirname):
            os.chdir(dirname)
            click.echo(dirname)
            git('pull')


@click.command()
def push():
    for dirname in os.listdir('.'):
        if not dirname.startswith('.') and os.path.isdir(dirname):
            os.chdir(dirname)
            click.echo(dirname)
            git('push')


cli.add_command(init)
cli.add_command(sync)
cli.add_command(push)

if __name__ == '__main__':
    cli()