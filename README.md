* First install build libraries

```bash
$ sudo apt-get update; sudo apt-get install make build-essential libssl-dev zlib1g-dev \
  libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm \
  libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev
```

* Then, install pyenv

```bash
$ curl https://pyenv.run | bash
$ export PYENV_ROOT="$HOME/.pyenv"
$ export PATH="$PYENV_ROOT/bin:$PATH"
$ eval "$(pyenv init --path)"
```

* Next, install python versions

```bash
$ pyenv install 3.6.15
$ pyenv install 3.8.13
$ pyenv global 3.8.13
```

* Next, install poetry
```bash
$ curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -
$ source $HOME/.poetry/env
```

* Next, install neovim
```bash
$ sudo apt install neovim
```

* Then, install dot
```bash
$ poetry install
```



