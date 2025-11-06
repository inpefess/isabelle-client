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


class SimpleIsabelleResponse(BaseModel):
    """
    Isabelle response with no body.

    .. attribute :: response_type

    an all capitals word like ``FINISHED`` or ``ERROR``

    """

    response_type: IsabelleResponseType


class IsabelleResponse(SimpleIsabelleResponse):
    """
    A response from an Isabelle server.

    .. attribute :: response_body

         a JSON-formatted response

    .. attribute :: response_length

        a length of JSON response
    """

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
            + (
                self.response_body.model_dump_json()
                if isinstance(self.response_body, BaseModel)
                else json.dumps(self.response_body)
            )
        )


class HelpResult(IsabelleResponse):
    """Result of the ``help`` command."""

    response_body: list[str]


class Task(BaseModel):
    """Identifies a newly created asynchronous task."""

    task: str


class TaskOK(IsabelleResponse):
    """Immediate result of task creation."""

    response_body: Task


class Position(BaseModel):
    """Describes a source position within Isabelle text."""

    line: int | None = None
    offset: int | None = None
    end_offset: int | None = None
    file: str | None = None
    id: int | None = None


class Export(BaseModel):
    """Export."""

    name: str
    base64: bool
    body: str


class Message(BaseModel):
    """Message."""

    kind: str
    message: str
    pos: Position | None = None


class Node(BaseModel):
    """Theory node."""

    node_name: str
    theory_name: str


class NodeStatus(BaseModel):
    """Represents a formal theory node status."""

    ok: bool
    total: int
    unprocessed: int
    running: int
    warned: int
    failed: int
    finished: int
    canceled: bool
    consolidated: bool
    percentage: int


class NodeResult(BaseModel):
    """Node result."""

    node_name: str
    theory_name: str
    status: NodeStatus
    messages: list[Message]
    exports: list[Export]


class UseTheoriesResults(BaseModel):
    """Regular result of ``use_theories`` command."""

    ok: bool
    errors: list[Message]
    nodes: list[NodeResult]


class UseTheoriesResponse(IsabelleResponse):
    """Final response of ``use_theories`` command."""

    response_body: UseTheoriesResults


class PurgeTheoriesResult(BaseModel):
    """Result of ``purge_theories`` command."""

    purged: list[Node]
    retained: list[Node]


class PurgeTheoriesResponse(IsabelleResponse):
    """Response of ``purge_theories`` command."""

    response_body: PurgeTheoriesResult


class Timing(BaseModel):
    """Isabelle timing information in seconds."""

    elapsed: float
    cpu: float
    gc: float


class SessionBuildResult(BaseModel):
    """Session build result."""

    session: str
    ok: bool
    return_code: int
    timeout: bool
    timing: Timing


class SessionBuildResults(BaseModel):
    """Session build results."""

    ok: bool
    return_code: int
    sessions: list[SessionBuildResult]


class ErrorMessage(BaseModel):
    """Error message."""

    kind: str = "error"
    message: str


class SessionBuildRegularResult(Task, SessionBuildResults):
    """Session build regular result."""

    response_type: IsabelleResponseType = IsabelleResponseType.FINISHED


class SessionStartErrorResult(Task, ErrorMessage):
    """Session start error result."""

    response_type: IsabelleResponseType = IsabelleResponseType.FAILED


class UseTheoriesErrorResult(SessionStartErrorResult):
    """Error result of ``use_theories`` command."""


class SessionBuildErrorResult(SessionStartErrorResult, SessionBuildResults):
    """Session build error result."""


class SessionBuildRegularResponse(IsabelleResponse):
    """Regular response of ``session_build`` command."""

    response_body: SessionBuildRegularResult


class SessionStartRegularResult(Task):
    """Regular result of ``session_start`` command."""

    session_id: str
    tmp_dir: str


class SessionStartRegularResponse(IsabelleResponse):
    """Regular response of ``session_start`` command."""

    response_body: SessionStartRegularResult


class SessionBuildErrorResponse(IsabelleResponse):
    """Error response of ``session_build`` command."""

    response_body: SessionBuildErrorResult


class SessionStartErrorResponse(IsabelleResponse):
    """Error response of ``session_start`` command."""

    response_body: SessionStartErrorResult


class UseTheoriesErrorResponse(IsabelleResponse):
    """Error response of ``use_theories`` command."""

    response_body: UseTheoriesErrorResult


class TheoryProgress(BaseModel):
    """Theory progress."""

    kind: str = "writeln"
    message: str
    theory: str
    session: str
    percentage: int | None = None


class TheoryProgressNotification(Task, TheoryProgress):
    """Theory progress notification."""


class MessageNotification(Task, Message):
    """Message notification."""


class NotificationResponse(IsabelleResponse):
    """Notification response."""

    response_body: TheoryProgressNotification | MessageNotification


class SessionStopResult:
    """Session stop result."""

    ok: bool
    return_code: int


class SessionStopRegularResult(Task, SessionStopResult):
    """Session stop regular result."""

    response_type: IsabelleResponseType = IsabelleResponseType.FINISHED


class SessionStopErrorResult(Task, ErrorMessage, SessionStopResult):
    """Session stop regular result."""

    response_type: IsabelleResponseType = IsabelleResponseType.FAILED


class SessionStopErrorResponse(IsabelleResponse):
    """Error response of ``session_stop`` command."""

    response_body: SessionStopErrorResult


class SessionStopRegularResponse(IsabelleResponse):
    """Regular response of ``session_stop`` command."""

    response_body: SessionStopRegularResult
