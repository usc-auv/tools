#!/usr/bin/env python

import json
import re
from os import path

import click
from git import *


@click.group()
def cli():
    pass


@click.command()
@click.argument('repo')
def init(repo):
    if path.isdir('.manifest'):
        click.echo("Error: repo is already instantiated here.")
        exit()

    # if this regex doesn't match, assume we are dealing with a github repo
    if not re.match('git@|https://|git://', repo):
        repo = 'git@github.com:' + repo + '.git'

    Repo.clone_from(repo, '.manifest')
    with open('.manifest/manifest.json') as json_file:
        data = json.load(json_file)
        for project in data['projects']:
            Repo.clone_from(data['fetch'] + project['name'], project['path'])
            if 'branch' in project:
                gitRepo = Repo(project['path'])
                gitRepo.heads[project['branch']].checkout()
            else:
                project['branch'] = 'master'
            click.echo('[' + project['name'] + '] ==> ' + project['branch'])


@click.command()
def sync():
    if not path.isdir('.manifest'):
        click.echo("Error: repo is not instantiated here.")
        exit()

    click.echo("Checking for updates to manifest...")
    manifest_repo = Repo('.manifest')
    manifest_repo.remotes.origin.pull()

    with open('.manifest/manifest.json') as json_file:
        data = json.load(json_file)
        for project in data['projects']:
            # if it doesn't exist already, clone it
            if not path.isdir(project['path']):
                click.echo("New project found: [" + project["name"] + ']')
                Repo.clone_from(data['fetch'] + project['name'], project['path'])
                if 'branch' in project:
                    repo = Repo(project['path'])
                    repo.heads[project['branch']].checkout()
                else:
                    project['branch'] = 'master'
                click.echo('[' + project['name'] + '] ==> ' + project['branch'])
            # it already exists, pull
            else:
                repo = Repo(project['path'])
                prev_commit = repo.head.reference.commit
                repo.remotes.origin.pull()
                new_commit = repo.head.reference.commit

                if new_commit != prev_commit:
                    click.echo('[' + project['name'] + ']  ' + prev_commit + " ==> " + new_commit)
                else:
                    click.echo('[' + project['name'] + '] already up-to-date.')


@click.command()
def push():
    with open('.manifest/manifest.json') as json_file:
        data = json.load(json_file)
        for project in data['projects']:
            repo = Repo(project['path'])
            commits_ahead = repo.iter_commits(repo.active_branch.name + '..origin/' + repo.active_branch.name)
            commits_behind = repo.iter_commits('origin/' + repo.active_branch.name + '..' + repo.active_branch.name)
            ahead_count = sum(1 for c in commits_ahead)
            behind_count = sum(1 for c in commits_behind)
            if ahead_count > 0 and behind_count == 0:
                click.echo("[" + project["name"] + "] ==> pushing " + ahead_count + " commits")
                repo.remotes.origin.push()
            if ahead_count == 0 and behind_count > 0:
                click.echo("[" + project["name"] + "] ==> behind by " + behind_count + " commits. Run sync first.")
            if ahead_count == 0 and behind_count == 0:
                click.echo("[" + project["name"] + "] ==> already up-to-date.")


@click.command()
def status():
    with open('.manifest/manifest.json') as json_file:
        data = json.load(json_file)
        for project in data['projects']:
            repo = Repo(project['path'])
            commits_ahead = repo.iter_commits(repo.active_branch.name + '..origin/' + repo.active_branch.name)
            commits_behind = repo.iter_commits('origin/' + repo.active_branch.name + '..' + repo.active_branch.name)
            ahead_count = sum(1 for c in commits_ahead)
            behind_count = sum(1 for c in commits_behind)
            if ahead_count > 0 and behind_count == 0:
                click.echo("[" + project["name"] + "] ==> ahead by " + ahead_count + " commits")
            if ahead_count == 0 and behind_count > 0:
                click.echo("[" + project["name"] + "] ==> behind by " + behind_count + " commits.")
            if repo.is_dirty() or len(repo.untracked_files) != 0:
                click.echo("[" + project["name"] + "] ==> there are unstaged changes or untracked files.")
            elif not repo.is_dirty():
                click.echo("[" + project["name"] + "] ==> no changes to commit.")


cli.add_command(init)
cli.add_command(sync)
cli.add_command(push)
cli.add_command(status)

if __name__ == '__main__':
    cli()