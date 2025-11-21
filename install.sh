#!/usr/bin/env bash

export EDITOR=vim
COLOR_RED="\033[0;31m"
COLOR_GREEN="\033[0;32m"
COLOR_YELLOW="\033[1;33m"
COLOR_BLUE="\033[0;34m"
COLOR_OFF="\033[0m"

check () {
    message=$1
    echo -e "${COLOR_YELLOW}?  ${1}${COLOR_OFF}"
}

status () {
    message=$1
    echo -e "${COLOR_BLUE}>  ${1}${COLOR_OFF}"
}

confirm () {
    message=$1
    echo -e "${COLOR_GREEN}+  ${1}${COLOR_OFF}"
}

fail () {
    message=$1
    echo -e "${COLOR_RED}X  ${1} Aborting...${COLOR_OFF}"
    exit 1
}

check "Setting up variables"
home=$(echo "$HOME" | sed 's:/*$::')
python_version="3.13"
export EDITOR=vim
export PATH="$home/.local/bin:$PATH"
confirm "Setup complete"

check "Checking if $USER has already been added to sudoers"
sudo grep $USER /etc/sudoers > /dev/null 2>&1
if (( $? ))
then
    status "Making passwordless sudo"
    echo "$USER ALL=(ALL) NOPASSWD: ALL" | sudo tee /etc/sudoers.d/$USER > /dev/null
    if (( $? ))
    then
        fail "Failed to configure sudo! Aborting..."
    else
        confirm "Added $USER to sudoers"
    fi
else
    confirm "$USER is already a sudoer"
fi

check "Checking if uv is installed"
command -v uv > /dev/null 2>&1
if (( $? ))
then
    status "Installing uv"
    if [[ "$OSTYPE" == "darwin"* ]]
    then
        sudo port -N install uv
    else
        curl -LsSf https://astral.sh/uv/install.sh | sh
    fi
    if (( $? ))
    then
        fail "Failed to install uv!"
    else
        confirm "Installed uv"
    fi
    source $home/.local/bin/env
else
    confirm "uv is already installed."
    source $home/.local/bin/env
fi

# I'm not sure that this is still needed. Need to check on a fresh Ubuntu install
# check "Checking if python3.12-venv is installed (needed by Mason FOR NOW)"
# apt -qq list python3.12-venv > /dev/null 2>&1
# if (( $? ))
# then
#     status "Installing python3.12-venv"
#     sudo apt install -y python3.12-venv
#     if (( $? ))
#     then
#         fail "Failed to install python3.12-venv"
#     else
#         confirm "Installed python3.12-venv"
#     fi
# else
#     confirm "python3.12-venv is already installed"
# fi


check "Checking if python $python_version is installed"
uv python list | grep $python_version > /dev/null 2>&1
if (( $? ))
then
    status "Installing python $python_version via uv"
    uv python install $python_version
    if (( $? ))
    then
        fail "Failed to install python $python_version!"
    else
        confirm "Installed python $python_version"
    fi
else
    confirm "python $python_version is already available through uv"
fi

status "Making parent directories for dot"
mkdir -p $home/src/dusktreader

check "Checking if dot is cloned to this machine yet"
if [[ ! -d "$home/src/dusktreader/dot" ]]
then
    status "Cloning dot repository (via https)"
    git -C $home/src/dusktreader clone https://github.com/dusktreader/dot.git
    if (( $? ))
    then
        fail "Failed to clone dot repository!"
    else
        confirm "Cloned dot repository"
    fi

    status "Changing dot origin url to use ssh for future access"
    git -C $home/src/dusktreader/dot remote set-url origin git@github.com:dusktreader/dot.git
    if (( $? ))
    then
        fail "Failed to change origin to ssh url!"
    else
        confirm "Updated origin url"
    fi
else
    confirm "dot is already cloned on this machine"
fi

check "Checking if dot is installed yet"
dot-version > /dev/null 2>&1
if (( $? ))
then
    status "Installing dot via uv"
    uv tool install $home/src/dusktreader/dot --force --python=$python_version --editable
    if (( $? ))
    then
        fail "Failed to install dot!"
    else
        confirm "Installed dot"
    fi
else
    confirm "dot is already installed"
fi

status "Configuring dot"
dt configure --root=$home/src/dusktreader/dot
if (( $? ))
then
    fail "Failed to configure dot!"
else
    confirm "Configured dot"
fi

confirm "Completed installation! To activate > source $home/.bashrc"
