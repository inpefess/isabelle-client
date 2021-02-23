#!/bin/bash

set -e
PACKAGE_NAME=isabelle_client
cd doc
make clean html
cd ..
pycodestyle --max-doc-length 160 --ignore E203,E501,W503 \
	    ${PACKAGE_NAME} tests
pylint --rcfile=.pylintrc ${PACKAGE_NAME} tests
mypy --config-file mypy.ini ${PACKAGE_NAME} tests
pytest --cov ${PACKAGE_NAME} --cov-report term-missing --cov-fail-under=99 \
       --junit-xml test-results/isabelle-client.xml \
       --doctest-modules ${PACKAGE_NAME}
cloc ${PACKAGE_NAME}
