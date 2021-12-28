set -e

echo "Installing pyenv"
curl https://pyenv.run | bash

echo "Installing python 3.9.7 via pyenv"
pyenv install 3.9.7

echo "Installing pynvim"
python -m pip install pynvim
