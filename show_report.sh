#!/bin/bash

set -e
PACKAGE_NAME=isabelle_client
pycodestyle --max-doc-length 160 --ignore E203,E501,W503 \
	    ${PACKAGE_NAME}
pylint --rcfile=.pylintrc ${PACKAGE_NAME}
mypy --config-file mypy.ini ${PACKAGE_NAME}
pytest --cov ${PACKAGE_NAME} --cov-report term-missing --cov-fail-under=28 \
       --junit-xml test-results/isabelle-client.xml \
       --doctest-modules ${PACKAGE_NAME}
cloc ${PACKAGE_NAME}
