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

echo "Checking if oh-my-posh is installed"
if (( $? ))
then
    echo "Installing oh-my-posh"
    curl -s https://ohmyposh.dev/install.sh | bash -s
    if (( $? ))
    then
        echo "Failed to install oh-my-posh! Aborting..."
        exit 1
    fi
else
    echo "oh-my-posh is already installed. Skipping"
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
    uv tool install poetry --python=$python_version
    if (( $? ))
    then
        echo "Failed to install poetry! Aborting..."
        exit 1
    fi
    export PATH="$home/.local/bin:$PATH"
else
    echo "poetry is already installed. Skipping"
fi

echo "Checking if ripgrep is installed. (Needed by a neovim plugin)"
rg -v > /dev/null 2>&1
if (( $? ))
then
    echo "Installing ripgrep"
    sudo apt install ripgrep
    if (( $? ))
    then
        echo "Failed to install ripgrep! Aborting..."
        exit 1
    fi
    source $home/.cargo/env
else
    echo "ripgrep is already installed. Skipping"
fi

echo "Checking if fd is installed. (Needed by a neovim plugin)"
fd -v > /dev/null 2>&1
if (( $? ))
then
    echo "Installing fd"
    sudo apt install fd-find
    if (( $? ))
    then
        echo "Failed to install fd! Aborting..."
        exit 1
    fi
    source $home/.cargo/env
else
    echo "fd is already installed. Skipping"
fi

echo "Checking if neovim is installed"
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

echo "Checking if dot is cloned to this machine yet"
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

echo "Checking if dot is installed yet"
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
