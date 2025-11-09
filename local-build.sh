#!/bin/sh

set -e
cd doc
make clean html coverage
cat _build/coverage/python.txt
cd ..
ruff format
ruff check --fix
pydoclint src
pyrefly check src
pyroma -n 10 .
coverage run
coverage report
cloc --fmt 3 --include-lang python src
