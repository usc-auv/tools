#!/usr/bin/env python

import sys
import subprocess
import os
import json

def git(*args):
  return subprocess.check_call(['git'] + list(args))

opt = sys.argv[1].lower()

if opt == 'init':
  if os.path.isdir('.manifest'):
    print("Error: repo is already instantiated here.")
    exit()
  manifest_repo = sys.argv[2]
  git('clone', manifest_repo, '.manifest')
  with open('.manifest/manifest.json') as json_file:
    data = json.load(json_file)
    for project in data['projects']:
      git('clone', data['fetch'] + project['name'], project['path'])

if opt == 'sync':
  print('Checking for updates to manifest')
  os.chdir('.manifest')
  git('pull')
  os.chdir('..')
  for dirname in os.listdir('.'):
    if not dirname.startswith('.') and os.path.isdir(dirname):
      os.chdir(dirname)
      print(dirname)
      git('pull')

if opt == 'push':
  for dirname in os.listdir('.'):
    if not dirname.startswith('.') and os.path.isdir(dirname):
      os.chdir(dirname)
      print(dirname)
      git('push')
