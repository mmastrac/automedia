#!/bin/bash
set -eu -o pipefail

if [[ "$#" != "1" || "$1" == "--help" ]]; then
    echo usage: "$0" [version]
    echo '    version        numeric version plus hyphen/period only (ie: 0.1, 1.0-beta, 2.1, etc)'
    exit 1
fi

git diff --exit-code >/dev/null || (echo 'Uncommitted changes, aborting!'; exit 2)
git diff --cached --exit-code >/dev/null || (echo 'Uncommitted changes, aborting!'; exit 2)

VERSION=v"$1"
RAW_VERSION="$1"
echo Building version "$VERSION"...

sed -I.bak 's/version =.*/version = "'$RAW_VERSION'"/g' pyproject.toml && rm pyproject.toml.bak
git diff --exit-code >/dev/null || (git add pyproject.toml && git commit -m "Bump version to $VERSION")
git tag -d "$VERSION" 2>&1 >/dev/null || true
git tag "$VERSION"

python3 -m build
twine check dist/*
docker build . --build-arg AUTOMEDIA_VERSION="$RAW_VERSION" -t mmastrac/automedia:$RAW_VERSION -t mmastrac/automedia:latest

echo 'Now publish the package:'
echo
echo 'docker push mmastrac/automedia:latest'
echo 'docker push mmastrac/automedia:'$RAW_VERSION
echo 'twine upload dist/automedia-'$RAW_VERSION'*'
