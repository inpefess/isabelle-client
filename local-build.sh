#!/bin/sh

set -e
PACKAGE_NAME=isabelle_client
cd doc
make clean html coverage
cat _build/coverage/python.txt
cd ..
pydocstyle ${PACKAGE_NAME} examples
flake8 ${PACKAGE_NAME} examples
pylint ${PACKAGE_NAME} examples
mypy ${PACKAGE_NAME} examples
pyroma .
pytest
scc -i py ${PACKAGE_NAME}
