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
Sledgehammer Connector
=======================

A connector to the Isabelle server, hiding server interactions.
"""
import json
from typing import Dict, Optional

from isabelle_client.isabelle_connector import IsabelleConnector


class SledgehammerConnector(IsabelleConnector):
    r"""
    A connector to the Isabelle server parsing Sledgehammer response.

    >>> import os
    >>> os.environ["PATH"] = "isabelle_client/resources:$PATH"
    >>> sledgehammer = SledgehammerConnector()
    >>> sledgehammer.parse_sledgehammer_response(
    ...     "\<forall> x. \<exists> y. x = y", theory="Sledgehammer")
    {'verit': 'by simp', 'zipperposition': 'by simp',...spass': 'by fastforce'}
    """

    def parse_sledgehammer_response(
        self, lemma_text: str, theory: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Verify a lemma statement using the Isabelle server.

        :param lemma_text: (hopefully) syntactically valid Isabelle lemma
        :param theory: (for tests) fixed named for theory file
        :returns: parsed Sledgehammer response
        """
        theory_name = self._write_temp_theory_file(
            lemma_text=lemma_text, theory=theory, task="sledgehammer\noops"
        )
        sledgehammer_responses = self._client.use_theories(
            theories=[theory_name], master_dir=self._working_directory
        )
        messages = []
        for sledgehammer_response in sledgehammer_responses:
            if sledgehammer_response.response_type == "FINISHED":
                json_response = json.loads(sledgehammer_response.response_body)
                messages = [
                    node["message"].split(": ")
                    for node in json_response["nodes"][0]["messages"]
                    if ": Try this: " in node["message"]
                ]
        return {
            message[0]: message[2].split("(")[0].strip()
            for message in messages
        }
