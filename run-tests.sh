#!/usr/bin/env bash
function runtests {
  python3 -V
  pip3 install virtualenv
  virtualenv venv-tests
  source venv-tests/bin/activate
  pip3 install tox pytest coverage
  pip3 install -e .
  pip3 freeze
  tox
  deactivate
  rm -rf venv-tests
}

runtests $PROJECT

