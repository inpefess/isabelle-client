#!/bin/bash

set -e
PACKAGE_NAME=isabelle_client
cd doc
make clean html coverage
cat build/coverage/python.txt
cd ..
flake8 ${PACKAGE_NAME} examples
pylint ${PACKAGE_NAME} examples
mypy ${PACKAGE_NAME} examples
pytest --cov-report term-missing ${PACKAGE_NAME}
scc -i py ${PACKAGE_NAME}
