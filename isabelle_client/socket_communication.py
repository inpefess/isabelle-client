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
Socket Communication
=====================

A collection of functions for TCP communication.
"""  # noqa: D205, D400

import asyncio
import re
from dataclasses import dataclass
from logging import Logger
from typing import Optional
from collections.abc import AsyncGenerator


@dataclass
class IsabelleResponse:
    """
    A response from an Isabelle server.

    .. attribute :: response_type

        an all capitals word like ``FINISHED`` or ``ERROR``

    .. attribute :: response_body

         a JSON-formatted response

    .. attribute :: response_length

        a length of JSON response
    """

    response_type: str
    response_body: str
    response_length: Optional[int] = None

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
            + self.response_type
            + (" " if self.response_body != "" else "")
            + self.response_body
        )


async def get_response_from_isabelle(
    reader: asyncio.StreamReader,
) -> IsabelleResponse:
    r"""
    Get a response from Isabelle server.

    Format:

    * a carriage-return delimited message or
    * a fixed length message after a carriage-return delimited message with
      only one integer number denoting length

    >>> async def awaiter():
    ...     test_reader, test_writer = await asyncio.open_connection(
    ...     "localhost", 9999
    ... )
    ...     test_writer.write(b"test_password\nhelp\n")
    ...     result = [str(await get_response_from_isabelle(test_reader))]
    ...     result += [str(await get_response_from_isabelle(test_reader))]
    ...     return result
    >>> print(asyncio.run(awaiter()))
    ['OK {"isabelle_id":"mock","isabelle_name":"Isabelle2024"}', '118\nOK [...]
    >>> async def awaiter():
    ...     test_reader, test_writer = await asyncio.open_connection(
    ...     "localhost", 9998
    ... )
    ...     test_writer.write(b"test_password\nhelp\n")
    ...     result = [str(await get_response_from_isabelle(test_reader))]
    ...     result += [str(await get_response_from_isabelle(test_reader))]
    ...     return result
    >>> print(asyncio.run(awaiter()))
    Traceback (most recent call last):
      ...
    ValueError: Unexpected response from Isabelle: # !!!

    :param reader: a StreamReader connected to a server
    :returns: a response from Isabelle
    :raises ValueError: if the server response is malformed
    """
    response = (await reader.readline()).decode("utf-8")
    match = re.compile(r"(\d+)\n").match(response)
    length = int(match.group(1)) if match is not None else None
    if length is not None:
        response = (await reader.readexactly(length)).decode("utf-8")
    if (match := re.compile("(\\w+) ?(.*)").match(response)) is None:
        raise ValueError(f"Unexpected response from Isabelle: {response}")
    return IsabelleResponse(match.group(1), match.group(2), length)


async def get_final_message(
    reader: asyncio.StreamReader,
    final_message: set[str],
    logger: Optional[Logger] = None,
) -> AsyncGenerator[IsabelleResponse]:
    r"""
    Get responses from Isabelle server.

    (until a message of specified 'final' type arrives)

    >>> test_logger = getfixture("mock_logger")
    >>> async def awaiter():
    ...     test_reader, test_writer = await asyncio.open_connection(
    ...     "localhost", 9999
    ... )
    ...     test_writer.write(b"test_password\nhelp\n")
    ...     result = []
    ...     async for message in get_final_message(
    ...         test_reader, {"OK"}, test_logger
    ...     ):
    ...         result.append(message)
    ...     return result
    >>> for response in asyncio.run(awaiter()):
    ...     print(response)
    OK {"isabelle_id":"mock","isabelle_name":"Isabelle2024"}
    118
    OK ["cancel","echo","help","purge_theories","session_build",...]
    >>> print(test_logger.info.mock_calls)
    [call('OK {"isabelle_id":"mock","isabelle_name":"Isabelle2024"}'),
     call('118\nOK ["cancel","echo","help","purge_theories","session_buil...')]

    :param reader: a ``StreamReader`` connected to Isabelle server
    :param final_message: a set of possible final message types
    :param logger: a logger where to send all server replies
    :yields: the final response from Isabelle server
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
        yield response
