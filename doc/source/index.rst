..
  Copyright 2021 Boris Shminke

  Licensed under the Apache License, Version 2.0 (the "License");
  you may not use this file except in compliance with the License.
  You may obtain a copy of the License at

      https://www.apache.org/licenses/LICENSE-2.0

  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License.

Welcome to Isabelle client documentation!
===========================================

A client for `Isabelle`_ server. For more information about the server see part 4 of `the Isabelle system manual`_.

How to install
===============

The best way to install this client is to use ``pip``::

    pip install isabelle-client

In what case to use
====================

This client might be useful if:

* you have an Isabelle server instance running
* you have scripts for automatic generation of theory files in Python
* you want to communicate with the server not using Scala and/or StandardML

See also :ref:`usage-example`.

How to contribute
==================

Pull requests on are welcome. To start::

    git clone https://github.com/inpefess/isabelle-client
    cd isabelle-client
    # activate python virtual environment with Python 3.6+
    pip install -U pip
    pip install -U setuptools wheel poetry
    poetry install
    # recommended but not necessary
    pre-commit install

To check the code quality before creating a pull request, one might run the script ``show_report.sh``. It locally does nearly the same as the CI pipeline after the PR is created.

    
.. toctree::
   :maxdepth: 2
   :caption: Contents:
	     
   usage-example
   package-documentation

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. _Isabelle: https://isabelle.in.tum.de
.. _the Isabelle system manual: https://isabelle.in.tum.de/dist/Isabelle2021/doc/system.pdf
