# Copyright 2021-2025 Boris Shminke
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
Basic usage example.
====================
"""  # noqa: D205

# %%
# In what case to use
# -------------------
#
# This client might be useful if:
#
# * you have a machine with Isabelle installed
# * you have scripts for automatic generation of theory files in Python
# * you want to communicate with the server not using
#   `Scala <https://scala-lang.org/>`__ and/or
#   `Standard ML <https://polyml.org/>`__

# %%
# In what environment to use
# --------------------------
#
# The client works well in scripts and in Jupyter notebooks. For the
# latter, one has to enable nested event loops first. Please refer to
# ``nest_asyncio`` `documentation
# <https://pypi.org/project/nest-asyncio/>`__.

# %%
# Starting Isabelle server
# ------------------------
# First, we need to start an Isabelle server

from isabelle_client import start_isabelle_server

server_info, _ = start_isabelle_server(
    name="test", port=9999, log_file="server.log"
)

# %%
# .. warning::
#   When using `start_isabelle_server
#   <package-documentation.html#isabelle_client.utils.start_isabelle_server>`__
#   utility function in Python REPL or terminal IPython, shutting the server
#   down within the same session is known to cause a runtime error on exit from
#   the session. This behaviour is related to a `well known issue
#   <https://ipython.readthedocs.io/en/stable/interactive/autoawait.html#difference-between-terminal-ipython-and-ipykernel>`__.

# %%
# We could also start the server outside this script and use its info (on
# Windows, this is done in Cygwin)::
#
#    isabelle server

# %%
# Interacting with Isabelle server
# --------------------------------
# Let's create a client to our server

from isabelle_client import get_isabelle_client

isabelle = get_isabelle_client(server_info)

# %%
# We will log all the messages from the server to a file

import logging

isabelle.logger = logging.getLogger()
isabelle.logger.setLevel(logging.INFO)
isabelle.logger.addHandler(logging.FileHandler("session.log"))

# %%
# Isabelle client supports all the commands implemented in Isabelle server

from pprint import pprint

pprint(isabelle.help())

# %%
# Let's suppose we have a ``Example.thy`` theory file in our working directory
# which we, e.g. generated with another Python script
#
# .. literalinclude:: ../../examples/Example.thy
#

# %%
# We can send this theory file to the server and get a response

pprint(isabelle.use_theories(theories=["Example"], master_dir="."))

# %%
# or we can build a session document using ``./ROOT`` file
#
# .. literalinclude:: ../../examples/ROOT
#
# and ``./document/root.tex`` file
#
# .. literalinclude:: ../../examples/document/root.tex
#    :language: tex
#

import json

pprint(
    json.loads(
        isabelle.session_build(dirs=["."], session="examples")[
            -1
        ].response_body
    )
)

# %%
# One can also issue a free-form command, e.g.

import asyncio

pprint(asyncio.run(isabelle.execute_command("echo 42", asynchronous=False)))

# %%
# Finally, we can shut the server down.

pprint(isabelle.shutdown())
