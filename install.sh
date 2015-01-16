#!/bin/sh

BASEDIR=$(pwd)
echo "Installing AUV tools to the current directory: $BASEDIR"
echo "If you want to uninstall or move the tools, find the entry sourcing env_setup.sh in .bash_rc or .zsh_rc in this directory and remove it."

if [ -f ~/.bash_profile ];
then
   echo "Adding entry to ~/.bash_profile"
   echo "source $BASEDIR/env_setup.sh" >> ~/.bash_profile
fi

if [ -f ~/.bashrc ];
then
   echo "Adding entry to ~/.bashrc"
   echo "source $BASEDIR/env_setup.sh" >> ~/.bashrc
fi

if [ -f ~/.zshrc ];
then
   echo "Adding entry to ~/.zshrc"
   echo "source $BASEDIR/env_setup.sh" >> ~/.zshrc
fi

source ./env_setup.sh
