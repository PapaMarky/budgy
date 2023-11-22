#!/usr/bin/env bash

function build {
  rm -rf dist
  python3 -m build
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
build $PROJECT
popd
