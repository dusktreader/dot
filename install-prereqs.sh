#!/usr/bin/env bash

set -e

sudo grep $USER /etc/sudoers > /dev/null 2>&1
if (( $? ))
then
    echo "Making passwordless sudo"
    echo "$USER ALL=(ALL) NOPASSWD: ALL" | (sudo su -c 'EDITOR="tee" visudo')
fi


pyenv_root=$HOME/.pyenv
if [[ -e $pyenv_root ]]
then
    echo "pyenv is already installed. Skipping"
else
    echo "Installing needed libs"
    sudo apt-get update -y
    sudo apt-get install -y make build-essential libssl-dev zlib1g-dev \
    libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm \
    libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev

    echo "Installing pyenv"
    curl https://pyenv.run | bash

    export PYENV_ROOT="$HOME/.pyenv"
    export PATH="$PYENV_ROOT/bin:$PATH"
    eval "$(pyenv init --path)"
fi

echo "Installing python 3.6.12 via pyenv"
pyenv install 3.6.15

echo "Installing python 3.8.12 via pyenv"
pyenv install 3.8.12

echo "Setting python 3.8.12 as default"
pyenv global 3.8.12


if [[ -e $HOME/.config/pypoetry ]]
then
    debug_out "poetry is already installed. Skipping"
else
    echo "Installing poetry"
    curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -
    source $HOME/.poetry/env
fi

echo "Setting up neovim"
sudo apt install neovim
