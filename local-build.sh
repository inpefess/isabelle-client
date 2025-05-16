#!/bin/sh

set -e
PACKAGE_NAME=isabelle_client
cd doc
make clean html coverage
cat _build/coverage/python.txt
cd ..
ruff check
pylint ${PACKAGE_NAME}
mypy ${PACKAGE_NAME}
find ${PACKAGE_NAME} -name "*.py" | xargs -I {} pyupgrade --py39-plus {}
pyroma -n 10 .
coverage run
coverage report
scc --no-cocomo --by-file -i py ${PACKAGE_NAME}
