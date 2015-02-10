#!/usr/bin/env python

import json
import re
from threading import Thread
from os import path

import click
from git import *


def message(project, message):
    click.echo(('[' + project + '] ').ljust(max_repo_len + 3, ' ') + '==> ' + message)


@click.group()
def cli():
    pass


def find_repo_dir(dir='.'):
    if path.isdir(dir + '/.manifest'):
        return path.abspath(dir)
    if path.realpath(dir) == '/':
        return None
    return find_repo_dir(path.abspath(dir + '/..'))


def manifest_file():
    repo_dir = find_repo_dir()
    if not repo_dir:
        return None
    return repo_dir + '/.manifest/manifest.json'


@click.command()
@click.argument('repo')
def init(repo):
    if find_repo_dir():
        click.echo("Error: repo is already installed here.")
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
            message(project['name'], project['branch'])


@click.command()
def sync():
    if not find_repo_dir():
        click.echo("Error: repo is not installed here.")
        exit()

    click.echo("Checking for updates to manifest...")
    manifest_repo = Repo(find_repo_dir() + "/.manifest")
    manifest_repo.remotes.origin.pull()

    with open(manifest_file()) as json_file:
        data = json.load(json_file)
        for project in data['projects']:
            # trailing comma indicates that it is a tuple, otherwise it treats project as multiple arguments
            thread = Thread(target=sync_repo, args=(project,))
            thread.start()


def sync_repo(project):
    # if it doesn't exist already, clone it
    if not path.isdir(find_repo_dir() + "/" + project['path']):
        Repo.clone_from(data['fetch'] + project['name'], find_repo_dir() + "/" + project['path'])
        if 'branch' in project:
            repo = Repo(find_repo_dir() + "/" + project['path'])
            repo.heads[project['branch']].checkout()
        else:
            project['branch'] = 'master'
        message(project['name'], project['branch'])
    # it already exists, pull
    else:
        repo = Repo(find_repo_dir() + "/" + project['path'])
        prev_commit = repo.head.reference.commit
        repo.remotes.origin.pull()
        new_commit = repo.head.reference.commit

        if new_commit != prev_commit:
            click.echo('[' + project['name'] + ']  ' + str(prev_commit)[:7] + " ==> " + str(new_commit)[:7])
        else:
            message(project['name'], "already up-to-date.")


@click.command()
def push():
    if not find_repo_dir():
        click.echo("Error: repo is not installed here.")
        exit()

    with open(manifest_file()) as json_file:
        data = json.load(json_file)
        for project in data['projects']:
            repo = Repo(find_repo_dir() + "/" + project['path'])
            commits_behind = repo.iter_commits(repo.active_branch.name + '..origin/' + repo.active_branch.name)
            commits_ahead = repo.iter_commits('origin/' + repo.active_branch.name + '..' + repo.active_branch.name)
            ahead_count = sum(1 for c in commits_ahead)
            behind_count = sum(1 for c in commits_behind)
            if ahead_count > 0 and behind_count == 0:
                message(project['name'], "pushing " + str(ahead_count) + " commits")
                repo.remotes.origin.push()
            if ahead_count == 0 and behind_count > 0:
                message(project['name'], "behind by " + str(behind_count) + " commits. Run sync first.")
            if ahead_count == 0 and behind_count == 0:
                message(project['name'], "already up-to-date.")


@click.command()
def status():
    if not find_repo_dir():
        click.echo("Error: repo is not installed here.")
        exit()

    with open(manifest_file()) as json_file:
        data = json.load(json_file)
        for project in data['projects']:
            repo = Repo(find_repo_dir() + "/" + project['path'])
            commits_behind = repo.iter_commits(repo.active_branch.name + '..origin/' + repo.active_branch.name)
            commits_ahead = repo.iter_commits('origin/' + repo.active_branch.name + '..' + repo.active_branch.name)
            ahead_count = sum(1 for c in commits_ahead)
            behind_count = sum(1 for c in commits_behind)
            if ahead_count > 0 and behind_count == 0:
                message(project['name'], "ahead by " + str(ahead_count) + " commits.")
            if ahead_count == 0 and behind_count > 0:
                message(project['name'], "behind by " + str(behind_count) + " commits.")
            if repo.is_dirty() or len(repo.untracked_files) != 0:
                message(project['name'], "there are unstaged changes or untracked files.")
            elif not repo.is_dirty():
                message(project['name'], "no changes to commit.")


cli.add_command(init)
cli.add_command(sync)
cli.add_command(push)
cli.add_command(status)

if __name__ == '__main__':
    # want to figure out the max repo name length to format properly
    max_repo_len = 0

    # don't crash if repo is not installed here
    if manifest_file():
        with open(manifest_file()) as json_file:
            data = json.load(json_file)
            for project in data['projects']:
                if len(project['name']) > max_repo_len:
                    max_repo_len = len(project['name'])

    cli()
