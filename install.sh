#!/usr/bin/env bash

source ./.dot_colors
home=$(echo "$HOME" | sed 's:/*$::')
python_version="3.13"

check () {
    message=$1
    echo -e "${COLOR_YELLOW}  ${1}${COLOR_OFF}"
}

status () {
    message=$1
    echo -e "${COLOR_BLUE}►  ${1}${COLOR_OFF}"
}

confirm () {
    message=$1
    echo -e "${COLOR_GREEN}  ${1}${COLOR_OFF}"
}

fail () {
    message=$1
    echo -e "${COLOR_RED}  ${1} Aborting...${COLOR_OFF}"
    exit 1
}

check "Checking if $USER has already been added to sudoers"
sudo grep $USER /etc/sudoers > /dev/null 2>&1
if (( $? ))
then
    status "Making passwordless sudo"
    echo "$USER ALL=(ALL) NOPASSWD: ALL" | (EDITOR="tee -a" sudo visudo)
    if (( $? ))
    then
        fail "Failed to configure sudo! Aborting..."
    else
        confirm "Added $USER to sudoers"
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
    else
        confirm "Installed unzip"
    fi
else
    confirm "unzip is already installed."
fi

check "Checking if oh-my-posh is installed"
oh-my-posh version > /dev/null 2>&1
if (( $? ))
then
    status "Installing oh-my-posh"
    if [[ "$OSTYPE" == "darwin"* ]]
    then
	    sudo port -N install oh-my-posh
    else
        curl -s https://ohmyposh.dev/install.sh | bash -s
    fi
    if (( $? ))
    then
        fail "Failed to install oh-my-posh!"
    else
        confirm "Installed oh-my-posh"
    fi
else
    confirm "oh-my-posh is already installed."
fi

check "Checking if uv is installed"
uv version > /dev/null 2>&1
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

check "Checking if poetry is installed"
poetry --version > /dev/null 2>&1
if (( $? ))
then
    status "Installing poetry"
    uv tool install poetry --python=$python_version
    if (( $? ))
    then
        fail "Failed to install poetry!"
    else
        confirm "Installed poetry"
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
    if [[ "$OSTYPE" == "darwin"* ]]
    then
        sudo port -N install ripgrep
    else
        sudo apt install ripgrep
    fi
    if (( $? ))
    then
        fail "Failed to install ripgrep!"
    else
        confirm "Installed ripgrep"
    fi
    source $home/.local/bin/env
else
    confirm "ripgrep is already installed."
fi

check "Checking if fd is installed. (Needed by a neovim plugin)"
fd --version > /dev/null 2>&1
if (( $? ))
then
    status "Installing fd"
    if [[ "$OSTYPE" == "darwin"* ]]
    then
        sudo port -N install fd
    else
        sudo apt install fd-find
    fi
    if (( $? ))
    then
        fail "Failed to install fd!"
    else
        confirm "Installed fd"
    fi
else
    confirm "fd is already installed."
fi

check "Checking if fzf is installed. (Needed by a neovim plugin)"
fzf --version > /dev/null 2>&1
if (( $? ))
then
    status "Installing fzf"
    if [[ "$OSTYPE" == "darwin"* ]]
    then
        sudo port -N install fzf
    else
        sudo apt install fzf
    fi
    if (( $? ))
    then
        fail "Failed to install fzf!"
    else
        confirm "Installed fzf"
    fi
else
    confirm "fzf is already installed."
fi

check "Checking if lynx is installed. (Needed by a neovim plugin)"
lynx --version > /dev/null 2>&1
if (( $? ))
then
    status "Installing lynx"
    if [[ "$OSTYPE" == "darwin"* ]]
    then
        sudo port -N install lynx
    else
        sudo apt install lynx
    fi
    if (( $? ))
    then
        fail "Failed to install lynx!"
    else
        confirm "Installed linx"
    fi
else
    confirm "lynx is already installed."
fi

check "Checking if volta is installed"
volta --version > /dev/null 2>&1
if (( $? ))
then
    status "Setting up volta"
    curl https://get.volta.sh | bash
    if (( $? ))
    then
        fail "Failed to install volta!"
    else
        confirm "Installed volta"
    fi
else
    confirm "volta is already installed"
fi

check "Checking if node is installed"
node --version > /dev/null 2>&1
if (( $? ))
then
    status "Setting up node"
    volta install node
    if (( $? ))
    then
        fail "Failed to install node!"
    else
        confirm "Installed node"
    fi
else
    confirm "node is already installed"
fi

status "Making directories for global npm"
mkdir -p $home/.local/share/npm

