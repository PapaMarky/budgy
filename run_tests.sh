#!/usr/bin/env bash
function runtests {
  python3 -V
  pip3 install virtualenv
  virtualenv venv-tests
  source venv-tests/bin/activate

  pip3 install tox

  pip3 freeze

  tox

  rm -rf venv-tests
}

PROJECT=$1
echo "Running Unit Tests for $PROJECT"

if [[ ! -d $PROJECT ]]; then
  echo "$PROJECT must be a python package source directory."
  exit 1
fi

set -x

pushd $PROJECT
python3 -V
pip3 install virtualenv
virtualenv venv-tests
source venv-tests/bin/activate

pip3 install tox

pip3 freeze

tox

rm -rf venv-tests .tox
rm -f .coverage
popd

