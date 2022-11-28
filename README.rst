|Binder|\ |PyPI version|\ |Anaconda version|\ |CircleCI|\ |Documentation Status|\ |codecov|

Python client for Isabelle server
=================================

``isabelle-client`` is a TCP client for
`Isabelle <https://isabelle.in.tum.de>`__ server. For more information
about the server see part 4 of `the Isabelle system
manual <https://isabelle.in.tum.de/dist/Isabelle2021-1/doc/system.pdf>`__.

How to Install
==============

The best way to install this package is to use ``pip``:

.. code:: sh

   pip install isabelle-client


Another option is to use Anaconda:

.. code:: sh
	  
   conda install -c conda-forge isabelle-client 

One can also download and run the client together with Isabelle in a
Docker contanier:

.. code:: sh

   docker build -t isabelle-client https://github.com/inpefess/isabelle-client.git
   docker run -it --rm -p 8888:8888 isabelle-client jupyter-lab --ip=0.0.0.0 --port=8888

How to use
==========

.. code:: python

   from isabelle_client import get_isabelle_client, start_isabelle_server
   
   # start Isabelle server
   server_info, _ = start_isabelle_server()
   # create a client object
   isabelle = get_isabelle_client(server_info)
   # send a theory file from the current directory to the server
   response = isabelle.use_theories(
       theories=["Example"], master_dir=".", watchdog_timeout=0
   )
   # shut the server down
   isabelle.shutdown()


For more details, follow the `usage
example <https://isabelle-client.readthedocs.io/en/latest/usage-example.html#usage-example>`__
from documentation, run the
`script <https://github.com/inpefess/isabelle-client/blob/master/examples/example.py>`__,
or use ``isabelle-client`` from a
`notebook <https://github.com/inpefess/isabelle-client/blob/master/examples/example.ipynb>`__,
e.g. with
`Binder <https://mybinder.org/v2/gh/inpefess/isabelle-client/HEAD?labpath=isabelle-client-examples/example.ipynb>`__ (Binder might fail with 'Failed to create temporary user for ...' error which is `well known <https://mybinder-sre.readthedocs.io/en/latest/incident-reports/2018-02-20-jupyterlab-announcement.html>`__ and related neither to ``isabelle-client`` nor to the provided ``Dockerfile``. If that happens, try to run Docker as described in the section above).

More documentation
==================

More documentation can be found
`here <https://isabelle-client.readthedocs.io/en/latest>`__.

Similar Packages
================

There are Python clients to other interactive theorem provers, for
example:

* `for Lean
  <https://github.com/leanprover-community/lean-client-python>`__
* `for Coq <https://github.com/IBM/pycoq>`__
* `another one for Coq <https://github.com/ejgallego/pycoq>`__

Modules helping to inetract with Isabelle server from Python are
parts of the `Proving for Fun
<https://github.com/maxhaslbeck/proving-contest-backends>`__ project.

How to cite
===========

If you’re writing a research paper, you can cite Isabelle client
using the `following DOI
<https://doi.org/10.1007/978-3-031-16681-5_24>`__. You can also cite
Isabelle 2021 (and the earlier version of the client) with `this
DOI <https://doi.org/10.1007/978-3-030-81097-9_20>`__.

How to Contribute
=================

Please follow `the contribution guide <https://isabelle-client.readthedocs.io/en/latest/contributing.html>`__ while adhering to `the code of conduct <https://isabelle-client.readthedocs.io/en/latest/code-of-conduct.html>`__.


.. |PyPI version| image:: https://badge.fury.io/py/isabelle-client.svg
   :target: https://badge.fury.io/py/isabelle-client
.. |Anaconda version| image:: https://anaconda.org/conda-forge/isabelle-client/badges/version.svg
   :target: https://anaconda.org/conda-forge/isabelle-client
.. |CircleCI| image:: https://circleci.com/gh/inpefess/isabelle-client.svg?style=svg
   :target: https://circleci.com/gh/inpefess/isabelle-client
.. |Documentation Status| image:: https://readthedocs.org/projects/isabelle-client/badge/?version=latest
   :target: https://isabelle-client.readthedocs.io/en/latest/?badge=latest
.. |codecov| image:: https://codecov.io/gh/inpefess/isabelle-client/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/inpefess/isabelle-client
.. |Binder| image:: https://mybinder.org/badge_logo.svg
   :target: https://mybinder.org/v2/gh/inpefess/isabelle-client/HEAD?labpath=isabelle-client-examples/example.ipynb
