# Copyright 2023 Boris Shminke
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
# noqa: D205, D400
"""
Isabelle Connector
===================

A connector to the Isabelle server, hiding server interactions.
"""
import json
import logging
import os
import tempfile
from typing import Optional
from uuid import uuid4

from isabelle_client.utils import get_isabelle_client, start_isabelle_server


class IsabelleTheoryError(RuntimeError):
    """Raised when the Isabelle response contains errors."""


class IsabelleConnector:
    r"""
    A connector to the Isabelle server, hiding server interactions.

    >>> os.environ["PATH"] = "isabelle_client/resources:$PATH"
    >>> connector = IsabelleConnector()
    >>> print(connector.working_directory)
    /...
    >>> connector.verify_lemma(
    ...     "\<forall> x. \<exists> y. x = y", theory="Mock")
    True
    >>> connector.verify_lemma(
    ...     "\<forall> x. \<forall> y. x = y", theory="Fail")
    Traceback (most recent call last):
     ...
    isabelle...Error: Failed to finish proof\<^here>:
    goal (1 subgoal):
     1. \<And>x y. x = y
    """

    def _get_or_create_working_directory(
        self, working_directory: Optional[str]
    ) -> str:
        new_working_directory = (
            working_directory
            if working_directory is not None
            else os.path.join(tempfile.mkdtemp(), str(uuid4()))
        )
        if not os.path.exists(new_working_directory):
            os.mkdir(new_working_directory)
        return new_working_directory

    def __init__(self, working_directory: Optional[str] = None):
        """
        Start the server and create a client.

        :param working_directory: a directory for storing the server logs,
            temporary theory files etc.
        """
        self._working_directory = self._get_or_create_working_directory(
            working_directory
        )
        server_info, self._server_process = start_isabelle_server(
            log_file=os.path.join(
                self._working_directory, "isabelle-server.log"
            )
        )
        self._client = get_isabelle_client(server_info=server_info)
        self._client.logger = logging.getLogger()
        self._client.logger.setLevel(logging.INFO)
        self._client.logger.addHandler(
            logging.FileHandler(
                os.path.join(self._working_directory, "session.log")
            )
        )

    def _write_temp_theory_file(
        self,
        lemma_text: str,
        task: str,
        theory: Optional[str] = None,
    ) -> str:
        theory_name = (
            "T" + str(uuid4()).replace("-", "") if theory is None else theory
        )
        with open(
            os.path.join(self._working_directory, f"{theory_name}.thy"),
            "w",
            encoding="utf8",
        ) as theory_file:
            theory_file.write(f"theory {theory_name}\n")
            theory_file.write("imports Main\n")
            theory_file.write("begin\n")
            theory_file.write(f'lemma "{lemma_text}"\n')
            theory_file.write(f"{task}\n")
            theory_file.write("end\n")
        return theory_name

    def verify_lemma(
        self,
        lemma_text: str,
        task: str = "by auto",
        theory: Optional[str] = None,
    ) -> bool:
        """
        Verify a lemma statement using the Isabelle server.

        :param lemma_text: (hopefully) syntactically valid Isabelle lemma
        :param task: how to prove lemma. ``"by auto"`` by default
        :param theory: (for tests) fixed named for theory file
        :returns: True if validation successful
        :raises IsabelleTheoryError: if validation failed
        """
        theory_name = self._write_temp_theory_file(lemma_text, task, theory)
        validation_result = self._client.use_theories(
            theories=[theory_name], master_dir=self._working_directory
        )
        for isabelle_response in validation_result:
            if isabelle_response.response_type == "FINISHED":
                json_response = json.loads(isabelle_response.response_body)
                errors = json_response["errors"]
                if errors:
                    raise IsabelleTheoryError(errors[0]["message"])
        return True

    @property
    def working_directory(self) -> str:
        """Get working directory."""
        return self._working_directory
