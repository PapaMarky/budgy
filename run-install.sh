#!/usr/bin/env bash

function install {
  N=$(ls dist/*.whl | wc -l | sed 's/[[:blank:]]//g')
  if [[ $N > 1 ]]; then
    echo "ERROR: Multiple whl files found in dist:"
    ls -al dist/*.whl
    return
  fi
  pip3 install --force-reinstall dist/*.whl
}
if [[ -z $1 ]]; then
  echo "ERROR: You must supply the python package source directory on the command line"
  exit 1
fi

PROJECT=$1
echo "Building package in '$PROJECT'"

if [[ ! -d $PROJECT ]]; then
  echo "ERROR: '$PROJECT' must be a python package source directory."
  exit 1
fi

if [[ ! -f "$PROJECT/setup.cfg" ]]; then
  echo "ERROR: No 'setup.cfg' file in '$PROJECT'"
  exit 1
fi

pushd $PROJECT
install $PROJECT
popd
