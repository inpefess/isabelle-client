#!/bin/sh

set -e
PACKAGE_NAME=isabelle_client
cd doc
make clean html coverage
cat _build/coverage/python.txt
cd ..
ruff format
ruff check
pydoclint ${PACKAGE_NAME}
pyright
pyroma -n 10 .
coverage run
coverage report
scc --no-cocomo --by-file -i py ${PACKAGE_NAME}
