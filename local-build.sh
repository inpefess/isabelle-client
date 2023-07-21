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
find ${PACKAGE_NAME} -name "*.py" | xargs -I {} pyupgrade --py38-plus {}
pyupgrade examples/*.py
pyroma -n 10 .
pytest
scc -i py ${PACKAGE_NAME}