check "Checking if neovim is installed"
nvim --version > /dev/null 2>&1
if (( $? ))
then
    status "Setting up neovim"
    if [[ "$OSTYPE" == "darwin"* ]]
    then
        sudo port -N install neovim
    else
        sudo snap install nvim --classic
    fi
    if (( $? ))
    then
        fail "Failed to install neovim!"
    else
        confirm "Installed neovim"
    fi
else
    confirm "nvim is already installed."
fi

check "Checking if lua is installed"
lua -v > /dev/null 2>&1
if (( $? ))
then
    status "Setting up lua"
    if [[ "$OSTYPE" == "darwin"* ]]
    then
        sudo port -N install lua
    else
        sudo apt install -y lua5.3
    fi
    if (( $? ))
    then
        fail "Failed to install lua!"
    else
        confirm "Installed lua"
    fi
else
    confirm "lua is already installed."
fi

check "Checking if go is installed"
go version > /dev/null 2>&1
if (( $? ))
then
    status "Setting up go"
    if [[ "$OSTYPE" == "darwin"* ]]
    then
        sudo port -N install go
    else
        sudo snap install go --classic
    fi
    if (( $? ))
    then
        fail "Failed to install go!"
    else
        confirm "Installed go"
    fi
else
    confirm "go is already installed."
fi

check "Checking if luarocks is installed"
luarocks --version > /dev/null 2>&1
if (( $? ))
then
    status "Getting current lua version"
    ver=$(lua -v | awk '{print $2}' | cut -d. -f1,2)
    if [[ -z "$ver" ]]
    then
        fail "Failed to get lua version!"
    else
        status "Setting up luarocks"
        if [[ "$OSTYPE" == "darwin"* ]]
        then
            pkg=$(echo $ver | perl -pe 's/(\d)\.(\d)/lua\1\2-luarocks/g')
            sudo port -N install $pkg
        else
            sudo apt install -y liblua${ver}-dev && \
            pushd /tmp && \
            wget https://luarocks.org/releases/luarocks-3.11.1.tar.gz && \
            tar zxpf luarocks-3.11.1.tar.gz && \
            cd luarocks-3.11.1 && \
            ./configure && \
            make && \
            sudo make install && \
            popd
        fi
        if (( $? ))
        then
            fail "Failed to install luarocks!"
        else
            confirm "Installed luarocks"
        fi
    fi
else
    confirm "luarocks is already installed"
fi

check "Checking if rustup is installed"
rustup --version > /dev/null 2>&1
if (( $? ))
then
    status "Setting up rustup"
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
    if (( $? ))
    then
        fail "Failed to install rustup!"
    else
        confirm "Installed rustup"
    fi
else
    confirm "rustup is already installed"
fi


check "Checking if 1password-cli is installed"
op --version > /dev/null 2>&1
if (( $? ))
then
    status "Setting up 1password-cli"
    if [[ "$OSTYPE" == "darwin"* ]]
    then
        sudo port -N install 1password-cli
    else
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
    fi
    if (( $? ))
    then
        fail "Failed to install 1password-cli!"
    else
        confirm "Installed 1password-cli"
    fi
else
    confirm "1password-cli is already installed"
fi

check "Checking if github cli is installed"
gh --version > /dev/null 2>&1
if (( $? ))
then
    status "Setting up github cli"
    if [[ "$OSTYPE" == "darwin"* ]]
    then
        sudo port -N install gh
    else
        (type -p wget >/dev/null || (sudo apt update && sudo apt-get install wget -y)) && \
    	  sudo mkdir -p -m 755 /etc/apt/keyrings && \
          out=$(mktemp) && \
          wget -nv -O$out https://cli.github.com/packages/githubcli-archive-keyring.gpg && \
          cat $out | sudo tee /etc/apt/keyrings/githubcli-archive-keyring.gpg > /dev/null && \
    	  sudo chmod go+r /etc/apt/keyrings/githubcli-archive-keyring.gpg && \
    	  echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null && \
    	  sudo apt update && \
    	  sudo apt install gh -y
    fi
    if (( $? ))
    then
        fail "Failed to install github cli"
    else
        confirm "Installed github cli"
    fi
else
    confirm "github cli is already installed"
fi

status "Making parent directories for dot"
mkdir -p $home/src/dusktreader

check "Checking if dot is cloned to this machine yet"
if [[ ! -d "$home/src/dusktreader/dot" ]]
then
    status "Cloning dot repository"
    git clone git@github.com:dusktreader/dot.git $home/src/dusktreader/dot
    if (( $? ))
    then
        fail "Failed to clone dot repository!"
    else
        confirm "Cloned dot repository"
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
configure-dot --quiet --root=$home/src/dusktreader/dot
if (( $? ))
then
    fail "Failed to configure dot!"
else
    confirm "Configured dot"
fi

confirm "Completed installation! To activate > source $home/.bashrc"
