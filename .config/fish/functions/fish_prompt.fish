function fish_prompt --description 'Write out the prompt'
  set -l last_status $status

  # User
  set_color $fish_color_user
  echo -n (whoami)
  set_color normal

  echo -n '@'

  # Host
  set_color $fish_color_host
  echo -n (hostname -s)
  set_color normal

  echo -n ':'

  # PWD
  set_color $fish_color_cwd
  echo -n (prompt_pwd)
  set_color normal

  __terlar_git_prompt
  __fish_hg_prompt
  echo

  if not test $last_status -eq 0
    set_color $fish_color_error
  end

  echo -n '➤ '
  set_color normal
end

function debug_out --description Conditionally print debug lines
    if begin; status --is-interactive; or $DOT_DEBUG; end
        echo $argv
    end
end

debug_out "Processing main dot configuration"

set -Ux PATH $PATH \
    ~/bin \
    /Applications/Postgres.app/Contents/Versions/latest/bin

debug_out "Detecting which python3"
# For the rtk machines...they make executables for python3.4 this way
set python3_path (which python34; or which python3)
debug_out "found python path at $python3_path"
if [ $python3_path ]
    debug_out "Detected python3 at $python3_path"
    set user_base ($python3_path -c 'import site;print(site.USER_BASE)'
    if [ $status ]
        debug_out "Python3 is not yet installed. Not modifying PATH"
    else
        set -Ux PATH $PATH "$user_base/bin"
        function python3; command $python3_path $argv; end
        debug_out "Added python3 user base to PATH"
    end
end

function vim; command vim -O $argv; end
function vi; command vim $argv; end
function evim; command $EDITOR ~/dot/.vimrc; end

function egit; command $EDITOR ~/dot/.gitconfig; end

function ebash; command $EDITOR ~/.bashrc; end
function sbash; command source ~/.bashrc; end

alias edot="$EDITOR ~/dot/.dotrc"
alias sdot='source ~/dot/.dotrc'
alias idot='install_dot'
alias cdot='cd ~/dot'

alias egrep='egrep --color=auto'
alias grep='egrep --color=auto'

alias sl='ls'
if [[ $(uname) == "Darwin" ]]
then
    alias ls='gls --color=tty'
    alias ln='gln'
    alias cp='gcp'
    alias touch='gtouch'
    alias vim='/usr/local/bin/vim -O'
    alias ps='pstree -wg3 | less'
else
    alias ls='ls --color=tty'
fi

alias cd='fancy_cd'
alias less='less -RNJMw -z-4'

alias mkdir="echo '(remember the td function?)'; command mkdir"

alias activate='source $(ls | grep env)/bin/activate'

alias gti='git'

debug_out "Detecting which ack"
which ack > /dev/null 2>&1
if (( $? ))
then
    alias ack='ack-grep --color'
else
    alias ack='ack --color'
fi

if [[ "$(hostname)" =~ "digidown" ]]
then
    export SUBSYSTEM_PATH="/data_storage/apps/digital_download/current/"
fi

rentrak_rsa_key="tbeck_rentrak_id_rsa"
rentrak_rsa_path="$HOME/.ssh/$rentrak_rsa_key"
if [[ -e $rentrak_rsa_path ]]
then
    if [[ -z "$(ssh-add -l | grep $rentrak_rsa_key)" ]]
    then
        debug_out "$rentrak_rsa_key key not found in active ssh identities not found.  Setting it up:"
        ssh-add $rentrak_rsa_path
    fi
fi

dusktreader_rsa_key="dusktreader_id_rsa"
dusktreader_rsa_path="$HOME/.ssh/$dusktreader_rsa_key"
if [[ -e $dusktreader_rsa_path ]]
then
    if [[ -z "$(ssh-add -l | grep $dusktreader_rsa_key)" ]]
    then
        debug_out "$dusktreader_rsa_key key not found in active ssh identities not found.  Setting it up:"
        ssh-add $dusktreader_rsa_path
    fi
fi



pip_install_save() {
    package_name=$1
    requirements_file=$2
    if [[ -z $requirements_file ]]
    then
        requirements_file='./etc/setuptools/requirements.txt'
    fi
    pip install $package_name && pip freeze | grep -i "^$package_name==" >> $requirements_file
}

count_files_in_subdirs() {
    target_dir=$1
    if [[ -z $target_dir ]]
    then
        echo "Please supply a target directory" >&2
        return 1
    fi
    debug_out "Counting files in subdirectories of $(readlink -f $target_dir)"
    sort_arg=$2
    if [[ -z $sort_arg ]]
    then
        sort_arg="-k2rn"
    fi
    timestamp=$(date '+%Y%m%d_%H%M%S')
    filename="/tmp/$timestamp-counts.txt"
    rm -f $filename
    for subdir in $(find $target_dir -maxdepth 1 -type d ! -path . )
    do
        echo "$subdir: $(find $subdir -type f | wc -l)" >> $filename
    done
    cat $filename | sort $sort_arg
}

smart_ls() {
    target=$1
    simple_list=$(command ls -1 $target) || return
    count=$(echo $simple_list | wc -w)
    if (( $count == 0 ))
    then
        echo "Directory is empty"
    elif (( $count <= 10 ))
    then
        ls -l --color=tty $target
    elif (( $count <= 100 ))
    then
        ls --color=tty $target
    else
        echo "Directory contains $count files"
    fi
}

fancy_cd() {
    newdir=$1
    builtin cd $newdir || return
    smart_ls .
}

td() {
    newdir=$1
    command mkdir $newdir || return
    builtin cd $newdir
}

abs_path() {
    path=$1
    if [[ -z $path ]]
    then
        pwd
        return
    fi

    python -c "import os; print(os.path.realpath('$path'))"
}

install_local_python() {
    log_file=$1
    redirect=''
    if [[ ! -z $log_file ]]
    then
        redirect=">>$log_file 2>&1"
    fi

    command cd ~
    commands=(
        "wget http://www.python.org/ftp/python/3.4/Python-3.4.tgz"
        "tar xzf Python-3.4.tgz"
        "command cd Python-3.4/"
        "./configure --prefix=/home/tbeck/"
        "make"
        "make install"
        "rm -rf Python-3.4*"
    )
    for command in "${commands[@]}"
    do
        eval "$command $redirect"
        if (( $? ))
        then
            message="Command failed: $command"
            return 0
        fi
    done
    return 1
}

source_dotfiles() {
    debug_out "Sourcing dotfiles"
    if [[ -e ~/dot/.dotfiles ]]
    then
        while read dotfile
        do
            source ~/dot/$dotfile
        done < ~/dot/.dotfiles
    fi
}

install_dot() {
    initial_directory=$(pwd)
    for return_status in 0
    do
        export SKIP_TODO=1

        echo "Installing DotTools python package for current user"

        debug_out "Attempting to deactivate virtual environment"
        deactivate

        command cd ~/dot/DotTools
        if (( $? ))
        then
            message="Couldn't navigate to DotTools directory.  Aborting..."
            return_status=1
            break
        fi
        debug_out "Changed directory to $(pwd)"

        installed_files=~/dot/DotTools/installed_files.txt
        install_log=~/dot/DotTools/install_log.txt
        if [[ ! -e $installed_files ]]
        then
            touch $installed_files
            if (( $? ))
            then
                message="Couldn't create record for installed files.  Aborting..."
                return_status=1
                break
            fi
        fi
        if [[ ! -e $install_log ]]
        then
            touch $install_log
            if (( $? ))
            then
                message="Couldn't create log for install.  Aborting..."
                return_status=1
                break
            fi
        fi

        debug_out "Checking for Python 3 installation"
        which python3 > /dev/null 2>&1
        if (( $? ))
        then
            debug_out "Python 3 is not installed. Installing locally"
            if install_local_python $install_log
            then
                debug_out "Installed Python 3 locally"
            else
                message="Couldn't install local python. Aborting..."
                return_status=1
                break
            fi
        else
            debug_out "Python 3 is already installed"
        fi

        debug_out "Discovering pip3"
        pip3="$(which pip3 || which pip34)"
        if (( $? ))
        then
            message="Couldn't find pip3 on the system. Aborting..."
            return_status=1
            break
        fi

        debug_out "Installing virtualenvwrapper"
        $pip3 install --user --force-reinstall --verbose virtualenvwrapper

        debug_out "Installing DotTools package"
        $pip3 install --user --force-reinstall --verbose ~/dot/DotTools/
        if (( $? ))
        then
            message="Couldn't install python DotTools package.  Aborting..."
            return_status=1
            break
        fi
        user_base=$(python3 -c 'import site;print(site.USER_BASE)')

        command cd $initial_directory

        $user_base/bin/underlined_header "Installing dot config on $(hostname)"

        link_list=(
            .vimrc
            .psqlrc
            .gitconfig
            .vim/after/
            .vim/autoload/
            .vim/bundle/
            .vim/bundle2/
            .vim/fonts/
            .config/terminator/
            .config/fish/
        )

        copy_list=(
            .ssh/config
            .ssh/rc
        )

        dot_files=(
            .dot_misc
            .dot_tools_helpers
            .dot_colors
        )

        mkdir_list=(
            .vim/local/backup
            .vim/local/swap
        )

        if [[ -e ~/dot/.dotfiles ]]
        then
            > ~/dot/.dotfiles
            if (( $? ))
            then
                return_status=1
                message="Failed to clear .dotfiles"
                break
            fi
        else
            touch ~/dot/.dotfiles
            if (( $? ))
            then
                return_status=1
                message="Failed to add .dotfiles"
                break
            fi
        fi

        for path_name in "${mkdir_list[@]}"
        do
            full_path=$(abs_path ~)/$path_name
            debug_out "Making $full_path directory"
            mkdir -p $full_path
            if (( $? ))
            then
                return_status=1
                message="Failed to make $full_path directory"
                break
            fi
        done

        for file_name in "${dot_files[@]}"
        do
            debug_out "Installing $file_name in .dotfiles"
            debug_out $file_name >> ~/dot/.dotfiles
        done

        for file_name in "${link_list[@]}"
        do
            link_path=$(abs_path ~)/$file_name
            link_dir=$(dirname $link_path)
            target_path=$(abs_path ~)/dot/$file_name

            if [[ -h $link_path && "$(readlink $link_path)" == "$target_path" ]]
            then
                debug_out "Skipping $file_name: it is already installed"
                continue
            fi

            if [[ ! -e $link_dir ]]
            then
                mkdir -p $link_dir
                if (( $? ))
                then
                    debug_out "Couldn't install $file_name: Couldn't make $link_dir for link $link_path"
                    continue
                fi
            fi

            debug_out "Installing $file_name"
            ln -sb $target_path $link_dir
            if (( $? ))
            then
                debug_out "Couldn't install $file_name: failed to link $target_path to $link_path"
                continue
            fi
        done

        for file_name in "${copy_list[@]}"
        do
            copy_path=$(abs_path ~)/$file_name
            copy_dir=$(dirname $copy_path)
            target_path=$(abs_path ~)/dot/$file_name

            if [[ -e $copy_path && ! -h $copy_path && -z $(diff $copy_path $target_path) ]]
            then
                debug_out "Skipping $file_name: it is already installed"
                continue
            fi

            if [[ ! -e $link_dir ]]
            then
                mkdir -p $copy_dir
                if (( $? ))
                then
                    debug_out "Couldn't install $file_name: Couldn't make $link_dir for link $link_path"
                    continue
                fi
            fi

            debug_out "Installing $file_name"
            cp -b $target_path $copy_dir
            if (( $? ))
            then
                debug_out "Couldn't install $file_name: failed to copy $target_path to $copy_path"
                continue
            fi

            chmod 600 $copy_path
            if (( $? ))
            then
                debug_out "Couldn't change permissions of $file_name.  Connection via ssh may not work"
                continue
            fi
        done

        debug_out "Installing powerline fonts"
        bash ~/dot/.vim/fonts/powerline/install.sh

        if [[ "$(uname)" -eq 'Darwin' ]]
        then
            startup_config="$HOME/.bash_profile"
        else
            startup_config="$HOME/.bashrc"
        fi

        debug_out "$startup_config doesn't exist. Creating it"
        if [[ ! -e $startup_config ]]
        then
            touch $startup_config
        fi

        debug_out "Adding .dotrc to $startup_config"
        if [[ -z $(grep "DOT INSTALLED" $startup_config) ]]
        then
            $user_base/bin/underlined_header "Updating .bashrc to source dot"

            if [[ ! -w $startup_config ]]
            then
                return_status=1
                message="Couldn't modify .bashrc to install dot.  Aborting..."
                break
            fi

            echo "# DOT INSTALLED" >> $startup_config
            echo "if [[ -e ~/dot/.dotrc ]]" >> $startup_config
            echo "then" >> $startup_config
            echo "    source ~/dot/.dotrc" >> $startup_config
            echo "fi" >> $startup_config
        fi

        source $startup_config

        message="Finished Installing dot"
    done

    command cd $initial_directory
    $user_base/bin/underlined_header -f "Updating .bashrc to source dot"
    return $return_status
}

source_dotfiles

debug_out "Detecting git"
which git > /dev/null 2>&1
if (( $? ))
then
    debug_out "Did not detect git. Using default prompt"
    export PS1="$C3// $C6[\h:\w]$C4 $P\n\$ "
else
    debug_out "Detected git. Embedding git branch propmt"
    source ~/dot/.git-prompt
    export PS1="$C3// $C6[\h:\w]$C4 \$(__git_ps1 '(%s)')$P\n\$ "
fi

# TODO: do this right
debug_out "Detecting virtualenvwrapper"
which virtualenvwrapper.sh > /dev/null 2>&1
if (( $? ))
then
    debug_out "Did not detect virtualenvwrapper. Skipping"
else
    debug_out "Found virtualenvwrapper. Sourcing with python3"
    export VIRTUALENVWRAPPER_PYTHON=$(which python3)
    source $(which virtualenvwrapper.sh)
fi

if [[ $- == *i* && -z "$SKIP_TODO" ]]
then
    which todo > /dev/null 2>&1
    if (( ! $? ))
    then
        todo
    fi
fi

