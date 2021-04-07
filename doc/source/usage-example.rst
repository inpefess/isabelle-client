..
  Copyright 2021 Boris Shminke

  Licensed under the Apache License, Version 2.0 (the "License");
  you may not use this file except in compliance with the License.
  You may obtain a copy of the License at

      http://www.apache.org/licenses/LICENSE-2.0

  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License.
	   
.. _usage-example:

Basic usage example
====================

Let's suppose that Isabelle binary is on our ``PATH`` and we started an Isabelle server in working directory with the following command::

    isabelle server > server.pid

Now we can get an instance of Isabelle client to talk to this server from Python in a very simple way::

    from isabelle_client import get_isabelle_client_from_server_info
  
    isabelle = get_isabelle_client_from_server_info("server.pid")

It might be useful to log all replies from the server somewhere, e.g.::

    import logging

    logging.basicConfig(filename="out.log")
    isabelle.logger = logging.getLogger()

This client has several methods implemented to communicate with the server Python-style, e.g.::

    isabelle.use_theories(theories=["Dummy"], master_dir=".")

In this command it's supposed that we have a ``Dummy.thy`` theory file in our working directory which we, e.g. generated with another Python script.

One can also issue a free-form command, e.g.::

    isabelle.execute_command("echo 42", asynchronous=False)

