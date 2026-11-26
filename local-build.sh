#!/bin/sh

set -e
zensical build --clean
ruff format
ruff check --fix
pydoclint src
ty check
pyroma -n 10 .
coverage run
coverage report
cloc --fmt 3 --include-lang python src
