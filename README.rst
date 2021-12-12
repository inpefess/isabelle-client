|PyPI version| |CircleCI| |Documentation Status| |codecov| |Binder|

Python client for Isabelle server
=================================

``isabelle-client`` is a TCP client for
`Isabelle <https://isabelle.in.tum.de>`__ server. For more information
about the server see part 4 of `the Isabelle system
manual <https://isabelle.in.tum.de/dist/Isabelle2021/doc/system.pdf>`__.

How to Install
==============

The best way to install this package is to use ``pip``:

.. code:: sh

   pip install isabelle-client

One can also download and run the client together with Isabelle in a
Docker contanier:

.. code:: sh

   docker build -t isabelle-client https://github.com/inpefess/isabelle-client.git
   docker run -it --rm -p 8888:8888 isabelle-client jupyter-lab --ip=0.0.0.0 --port=8888 --no-browser

How to use
==========

Follow the `usage
example <https://isabelle-client.readthedocs.io/en/latest/usage-example.html#usage-example>`__
from documentation, run the
`script <https://github.com/inpefess/isabelle-client/blob/master/examples/example.py>`__,
or use ``isabelle-client`` from a
`notebook <https://github.com/inpefess/isabelle-client/blob/master/examples/example.ipynb>`__,
e.g. with
`Binder <https://mybinder.org/v2/gh/inpefess/isabelle-client/HEAD?labpath=example.ipynb>`__.

How to Contribute
=================

`Pull requests <https://github.com/inpefess/isabelle-client/pulls>`__
are welcome. To start:

.. code:: sh

   git clone https://github.com/inpefess/isabelle-client
   cd isabelle-client
   # activate python virtual environment with Python 3.6+
   pip install -U pip
   pip install -U setuptools wheel poetry
   poetry install
   # recommended but not necessary
   pre-commit install

To check the code quality before creating a pull request, one might run
the script
`show_report.sh <https://github.com/inpefess/isabelle-client/blob/master/show_report.sh>`__.
It locally does nearly the same as the CI pipeline after the PR is
created.

Reporting issues or problems with the software
==============================================

Questions and bug reports are welcome on `the
tracker <https://github.com/inpefess/isabelle-client/issues>`__.

More documentation
==================

More documentation can be found
`here <https://isabelle-client.readthedocs.io/en/latest>`__.

Video example
=============

|video tutorial|.

How to cite
===========

If you’re writing a research paper, you can cite Isabelle client (and
Isabelle 2021) using the `following
DOI <https://doi.org/10.1007/978-3-030-81097-9_20>`__.

.. |PyPI version| image:: https://badge.fury.io/py/isabelle-client.svg
   :target: https://badge.fury.io/py/isabelle-client
.. |CircleCI| image:: https://circleci.com/gh/inpefess/isabelle-client.svg?style=svg
   :target: https://circleci.com/gh/inpefess/isabelle-client
.. |Documentation Status| image:: https://readthedocs.org/projects/isabelle-client/badge/?version=latest
   :target: https://isabelle-client.readthedocs.io/en/latest/?badge=latest
.. |codecov| image:: https://codecov.io/gh/inpefess/isabelle-client/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/inpefess/isabelle-client
.. |Binder| image:: https://mybinder.org/badge_logo.svg
   :target: https://mybinder.org/v2/gh/inpefess/isabelle-client/HEAD?labpath=example.ipynb
.. |video tutorial| image:: ../../examples/tty.gif
