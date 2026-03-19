    :Author: boris

.. contents::

1 Basic usage example.
----------------------

1.1 In what case to use
~~~~~~~~~~~~~~~~~~~~~~~

This client might be useful if:

- you have a machine with Isabelle installed

- you have scripts for automatic generation of theory files in Python

- you want to communicate with the server not using `Scala <https://scala-lang.org/>`_ and/or
  `Standard ML <https://polyml.org/>`_

1.2 In what environment to use
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The client works well in scripts and in Jupyter notebooks. For the
latter, one has to enable nested event loops first. Please refer to
``nest_asyncio`` `documentation <https://pypi.org/project/nest-asyncio/>`_.

1.3 Starting Isabelle server
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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

1.4 Interacting with Isabelle server
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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

    print(isabelle.help())

::

    [HelpResult(response_type=<IsabelleResponseType.OK: 'OK'>, response_body=['cancel', 'echo', 'help', 'purge_theories', 'session_build', 'session_start', 'session_stop', 'shutdown', 'use_theories'], response_length=118)]


Let's suppose we have a ``Example.thy`` theory file in our working directory which we, e.g. generated with another Python script

::

    theory Example
    imports Main
    begin
    lemma "\<forall> x. \<exists> y. x = y"
    by auto
    end

First, we start a session:

.. code:: python

    session_start_responses = isabelle.session_start()
    print(session_start_responses)

::

    [TaskOK(response_type=<IsabelleResponseType.OK: 'OK'>, response_body=Task(task='e4af2bc9-77ae-461f-b9cb-abe5b4a73140'), response_length=None), NotificationResponse(response_type=<IsabelleResponseType.NOTE: 'NOTE'>, response_body=MessageNotification(kind='writeln', message='Session Pure/Pure', pos=None, task='e4af2bc9-77ae-461f-b9cb-abe5b4a73140'), response_length=117), NotificationResponse(response_type=<IsabelleResponseType.NOTE: 'NOTE'>, response_body=MessageNotification(kind='writeln', message='Session Misc/Tools', pos=None, task='e4af2bc9-77ae-461f-b9cb-abe5b4a73140'), response_length=118), NotificationResponse(response_type=<IsabelleResponseType.NOTE: 'NOTE'>, response_body=MessageNotification(kind='writeln', message='Session HOL/HOL (main)', pos=None, task='e4af2bc9-77ae-461f-b9cb-abe5b4a73140'), response_length=122), NotificationResponse(response_type=<IsabelleResponseType.NOTE: 'NOTE'>, response_body=MessageNotification(kind='writeln', message='Session Doc/Main (doc)', pos=None, task='e4af2bc9-77ae-461f-b9cb-abe5b4a73140'), response_length=122), NotificationResponse(response_type=<IsabelleResponseType.NOTE: 'NOTE'>, response_body=MessageNotification(kind='writeln', message='Session Pure/Pure', pos=None, task='e4af2bc9-77ae-461f-b9cb-abe5b4a73140'), response_length=117), NotificationResponse(response_type=<IsabelleResponseType.NOTE: 'NOTE'>, response_body=MessageNotification(kind='writeln', message='Session Misc/Tools', pos=None, task='e4af2bc9-77ae-461f-b9cb-abe5b4a73140'), response_length=118), NotificationResponse(response_type=<IsabelleResponseType.NOTE: 'NOTE'>, response_body=MessageNotification(kind='writeln', message='Session HOL/HOL (main)', pos=None, task='e4af2bc9-77ae-461f-b9cb-abe5b4a73140'), response_length=122), NotificationResponse(response_type=<IsabelleResponseType.NOTE: 'NOTE'>, response_body=MessageNotification(kind='writeln', message='Session Doc/Main (doc)', pos=None, task='e4af2bc9-77ae-461f-b9cb-abe5b4a73140'), response_length=122), NotificationResponse(response_type=<IsabelleResponseType.NOTE: 'NOTE'>, response_body=MessageNotification(kind='writeln', message='Starting session Main ...', pos=None, task='e4af2bc9-77ae-461f-b9cb-abe5b4a73140'), response_length=126), SessionStartRegularResponse(response_type=<IsabelleResponseType.FINISHED: 'FINISHED'>, response_body=SessionStartRegularResult(task='e4af2bc9-77ae-461f-b9cb-abe5b4a73140', session_id='09019a3d-e074-4322-b113-463bf8afda7f', tmp_dir='/tmp/isabelle-boris/server_session33887120446384605'), response_length=173)]


Then we can send this theory file to the server and get a response

.. code:: python

    session_id = session_start_responses[-1].response_body.session_id
    print(isabelle.use_theories(
        session_id=session_id,
        theories=["Example"],
        master_dir="../examples"
    ))

