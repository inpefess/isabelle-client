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
import asyncio
import re
from dataclasses import dataclass
from logging import Logger
from typing import Optional, Set


@dataclass
class IsabelleResponse:
    """
    a response from an ``isabelle`` server

    :param response_type: an all capitals word like ``FINISHED`` or ``ERROR``
    :param response_body: a JSON-formatted response
    :param response_length: a length of JSON response
    """

    response_type: str
    response_body: str
    response_length: Optional[int] = None

    def __str__(self):
        return (
            (
                f"{self.response_length}\n"
                if self.response_length is not None
                else ""
            )
            + self.response_type
            + (" " if self.response_body != "" else "")
            + self.response_body
        )


async def get_response_from_isabelle(
    reader: asyncio.StreamReader,
) -> IsabelleResponse:
    """
    get a response from ``isabelle`` server:
    * a carriage-return delimited message or
    * a fixed length message after a carriage-return delimited message with
    only one integer number denoting length

    >>> from unittest.mock import Mock, AsyncMock
    >>> reader = Mock()
    >>> reader.readline = AsyncMock(return_value=b"42\\n")
    >>> reader.readexactly = AsyncMock(
    ...     return_value=b'FINISHED {"session_id": "session_id__42"}\\n'
    ... )
    >>> print(str(asyncio.run(get_response_from_isabelle(reader))))
    42
    FINISHED {"session_id": "session_id__42"}
    >>> reader.readline = AsyncMock(return_value=b"7\\n")
    >>> reader.readexactly = AsyncMock(return_value=b'# wrong')
    >>> print(str(asyncio.run(get_response_from_isabelle(reader))))
    Traceback (most recent call last):
      ...
    ValueError: Unexpected response from Isabelle: # wrong

    :param reader: a StreamReader connected to a server
    :returns: a response from ``isabelle``
    """
    response = (await reader.readline()).decode("utf-8")
    match = re.compile(r"(\d+)\n").match(response)
    length = int(match.group(1)) if match is not None else None
    if length is not None:
        response = (await reader.readexactly(length)).decode("utf-8")
    match = re.compile(r"(\w+) ?(.*)").match(response)
    if match is None:
        raise ValueError(f"Unexpected response from Isabelle: {response}")
    return IsabelleResponse(match.group(1), match.group(2), length)


async def get_final_message(
    reader: asyncio.StreamReader,
    final_message: Set[str],
    logger: Optional[Logger] = None,
) -> IsabelleResponse:
    """
    gets responses from ``isabelle`` server until a message of specified
    'final' type arrives

    >>> from unittest.mock import Mock, AsyncMock
    >>> reader = Mock()
    >>> reader.readline = AsyncMock(side_effect=[b"OK\\n", b"40\\n"])
    >>> reader.readexactly = AsyncMock(side_effect=[
    ...     b'FINISHED {"session_id": "test_session"}\\n'
    ...    ]
    ... )
    >>> test_logger = Mock()
    >>> test_logger.info = Mock()
    >>> print(str(asyncio.run(get_final_message(
    ...     reader, {"FINISHED"}, test_logger
    ... ))))
    40
    FINISHED {"session_id": "test_session"}
    >>> print(test_logger.info.mock_calls)
    [call('OK'), call('40\\nFINISHED {"session_id": "test_session"}')]

    :param tcp_socket:  a TCP socket to ``isabelle`` server
    :param final_message: a set of possible final message types
    :param logger: a logger where to send all server replies
    :returns: the final response from ``isabelle`` server
    """
    response = IsabelleResponse("", "")
    password_ok_received = False
    while (
        response.response_type not in final_message or not password_ok_received
    ):
        if response.response_type == "OK":
            password_ok_received = True
        response = await get_response_from_isabelle(reader)
        if logger is not None:
            logger.info(str(response))
    return response
