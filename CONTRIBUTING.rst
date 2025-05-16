============
Contributing
============

Contributions are welcome, and they are greatly appreciated! Every
little bit helps, and credit will always be given.

You can contribute in many ways:

Types of Contributions
----------------------

Report Bugs
~~~~~~~~~~~

Report bugs at https://github.com/inpefess/isabelle-client/issues

If you are reporting a bug, please include:

* Your operating system name and version.
* Any details about your local setup that might be helpful in
  troubleshooting.
* Detailed steps to reproduce the bug.

Fix Bugs
~~~~~~~~

Look through the GitHub issues for bugs. Anything tagged with "bug"
and "help wanted" is open to whoever wants to implement a fix for it.

Implement Features
~~~~~~~~~~~~~~~~~~

Look through the GitHub issues for features. Anything tagged with
"enhancement" and "help wanted" is open to whoever wants to implement
it.

Write Documentation
~~~~~~~~~~~~~~~~~~~

Python client for Isabelle server could always use more
documentation, whether as part of the official docs, in docstrings,
or even on the web in blog posts, articles, and such.

Submit Feedback
~~~~~~~~~~~~~~~

The best way to send feedback is to file an issue at
https://github.com/inpefess/isabelle-client/issues.

If you are proposing a new feature:

* Explain in detail how it would work.
* Keep the scope as narrow as possible, to make it easier to
  implement.
* Remember that this is a volunteer-driven project, and that
  contributions are welcome :)

Get Started!
------------

Ready to contribute? Here's how to set up `isabelle-client` for local
development. Please note this documentation assumes you already have
`Git
<https://git-scm.com/book/en/v2/Getting-Started-Installing-Git>`__
installed and ready to go.

1. `Fork <https://github.com/inpefess/isabelle-client/fork>`__ the
   `isabelle-client` repo on GitHub.

1. Clone your fork locally:

   .. code:: sh

      cd path_for_the_repo
      git clone git@github.com:YOUR_NAME/isabelle-client.git

1. Install
   [poetry](https://python-poetry.org/docs/#installing-with-the-official-installer).
      
1. Now you can install all the things you need for development (this
   command will also create a virtual environment in `.venv`
   subfolder):

   .. code:: bash

      poetry install --all-groups
      source .venv/bin/activate
      # recommended but not necessary
      pre-commit install

1. Create a branch for local development:

   .. code:: bash

      git checkout -b name-of-your-bugfix-or-feature

   Now you can make your changes locally.

1. When you're done making changes, check that your changes pass code
   quality checks.

   .. code:: bash

      ruff check
      pydocstyle isabelle_client
      pylint isabelle_client
      mypy isabelle_client

1. The next step would be to run the test cases. `isabelle-client`
   uses pytest and all the existing tests are `doctests
   <https://docs.python.org/3/library/doctest.html>`__.

   .. code:: bash

      pytest

7. If your contribution is a bug fix or new feature, you may want to
   add a test to the existing test suite. If possible, do it by
   doctest, not a dedicates test case file.

1. Commit your changes and push your branch to GitHub:

   .. code:: bash

      git add .
      git commit -m "Your detailed description of your changes."
      git push origin name-of-your-bugfix-or-feature

1. Submit a pull request through the GitHub website.


Pull Request Guidelines
-----------------------

Before you submit a pull request, check that it meets these
guidelines:

1. The pull request should include tests.

2. If the pull request adds functionality, the docs should be
   updated. Put your new functionality into a function with a
   docstring, and add the feature to the list in README.rst.

3. The pull request should work for Python 3.9, 3.10, 3.11, 3.12 and
   3.13. Check https://github.com/inpefess/isabelle-client/pulls and
   make sure that the tests pass for all supported Python versions.
