set -e

pyenv_root=$HOME/.pyenv
if [[ -e $pyenv_root ]]
then
    debug_out "pyenv is already installed. Skipping"
else
    echo "Installing pyenv"
    curl https://pyenv.run | bash
fi

echo "Installing python 3.8.12 via pyenv"
pyenv install 3.8.12

echo "Setting python 3.8.12 as default"
pyenv global 3.8.12


if [[ -e $HOME/.config/pypoetry ]]
then
    debug_out "poetry is already installed. Skipping"
else
    echo "Installing poetry"
    curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -
fi
