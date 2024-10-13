#!/usr/bin/env bash

home=$(echo "$HOME" | sed 's:/*$::')
python_version="3.12"

sudo grep $USER /etc/sudoers > /dev/null 2>&1
if (( $? ))
then
    echo "Making passwordless sudo"
    echo "$USER ALL=(ALL) NOPASSWD: ALL" | (sudo su -c 'EDITOR="tee -a" visudo')
    if (( $? ))
    then
        echo "Failed to configure sudo! Aborting..."
        exit 1
    fi
fi

echo "Checking if uv is installed"
uv version > /dev/null 2>&1
if (( $? ))
then
    echo "Installing uv"
    curl -LsSf https://astral.sh/uv/install.sh | sh
    if (( $? ))
    then
        echo "Failed to install uv! Aborting..."
        exit 1
    fi
    source $home/.cargo/env
else
    echo "uv is already installed. Skipping"
    source $home/.cargo/env
fi

echo "Checking if python $python_version is installed"
uv python list | grep $python_version > /dev/null 2>&1
if (( $? ))
then
    echo "Installing python $python_version via uv"
    uv python install $python_version
    if (( $? ))
    then
        echo "Failed to install python $python_version! Aborting..."
        exit 1
    fi
else
    echo "python $python_version is already available through uv"
fi

echo "Checking if poetry is installed"
poetry --version > /dev/null 2>&1
if (( $? ))
then
    echo "Installing poetry"
    uv tool install poetry
    if (( $? ))
    then
        echo "Failed to install poetry! Aborting..."
        exit 1
    fi
    export PATH="$home/.local/bin:$PATH"
else
    echo "poetry is already installed. Skipping"
fi

echo "Checking if node is installed"
nvim --version > /dev/null 2>&1
if (( $? ))
then
    echo "Installing node, because it's needed by the coc plugin for neovim"
    curl -sL install-node.vercel.app/lts | sudo bash
    if (( $? ))
    then
        echo "Failed to install node! Aborting..."
        exit 1
    fi
else
    echo "node is already installed. Skipping"
fi

echo "Checking if nvim is installed"
nvim --version > /dev/null 2>&1
if (( $? ))
then
    echo "Setting up neovim"
    sudo snap install nvim --classic
    if (( $? ))
    then
        echo "Failed to install neovim! Aborting..."
        exit 1
    fi
else
    echo "nvim is already installed. Skipping"
fi

echo "Making parent directories for dot"
mkdir -p $home/git-repos/personal

if [[ ! -d "$home/git-repos/personal/dot" ]]
then
    echo "Cloning dot repository"
    git clone git@github.com:dusktreader/dot.git $home/git-repos/personal/dot
    if (( $? ))
    then
        echo "Failed to clone dot repository! Aborting..."
        exit 1
    fi
fi

now > /dev/null 2>&1
if (( $? ))
then
    echo "Installing dot via uv"
    uv tool install $home/git-repos/personal/dot --force --python=$python_version
    if (( $? ))
    then
        echo "Failed to clone dot repository! Aborting..."
        exit 1
    fi
fi

echo "Configuring dot"
configure-dot --root=$home/git-repos/personal/dot
if (( $? ))
then
    echo "Failed to configure dot! Aborting..."
    exit 1
fi
