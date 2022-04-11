#!/bin/bash
set -eu -o pipefail

docker build . -t mmastrac/automedia
python3 -m build
twine check dist/*
