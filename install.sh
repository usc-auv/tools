#!/bin/sh

BASEDIR=$(pwd)
echo "Installing AUV tools to the current directory: $BASEDIR"
echo "If you want to uninstall or move the tools, find the entry sourcing env_setup.sh in .bash_rc or .zsh_rc in this directory and remove it."

if [ -f ~/.bash_profile ];
then
   echo "Adding entry to ~/.bash_profile"
   echo "source $BASEDIR/env_setup.sh \"$BASEDIR\"" >> ~/.bash_profile
fi

if [ -f ~/.bashrc ];
then
   echo "Adding entry to ~/.bashrc"
   echo "source $BASEDIR/env_setup.sh \"$BASEDIR\"" >> ~/.bashrc
fi

if [ -f ~/.zshrc ];
then
   echo "Adding entry to ~/.zshrc"
   echo "source $BASEDIR/env_setup.sh \"$BASEDIR\"" >> ~/.zshrc
fi

echo "Installing dependencies with pip and pip3"

pip3 install -r requirements.txt > /dev/null
pip install -r requirements.txt > /dev/null

source ./env_setup.sh