::

    [TaskOK(response_type=<IsabelleResponseType.OK: 'OK'>, response_body=Task(task='afad4267-7888-40bb-a4f6-2cad90115612'), response_length=None), TaskOK(response_type=<IsabelleResponseType.NOTE: 'NOTE'>, response_body=Task(task='afad4267-7888-40bb-a4f6-2cad90115612'), response_length=161), TaskOK(response_type=<IsabelleResponseType.NOTE: 'NOTE'>, response_body=Task(task='afad4267-7888-40bb-a4f6-2cad90115612'), response_length=161), TaskOK(response_type=<IsabelleResponseType.NOTE: 'NOTE'>, response_body=Task(task='afad4267-7888-40bb-a4f6-2cad90115612'), response_length=163), UseTheoriesResponse(response_type=<IsabelleResponseType.FINISHED: 'FINISHED'>, response_body=UseTheoriesResults(ok=True, errors=[], nodes=[NodeResult(node_name='../examples/Example.thy', theory_name='Draft.Example', status=NodeStatus(ok=True, total=7, unprocessed=0, running=0, warned=0, failed=0, finished=7, canceled=False, consolidated=True, percentage=100), messages=[Message(kind='writeln', message='theorem \\<forall>x. \\<exists>y. x = y', pos=Position(line=5, offset=59, end_offset=61, file='../examples/Example.thy', id=None))], exports=[])]), response_length=482)]


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

    print(
        isabelle.session_build(
            dirs=["../examples/"], session="examples"
        )
    )

::

    [TaskOK(response_type=<IsabelleResponseType.OK: 'OK'>, response_body=Task(task='ded48e14-81dd-49e9-b4f1-64a6578cf768'), response_length=None), NotificationResponse(response_type=<IsabelleResponseType.NOTE: 'NOTE'>, response_body=MessageNotification(kind='writeln', message='Session Pure/Pure', pos=None, task='ded48e14-81dd-49e9-b4f1-64a6578cf768'), response_length=117), NotificationResponse(response_type=<IsabelleResponseType.NOTE: 'NOTE'>, response_body=MessageNotification(kind='writeln', message='Session Misc/Tools', pos=None, task='ded48e14-81dd-49e9-b4f1-64a6578cf768'), response_length=118), NotificationResponse(response_type=<IsabelleResponseType.NOTE: 'NOTE'>, response_body=MessageNotification(kind='writeln', message='Session HOL/HOL (main)', pos=None, task='ded48e14-81dd-49e9-b4f1-64a6578cf768'), response_length=122), NotificationResponse(response_type=<IsabelleResponseType.NOTE: 'NOTE'>, response_body=MessageNotification(kind='writeln', message='Session Unsorted/examples', pos=None, task='ded48e14-81dd-49e9-b4f1-64a6578cf768'), response_length=125), NotificationResponse(response_type=<IsabelleResponseType.NOTE: 'NOTE'>, response_body=MessageNotification(kind='writeln', message='Session Pure/Pure', pos=None, task='ded48e14-81dd-49e9-b4f1-64a6578cf768'), response_length=117), NotificationResponse(response_type=<IsabelleResponseType.NOTE: 'NOTE'>, response_body=MessageNotification(kind='writeln', message='Session Misc/Tools', pos=None, task='ded48e14-81dd-49e9-b4f1-64a6578cf768'), response_length=118), NotificationResponse(response_type=<IsabelleResponseType.NOTE: 'NOTE'>, response_body=MessageNotification(kind='writeln', message='Session HOL/HOL (main)', pos=None, task='ded48e14-81dd-49e9-b4f1-64a6578cf768'), response_length=122), NotificationResponse(response_type=<IsabelleResponseType.NOTE: 'NOTE'>, response_body=MessageNotification(kind='writeln', message='Session Unsorted/examples', pos=None, task='ded48e14-81dd-49e9-b4f1-64a6578cf768'), response_length=125), SessionBuildRegularResponse(response_type=<IsabelleResponseType.FINISHED: 'FINISHED'>, response_body=SessionBuildRegularResult(ok=True, return_code=0, sessions=[SessionBuildResult(session='Pure', ok=True, return_code=0, timeout=False, timing=Timing(elapsed=0.0, cpu=0.0, gc=0.0)), SessionBuildResult(session='HOL', ok=True, return_code=0, timeout=False, timing=Timing(elapsed=0.0, cpu=0.0, gc=0.0)), SessionBuildResult(session='examples', ok=True, return_code=0, timeout=False, timing=Timing(elapsed=0.0, cpu=0.0, gc=0.0))], task='ded48e14-81dd-49e9-b4f1-64a6578cf768', response_type=<IsabelleResponseType.FINISHED: 'FINISHED'>), response_length=396)]


One can also issue a free-form command, e.g.

.. code:: python

    import asyncio

    print(asyncio.run(isabelle.execute_command("echo 42", asynchronous=False)))

::

    [IsabelleResponse(response_type=<IsabelleResponseType.OK: 'OK'>, response_body=42, response_length=None)]


Finally, we can shut the server down.

.. code:: python

    print(isabelle.shutdown())

::

    response_type=<IsabelleResponseType.OK: 'OK'>
