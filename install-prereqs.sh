#!/usr/bin/env bash

set -e

sudo grep $USER /etc/sudoers > /dev/null 2>&1
if (( $? ))
then
    echo "Making passwordless sudo"
    echo "$USER ALL=(ALL) NOPASSWD: ALL" | (sudo su -c 'EDITOR="tee" visudo')
fi


echo "Checking if pyenv is installed"
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

echo "Checking if uv is installed"
uv version > /dev/null 2>&1
if (( $? ))
then
    echo "Installing uv"
    curl -LsSf https://astral.sh/uv/install.sh | sh
else
    echo "uv is already installed. Skipping"
fi

echo "Checking if python 3.11 is installed"
pyenv versions | grep "3\.11" > /dev/null 2>&1
if (( $? ))
then
    echo "Installing python 3.11 via pyenv"
    pyenv install 3.11

    echo "Setting python 3.11 as default"
    pyenv global 3.11
else
    echo "python 3.11 is already available through pyenv"
fi


echo "Checking if poetry is installed"
if [[ -e $HOME/.config/pypoetry ]]
then
    echo "poetry is already installed. Skipping"
else
    echo "Installing poetry"
    curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -
    source $HOME/.poetry/env
fi

echo "Checking if nvim is installed"
nvim --version > /dev/null 2>&1
if (( $? ))
then
    echo "Setting up neovim"
    sudo snap install nvim --classic
else
    echo "nvim is already installed. Skipping"
fi
