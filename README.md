USC AUV Tools
=============

This is a collection of command-line tools for USC AUV.

Installation
============

First install `pip`. Instructions vary per platform, but shouldn't be difficult
```
git clone git@github.com:uscauv/tools.git
./install.sh
```

Uninstallation
--------------
Remove references to this directory's `env_setup.sh` script from your ~/.bashrc, ~/.bash_profile and ~/.zshrc

Repo Tool
=========
The `repo` tool is a utility developed for managing multiple git repos as part of a larger project. It is inspired by Google's "repo" tool used in the Android Open Source Project.

Usage
-----

`repo init uscauv/manifest` will download the repo manifest, and clone all of the referenced projects.

`repo status` will show you the status of your working copy of each project similar to `git status`.

`repo sync` will pull changes from the remote repositories into your local copies.

`repo push` will push any committed changes for all repos. This is equivalent to running `git push` in each repo.

Manifest details
----------------
The manifest is a special GitHub repo containing metadata about all of the projects. For more information visit the [manifest project](https://github.com/uscauv/manifest).
