# Copyright 2025 Boris Shminke
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
Data Models
===========
"""  # noqa: D205, D400

import json
from enum import Enum
from typing import Any

from pydantic import BaseModel


class IsabelleResponseType(Enum):
    """Isabelle server response type."""

    OK = "OK"
    FINISHED = "FINISHED"
    NOTE = "NOTE"
    FAILED = "FAILED"
    ERROR = "ERROR"


ASYNCHRONOUS_FINAL_MESSAGES = {
    IsabelleResponseType.FAILED,
    IsabelleResponseType.FINISHED,
    IsabelleResponseType.ERROR,
}
SYNCHRONOUS_FINAL_MESSAGES = {
    IsabelleResponseType.OK,
    IsabelleResponseType.ERROR,
}


class IsabelleResponse(BaseModel):
    """
    A response from an Isabelle server.

    .. attribute :: response_type

        an all capitals word like ``FINISHED`` or ``ERROR``

    .. attribute :: response_body

         a JSON-formatted response

    .. attribute :: response_length

        a length of JSON response
    """

    response_type: IsabelleResponseType
    response_body: Any
    response_length: int | None = None

    def __str__(self) -> str:
        """
        Pretty print Isabelle server response.

        :returns: a string representation of Isabelle server response
        """
        return (
            (
                f"{self.response_length}\n"
                if self.response_length is not None
                else ""
            )
            + self.response_type.value
            + (" " if self.response_body else "")
            + json.dumps(self.response_body)
        )


class HelpResult(IsabelleResponse):
    """Result of the ``help`` command."""

    response_body: list[str]
