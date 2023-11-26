#!/usr/bin/env bash

function build {
  rm -rf dist
  python3 -m build
}


build
