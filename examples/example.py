# Copyright 2021-2022 Boris Shminke
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
""" An example of the client usage """
import asyncio
import logging

from isabelle_client import get_isabelle_client, start_isabelle_server


def main():
    """using Isabelle client"""
    # first, we start Isabelle server
    server_info, _ = start_isabelle_server(
        name="test", port=9999, log_file="server.log"
    )
    isabelle = get_isabelle_client(server_info)
    # we will log all the messages from the server to a file
    isabelle.logger = logging.getLogger()
    isabelle.logger.setLevel(logging.INFO)
    isabelle.logger.addHandler(logging.FileHandler("session.log"))
    # now we can send a theory file from this directory to the server
    # and get a response
    isabelle.use_theories(
        theories=["Example"], master_dir=".", watchdog_timeout=0
    )
    # or we can build a session document using ROOT and root.tex files from it
    isabelle.session_build(dirs=["."], session="examples")
    # or we can issue a free-text command through TCP
    asyncio.run(isabelle.execute_command("echo 42", asynchronous=False))
    isabelle.shutdown()


if __name__ == "__main__":
    main()
