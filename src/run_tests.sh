#!/usr/bin/env bash
set -x

python3 -V
pip3 install virtualenv
virtualenv venv-tests
source venv-tests/bin/activate

pip3 install tox

pip3 freeze

tox

rm -rf venv-tests