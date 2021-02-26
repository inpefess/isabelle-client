"""
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
"""
import logging

from isabelle_client import get_isabelle_client_from_server_info


def main():
    """ using ``isabelle`` client """
    # first, run Isabelle server in the same directory as this script:
    # isabelle server > server.info
    isabelle = get_isabelle_client_from_server_info("server.info")
    # we will log all the messages from the server to stdout
    logging.basicConfig(filename="out.log")
    isabelle.logger = logging.getLogger()
    isabelle.logger.setLevel(logging.INFO)
    # now we can send a theory file from this directory to the server
    # and get a response
    isabelle.use_theories(theories=["dummy"], master_dir=".")
    isabelle.execute_command("echo 42", asynchronous=False)


if __name__ == "__main__":
    main()
