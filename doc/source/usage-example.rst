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
  
Basic usage example
********************

In what case to use
====================

This client might be useful if:

* you have an Isabelle server instance running
* you have scripts for automatic generation of theory files in Python
* you want to communicate with the server not using Scala and/or StandardML

First, we need to start an Isabelle server::
  
    from isabelle_client import start_isabelle_server

    server_info, _ = start_isabelle_server(
        name="test", port=9999, log_file="server.log"
    )

We could also start the server outside this script and use its info::

    isabelle server > server.info
    
Now let's create a client to our server ::

    from isabelle_client import get_isabelle_client

    isabelle = get_isabelle_client(server_info)

We will log all the messages from the server to a file ::
  
    import logging

    isabelle.logger = logging.getLogger()
    isabelle.logger.setLevel(logging.INFO)
    isabelle.logger.addHandler(logging.FileHandler("session.log"))

This client has several methods implemented to communicate with the server Python-style, e.g.::

    isabelle.use_theories(theories=["Example"], master_dir=".")

In this command it's supposed that we have a ``Example.thy`` theory file in our working directory which we, e.g. generated with another Python script.

One can also issue a free-form command, e.g.::

    from isabelle_client import async_run

    async_run(isabelle.execute_command("echo 42", asynchronous=False))
