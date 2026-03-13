#!/usr/bin/env bash

COLOR_RED="\033[0;31m"
COLOR_GREEN="\033[0;32m"
COLOR_YELLOW="\033[1;33m"
COLOR_BLUE="\033[0;34m"
COLOR_OFF="\033[0m"

check () {
    echo -e "${COLOR_YELLOW}?  ${1}${COLOR_OFF}"
}

status () {
    echo -e "${COLOR_BLUE}>  ${1}${COLOR_OFF}"
}

confirm () {
    echo -e "${COLOR_GREEN}+  ${1}${COLOR_OFF}"
}

warn () {
    echo -e "${COLOR_YELLOW}!  ${1}${COLOR_OFF}"
}

skip () {
    echo -e "${COLOR_BLUE}-  Skipping: ${1}${COLOR_OFF}"
}

home=$(echo "$HOME" | sed 's:/*$::')
python_version="3.13"
export XDG_BIN_HOME="${XDG_BIN_HOME:-$home/.local/bin}"
export PATH="$XDG_BIN_HOME:$PATH"
dot_root="$home/src/dusktreader/dot"


# --- Extra dotfiles block in .bashrc / .zshrc ---

check "Checking for extra dotfiles block in startup config"
if [[ "$(uname)" == "Darwin" ]]; then
    startup_config="$home/.zshrc"
else
    startup_config="$home/.bashrc"
fi

if [[ -f "$startup_config" ]] && grep -q "EXTRA DOTFILES START" "$startup_config"
then
    status "Removing extra dotfiles block from $startup_config"
    # Remove everything between (and including) the EXTRA DOTFILES START/END markers
    sed -i '/# EXTRA DOTFILES START/,/# EXTRA DOTFILES END/d' "$startup_config"
    confirm "Removed extra dotfiles block from $startup_config"
else
    skip "No extra dotfiles block found in $startup_config"
fi


# --- ~/.extra_dotfiles ---

check "Checking for ~/.extra_dotfiles"
if [[ -f "$home/.extra_dotfiles" ]]
then
    status "Removing $home/.extra_dotfiles"
    rm "$home/.extra_dotfiles"
    confirm "Removed $home/.extra_dotfiles"
else
    skip "~/.extra_dotfiles not found"
fi


# --- dot uv tool ---

check "Checking if dot is installed as a uv tool"
if command -v uv > /dev/null 2>&1 && uv tool list 2>/dev/null | grep -q "^dot-tools"
then
    status "Uninstalling dot via uv"
    uv tool uninstall dot-tools
    confirm "Uninstalled dot"
else
    skip "dot is not installed as a uv tool"
fi


# --- Symlinks from link_paths ---

status "Removing symlinks"
link_paths=(
    .ackrc
    .psqlrc
    .gitconfig
    .gitconfig.dusktreader
    .systemd-env
    .config/terminator
    .config/nvim/init.lua
    .config/nvim/lua
    .config/oh-my-posh/dusktreader.omp.yaml
)
for path in "${link_paths[@]}"
do
    target="$home/$path"
    check "Checking $target"
    if [[ -L "$target" ]]
    then
        status "Removing symlink $target"
        rm "$target"
        confirm "Removed $target"
    else
        skip "$target is not a symlink"
    fi
done


# --- Copied files from copy_paths ---

status "Removing copied files"
copy_paths=(
    .ssh/config
    .ssh/rc
)
for path in "${copy_paths[@]}"
do
    target="$home/$path"
    check "Checking $target"
    if [[ -f "$target" ]]
    then
        status "Removing $target"
        rm "$target"
        confirm "Removed $target"
    else
        skip "$target not found"
    fi
done


# --- Directories from mkdir_paths ---

status "Removing created directories"
mkdir_paths=(
    .vim/local/backup
    .vim/local/swap
    .vim/undodir
)
for path in "${mkdir_paths[@]}"
do
    target="$home/$path"
    check "Checking $target"
    if [[ -d "$target" ]]
    then
        status "Removing directory $target"
        rm -rf "$target"
        confirm "Removed $target"
    else
        skip "$target not found"
    fi
done


# --- dot repository ---

check "Checking if dot repository is cloned"
if [[ -d "$dot_root" ]]
then
    status "Removing dot repository at $dot_root"
    rm -rf "$dot_root"
    confirm "Removed $dot_root"
else
    skip "dot repository not found at $dot_root"
fi

check "Checking if $home/src/dusktreader is empty"
if [[ -d "$home/src/dusktreader" ]] && [[ -z "$(ls -A "$home/src/dusktreader")" ]]
then
    status "Removing empty directory $home/src/dusktreader"
    rmdir "$home/src/dusktreader"
    confirm "Removed $home/src/dusktreader"
fi

check "Checking if $home/src is empty"
if [[ -d "$home/src" ]] && [[ -z "$(ls -A "$home/src")" ]]
then
    status "Removing empty directory $home/src"
    rmdir "$home/src"
    confirm "Removed $home/src"
fi


# --- uv python ---

check "Checking if python $python_version is installed via uv"
if command -v uv > /dev/null 2>&1 && uv python list 2>/dev/null | grep -q "$python_version"
then
    status "Uninstalling python $python_version via uv"
    uv python uninstall "$python_version"
    confirm "Uninstalled python $python_version"
else
    skip "python $python_version not found in uv"
fi


# --- uv itself ---

check "Checking if uv is installed"
if command -v uv > /dev/null 2>&1
then
    status "Uninstalling uv"
    uv self uninstall --no-confirm 2>/dev/null || {
        # fallback: remove the binary and env script directly
        rm -f "$XDG_BIN_HOME/uv" "$XDG_BIN_HOME/uvx" "$XDG_BIN_HOME/env"
    }
    confirm "Uninstalled uv"
else
    skip "uv is not installed"
fi


# --- sudoers entry ---

check "Checking if $USER has a sudoers entry created by install.sh"
if [[ -f "/etc/sudoers.d/$USER" ]]
then
    status "Removing /etc/sudoers.d/$USER"
    sudo rm "/etc/sudoers.d/$USER"
    confirm "Removed sudoers entry for $USER"
else
    skip "No sudoers entry found at /etc/sudoers.d/$USER"
fi


confirm "Uninstall complete"
