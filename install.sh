#!/usr/bin/env bash

source ./.dot_colors
home=$(echo "$HOME" | sed 's:/*$::')
python_version="3.12"

check () {
    message=$1
    echo -e "${COLOR_YELLOW}\uf29c  ${1}${COLOR_OFF}"
}

status () {
    message=$1
    echo -e "${COLOR_BLUE}\u25ba  ${1}${COLOR_OFF}"
}

confirm () {
    message=$1
    echo -e "${COLOR_GREEN}\uf00c  ${1}${COLOR_OFF}"
}

fail () {
    message=$1
    echo -e "${COLOR_RED}\ueabd  ${1} Aborting...${COLOR_OFF}"
    exit 1
}

check "Checking if $USER has already been added to sudoers"
sudo grep $USER /etc/sudoers > /dev/null 2>&1
if (( $? ))
then
    status "Making passwordless sudo"
    echo "$USER ALL=(ALL) NOPASSWD: ALL" | (sudo su -c 'EDITOR="tee -a" visudo')
    if (( $? ))
    then
        fail "Failed to configure sudo! Aborting..."
    fi
else
    confirm "$USER is already a sudoer"
fi

check "Checking if unzip is installed (needed for oh-my-posh)"
unzip > /dev/null 2>&1
if (( $? ))
then
    status "Installing unzip"
    sudo apt install unzip
    if (( $? ))
    then
        fail "Failed to install unzip!"
    fi
else
    confirm "unzip is already installed."
fi

check "Checking if oh-my-posh is installed"
oh-my-posh version > /dev/null 2>&1
if (( $? ))
then
    status "Installing oh-my-posh"
    curl -s https://ohmyposh.dev/install.sh | bash -s
    if (( $? ))
    then
        fail "Failed to install oh-my-posh!"
    fi
else
    confirm "oh-my-posh is already installed."
fi

check "Checking if uv is installed"
uv version > /dev/null 2>&1
if (( $? ))
then
    status "Installing uv"
    curl -LsSf https://astral.sh/uv/install.sh | sh
    if (( $? ))
    then
        fail "Failed to install uv!"
    fi
    source $home/.cargo/env
else
    confirm "uv is already installed."
    source $home/.cargo/env
fi

check "Checking if python $python_version is installed"
uv python list | grep $python_version > /dev/null 2>&1
if (( $? ))
then
    status "Installing python $python_version via uv"
    uv python install $python_version
    if (( $? ))
    then
        fail "Failed to install python $python_version!"
    fi
else
    confirm "python $python_version is already available through uv"
fi

check "Checking if poetry is installed"
poetry --version > /dev/null 2>&1
if (( $? ))
then
    status "Installing poetry"
    uv tool install poetry --python=$python_version
    if (( $? ))
    then
        fail "Failed to install poetry!"
    fi
    export PATH="$home/.local/bin:$PATH"
else
    confirm "poetry is already installed."
fi

check "Checking if ripgrep is installed. (Needed by a neovim plugin)"
rg --version > /dev/null 2>&1
if (( $? ))
then
    status "Installing ripgrep"
    sudo apt install ripgrep
    if (( $? ))
    then
        fail "Failed to install ripgrep!"
        exit 1
    fi
    source $home/.cargo/env
else
    confirm "ripgrep is already installed."
fi

check "Checking if fd is installed. (Needed by a neovim plugin)"
fd --version > /dev/null 2>&1
if (( $? ))
then
    status "Installing fd"
    sudo apt install fd-find
    if (( $? ))
    then
        fail "Failed to install fd!"
    fi
    source $home/.cargo/env
else
    confirm "fd is already installed."
fi

check "Checking if fzf is installed. (Needed by a neovim plugin)"
fzf --version > /dev/null 2>&1
if (( $? ))
then
    status "Installing fzf"
    sudo apt install fzf
    if (( $? ))
    then
        fail "Failed to install fzf!"
    fi
else
    confirm "fzf is already installed."
fi

check "Checking if neovim is installed"
nvim --version > /dev/null 2>&1
if (( $? ))
then
    status "Setting up neovim"
    sudo snap install nvim --classic
    if (( $? ))
    then
        fail "Failed to install neovim!"
    fi
else
    confirm "nvim is already installed."
fi

check "Checking if 1password-cli is installed"
op --version > /dev/null 2>&1
if (( $? ))
then
    status "Setting up 1password-cli"
    curl -sS https://downloads.1password.com/linux/keys/1password.asc | \
      sudo gpg --dearmor --output /usr/share/keyrings/1password-archive-keyring.gpg && \
      echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/1password-archive-keyring.gpg] https://downloads.1password.com/linux/debian/$(dpkg --print-architecture) stable main" | \
      sudo tee /etc/apt/sources.list.d/1password.list && \
      sudo mkdir -p /etc/debsig/policies/AC2D62742012EA22/ && \
      curl -sS https://downloads.1password.com/linux/debian/debsig/1password.pol | \
      sudo tee /etc/debsig/policies/AC2D62742012EA22/1password.pol && \
      sudo mkdir -p /usr/share/debsig/keyrings/AC2D62742012EA22 && \
      curl -sS https://downloads.1password.com/linux/keys/1password.asc | \
      sudo gpg --dearmor --output /usr/share/debsig/keyrings/AC2D62742012EA22/debsig.gpg && \
      sudo apt update && sudo apt install 1password-cli
    if (( $? ))
    then
        fail "Failed to install 1password-cli!"
    fi
else
    confirm "1password-cli is already installed"
fi

status "Making parent directories for dot"
mkdir -p $home/git-repos/personal

check "Checking if dot is cloned to this machine yet"
if [[ ! -d "$home/git-repos/personal/dot" ]]
then
    status "Cloning dot repository"
    git clone git@github.com:dusktreader/dot.git $home/git-repos/personal/dot
    if (( $? ))
    then
        fail "Failed to clone dot repository!"
    fi
else
    confirm "dot is already cloned on this machine"
fi

check "Checking if dot is installed yet"
now > /dev/null 2>&1
if (( $? ))
then
    status "Installing dot via uv"
    uv tool install $home/git-repos/personal/dot --force --python=$python_version --editable
    if (( $? ))
    then
        fail "Failed to clone dot repository!"
    fi
else
    confirm "dot is already installed"
fi

status "Configuring dot"
configure-dot --quiet --root=$home/git-repos/personal/dot
if (( $? ))
then
    fail "Failed to configure dot!"
fi

confirm "Completed installation! To activate > source $home/.bashrc"
