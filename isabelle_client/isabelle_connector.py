# Copyright 2023-2025 Boris Shminke
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
Isabelle Connector
===================

A connector to the Isabelle server, hiding server interactions.
"""  # noqa: D205, D400

import json
import logging
from typing import Optional
from uuid import uuid4

from isabelle_client.socket_communication import IsabelleResponseType
from isabelle_client.utils import (
    get_isabelle_client,
    get_or_create_working_directory,
    start_isabelle_server,
)


class IsabelleTheoryError(RuntimeError):
    """Raised when the Isabelle response contains errors."""


class IsabelleConnector:
    r"""
    A connector to the Isabelle server, hiding server interactions.

    :param working_directory: a directory for storing the server logs,
            temporary theory files etc.

    >>> import os
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

    def __init__(self, working_directory: Optional[str] = None) -> None:  # noqa: D107
        self._working_directory = get_or_create_working_directory(
            working_directory
        )
        server_info, self._server_process = start_isabelle_server(
            log_file=str(self._working_directory / "isabelle-server.log")
        )
        self._client = get_isabelle_client(server_info=server_info)
        self._client.logger = logging.getLogger()
        self._client.logger.setLevel(logging.INFO)
        self._client.logger.addHandler(
            logging.FileHandler(str(self._working_directory / "session.log"))
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
        (self._working_directory / f"{theory_name}.thy").write_text(
            f"theory {theory_name}\n"
            "imports Main\n"
            "begin\n"
            f'lemma "{lemma_text}"\n'
            f"{task}\n"
            "end\n"
        )
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
            theories=[theory_name], master_dir=str(self._working_directory)
        )
        for isabelle_response in validation_result:
            if (
                isabelle_response.response_type
                == IsabelleResponseType.FINISHED
            ):
                json_response = json.loads(isabelle_response.response_body)
                if errors := json_response["errors"]:
                    raise IsabelleTheoryError(errors[0]["message"])
        return True

    @property
    def working_directory(self) -> str:
        """Get working directory."""
        return str(self._working_directory)
