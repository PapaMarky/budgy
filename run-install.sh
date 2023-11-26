#!/usr/bin/env bash

function install {
  DIST_DIR=dist
  N=$(ls $DIST_DIR/*.whl | wc -l | sed 's/[[:blank:]]//g')
  if [[ $N > 1 ]]; then
    echo "ERROR: Multiple whl files found in dist:"
    ls -al $DIST_DIR/*.whl
    return
  fi
  echo pip3 install --force-reinstall $DIST_DIR/*.whl
  pip3 install --force-reinstall $DIST_DIR/*.whl
}

install
