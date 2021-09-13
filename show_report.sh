#!/bin/bash

set -e
PACKAGE_NAME=isabelle_client
cd doc
make clean html
cd ..
pycodestyle --max-doc-length 160 --ignore E203,E501,W503 \
	    ${PACKAGE_NAME} tests examples
pylint --rcfile=.pylintrc ${PACKAGE_NAME} tests examples
mypy --config-file mypy.ini ${PACKAGE_NAME} tests examples
pytest --cov ${PACKAGE_NAME} --cov-report term-missing --cov-fail-under=99 \
       --junit-xml test-results/isabelle-client.xml ${PACKAGE_NAME}
scc -i py ${PACKAGE_NAME}
