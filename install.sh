#!/usr/bin/env bash

home=$(echo "$HOME" | sed 's:/*$::')

sudo grep $USER /etc/sudoers > /dev/null 2>&1
if (( $? ))
then
    echo "Making passwordless sudo"
    echo "$USER ALL=(ALL) NOPASSWD: ALL" | (sudo su -c 'EDITOR="tee" visudo')
fi


# Once UV has the option to set a global python, we can remove the pyenv dependency
echo "Checking if pyenv is installed"
pyenv_root=$home/.pyenv
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

    export PYENV_ROOT="$home/.pyenv"
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
    source $home/.cargo/env
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

# Once UV has the option to set a global python, we can use uv to install python 3.11
#echo "Checking if python 3.11 is installed"
#uv python list | grep "3\.11" > /dev/null 2>&1
#if (( $? ))
#then
#    echo "Installing python 3.11 via pyenv"
#    uv python install 3.11
#
#    # echo "Setting python 3.11 as default"
#    # pyenv global 3.11
#else
#    echo "python 3.11 is already available through uv"
#fi


echo "Checking if poetry is installed"
poetry --version > /dev/null 2>&1
if (( $? ))
then
    echo "Installing poetry"
    uv tool install poetry
    export PATH="/home/dusktreader/.local/bin:$PATH"
else
    echo "poetry is already installed. Skipping"
fi

echo "Installing node, because it's needed by the coc plugin for neovim"
curl -sL install-node.vercel.app/lts | sudo bash

echo "Checking if nvim is installed"
nvim --version > /dev/null 2>&1
if (( $? ))
then
    echo "Setting up neovim"
    sudo snap install nvim --classic
else
    echo "nvim is already installed. Skipping"
fi

echo "Making parent directories for dot"
mkdir -p $home/git-repos/personal

echo "Cloning dot repository"
git clone git@github.com:dusktreader/dot.git $home/git-repos/personal/dot

echo "Installing dot via uv"
uv tool install $home/git-repos/personal/dot --force

echo "Configuring dot"
configure-dot --root=$home/git-repos/personal/dot
