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
if [[ -z $1 ]]; then
  echo "ERROR: You must supply the python package source directory on the command line"
  exit 1
fi

PROJECT=$1
echo "Running Unit Tests for '$PROJECT'"

if [[ ! -d $PROJECT ]]; then
  echo "ERROR: '$PROJECT' must be a python package source directory."
  exit 1
fi

if [[ ! -f "$PROJECT/setup.cfg" ]]; then
  echo "ERROR: No 'setup.cfg' file in '$PROJECT'"
  exit 1
fi

pushd $PROJECT
runtests $PROJECT
popd

