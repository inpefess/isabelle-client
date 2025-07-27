Basic usage example.
--------------------

In what case to use
~~~~~~~~~~~~~~~~~~~

This client might be useful if:

- you have a machine with Isabelle installed

- you have scripts for automatic generation of theory files in Python

- you want to communicate with the server not using `Scala <https://scala-lang.org/>`_ and/or
  `Standard ML <https://polyml.org/>`_

In what environment to use
~~~~~~~~~~~~~~~~~~~~~~~~~~

The client works well in scripts and in Jupyter notebooks. For the
latter, one has to enable nested event loops first. Please refer to
``nest_asyncio`` `documentation <https://pypi.org/project/nest-asyncio/>`_.

Starting Isabelle server
~~~~~~~~~~~~~~~~~~~~~~~~

First, we need to start an Isabelle server

.. code:: python

    from isabelle_client import start_isabelle_server

    server_info, _ = start_isabelle_server(
        name="test", port=9999, log_file="server.log"
    )

When using ``start_isabelle_server`` utility function in Python REPL or
terminal IPython, shutting the server down within the same session is
known to cause a runtime error on exit from the session. This
behaviour is related to a `well known issue <https://ipython.readthedocs.io/en/stable/interactive/autoawait.html#difference-between-terminal-ipython-and-ipykernel>`_.

We could also start the server outside this script and use its info (on Windows, this is done in Cygwin)

::

    isabelle server

Interacting with Isabelle server
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Let's create a client to our server

.. code:: python

    from isabelle_client import get_isabelle_client

    isabelle = get_isabelle_client(server_info)

We will log all the messages from the server to a file

.. code:: python

    import logging

    isabelle.logger = logging.getLogger()
    isabelle.logger.setLevel(logging.INFO)
    isabelle.logger.addHandler(logging.FileHandler("session.log"))

Isabelle client supports all the commands implemented in Isabelle server

.. code:: python

    from pprint import pprint

    pprint(isabelle.help())

::

    [IsabelleResponse(response_type=<IsabelleResponseType.OK: 'OK'>,
                      response_body='{"isabelle_id":"4b875a4c83b0","isabelle_name":"Isabelle2025"}',
                      response_length=None),
     IsabelleResponse(response_type=<IsabelleResponseType.OK: 'OK'>,
                      response_body='["cancel","echo","help","purge_theories","session_build","session_start","session_stop","shutdown","use_theories"]',
                      response_length=118)]


Let's suppose we have a ``Example.thy`` theory file in our working directory which we, e.g. generated with another Python script

::

    theory Example
    imports Main
    begin
    lemma "\<forall> x. \<exists> y. x = y"
    by auto
    end

We can send this theory file to the server and get a response

.. code:: python

    pprint(isabelle.use_theories(
        theories=["Example"],
        master_dir="../examples"
    ))

::

    [IsabelleResponse(response_type=<IsabelleResponseType.OK: 'OK'>,
                      response_body='{"isabelle_id":"4b875a4c83b0","isabelle_name":"Isabelle2025"}',
                      response_length=None),
     IsabelleResponse(response_type=<IsabelleResponseType.OK: 'OK'>,
                      response_body='{"task":"3ed0d564-ecb3-4241-8eb1-c40131bad8a4"}',
                      response_length=None),
     IsabelleResponse(response_type=<IsabelleResponseType.NOTE: 'NOTE'>,
                      response_body='{"percentage":71,"task":"3ed0d564-ecb3-4241-8eb1-c40131bad8a4","message":"theory '
                                    'Draft.Example '
                                    '71%","kind":"writeln","session":"","theory":"Draft.Example"}',
                      response_length=161),
     IsabelleResponse(response_type=<IsabelleResponseType.NOTE: 'NOTE'>,
                      response_body='{"percentage":99,"task":"3ed0d564-ecb3-4241-8eb1-c40131bad8a4","message":"theory '
                                    'Draft.Example '
                                    '99%","kind":"writeln","session":"","theory":"Draft.Example"}',
                      response_length=161),
     IsabelleResponse(response_type=<IsabelleResponseType.NOTE: 'NOTE'>,
                      response_body='{"percentage":100,"task":"3ed0d564-ecb3-4241-8eb1-c40131bad8a4","message":"theory '
                                    'Draft.Example '
                                    '100%","kind":"writeln","session":"","theory":"Draft.Example"}',
                      response_length=163),
     IsabelleResponse(response_type=<IsabelleResponseType.FINISHED: 'FINISHED'>,
                      response_body='{"ok":true,"errors":[],"nodes":[{"messages":[{"kind":"writeln","message":"theorem '
                                    '\\\\<forall>x. \\\\<exists>y. x = '
                                    'y","pos":{"line":5,"offset":59,"end_offset":61,"file":"../examples/Example.thy"}}],"exports":[],"status":{"percentage":100,"unprocessed":0,"running":0,"finished":7,"failed":0,"total":7,"consolidated":true,"canceled":false,"ok":true,"warned":0},"theory_name":"Draft.Example","node_name":"../examples/Example.thy"}],"task":"3ed0d564-ecb3-4241-8eb1-c40131bad8a4"}',
                      response_length=482)]

or we can build a session document using ``./ROOT`` file

::

    session examples = HOL +
      options [document = pdf, document_output = "output"]
      theories
        Example
      document_files
        "root.tex"

and ``./document/root.tex`` file

.. code:: tex

    \documentclass{article}
    \usepackage{isabelle,isabellesym}
    \begin{document}
    \input{session}
    \end{document}

.. code:: python

    import json

    pprint(
        json.loads(
            isabelle.session_build(
                dirs=["../examples/"], session="examples"
            )[-1].response_body
        )
    )

::

    {'ok': True,
     'return_code': 0,
     'sessions': [{'ok': True,
                   'return_code': 0,
                   'session': 'Pure',
                   'timeout': False,
                   'timing': {'cpu': 0, 'elapsed': 0, 'gc': 0}},
                  {'ok': True,
                   'return_code': 0,
                   'session': 'HOL',
                   'timeout': False,
                   'timing': {'cpu': 0, 'elapsed': 0, 'gc': 0}},
                  {'ok': True,
                   'return_code': 0,
                   'session': 'examples',
                   'timeout': False,
                   'timing': {'cpu': 0, 'elapsed': 0, 'gc': 0}}],
     'task': '9aa6e7c3-79a0-401c-8292-6f870df5a02b'}

One can also issue a free-form command, e.g.

.. code:: python

    import asyncio

    pprint(asyncio.run(isabelle.execute_command("echo 42", asynchronous=False)))

::

    [IsabelleResponse(response_type=<IsabelleResponseType.OK: 'OK'>,
                      response_body='{"isabelle_id":"4b875a4c83b0","isabelle_name":"Isabelle2025"}',
                      response_length=None),
     IsabelleResponse(response_type=<IsabelleResponseType.OK: 'OK'>,
                      response_body='42',
                      response_length=None)]


Finally, we can shut the server down.

.. code:: python

    pprint(isabelle.shutdown())

::

    [IsabelleResponse(response_type=<IsabelleResponseType.OK: 'OK'>,
                      response_body='{"isabelle_id":"4b875a4c83b0","isabelle_name":"Isabelle2025"}',
                      response_length=None),
     IsabelleResponse(response_type=<IsabelleResponseType.OK: 'OK'>,
                      response_body='',
                      response_length=None)]
