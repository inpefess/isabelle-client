[![PyPI version](https://badge.fury.io/py/isabelle-client.svg)](https://badge.fury.io/py/isabelle-client) [![CircleCI](https://circleci.com/gh/inpefess/isabelle-client.svg?style=svg)](https://circleci.com/gh/inpefess/isabelle-client) [![Documentation Status](https://readthedocs.org/projects/isabelle-client/badge/?version=latest)](https://isabelle-client.readthedocs.io/en/latest/?badge=latest) [![codecov](https://codecov.io/gh/inpefess/isabelle-client/branch/master/graph/badge.svg)](https://codecov.io/gh/inpefess/isabelle-client)
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/inpefess/isabelle-client/HEAD?labpath=example.ipynb)

# Python client for Isabelle server

`isabelle-client` is a TCP client for [Isabelle](https://isabelle.in.tum.de) server. For more information about the server see part 4 of [the Isabelle system manual](https://isabelle.in.tum.de/dist/Isabelle2021/doc/system.pdf).

# How to Install

The best way to install this package is to use `pip`:

```sh
pip install isabelle-client
```

One can also download and run the client together with Isabelle in a Docker contanier:

```sh
docker build -t isabelle-client https://github.com/inpefess/isabelle-client.git
docker run -it --rm -p 8888:8888 isabelle-client jupyter-lab --ip=0.0.0.0 --port=8888 --no-browser
```

# How to use

Follow the [usage example](https://isabelle-client.readthedocs.io/en/latest/usage-example.html#usage-example) from documentation, run the [script](https://github.com/inpefess/isabelle-client/blob/master/examples/example.py), or use `isabelle-client` from a [notebook](https://github.com/inpefess/isabelle-client/blob/master/examples/example.ipynb), e.g. with [Binder](https://mybinder.org/v2/gh/inpefess/isabelle-client/HEAD?labpath=example.ipynb).

# How to Contribute

[Pull requests](https://github.com/inpefess/isabelle-client/pulls) are welcome. To start:

```sh
git clone https://github.com/inpefess/isabelle-client
cd isabelle-client
# activate python virtual environment with Python 3.6+
pip install -U pip
pip install -U setuptools wheel poetry
poetry install
# recommended but not necessary
pre-commit install
```

To check the code quality before creating a pull request, one might run the script [show_report.sh](https://github.com/inpefess/isabelle-client/blob/master/show_report.sh). It locally does nearly the same as the CI pipeline after the PR is created.

# Reporting issues or problems with the software

Questions and bug reports are welcome on [the tracker](https://github.com/inpefess/isabelle-client/issues). 

# More documentation

More documentation can be found [here](https://isabelle-client.readthedocs.io/en/latest).

# Video example

![video tutorial](https://github.com/inpefess/isabelle-client/blob/master/examples/tty.gif).

# How to cite

If you're writing a research paper, you can cite Isabelle client (and Isabelle 2021) using the [following DOI](https://doi.org/10.1007/978-3-030-81097-9\_20).
