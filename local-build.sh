#!/bin/sh

set -e
cd doc
make clean html coverage
cat _build/coverage/python.txt
cd ..
ruff format
ruff check --fix
pydoclint src
pyrefly check
pyroma -n 10 .
coverage run
coverage report
scc --no-cocomo --by-file -i py src
