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
import io
import re
import socket
from dataclasses import dataclass
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
            + " "
            + self.response_body
        )


def get_delimited_message(
    tcp_socket: socket.socket,
    delimiter: str = "\n",
    encoding: str = "utf-8",
) -> str:
    """
    get a delimited (not fixed-length)response from a TCP socket

    >>> from unittest.mock import Mock
    >>> tcp_socket = Mock()
    >>> tcp_socket.recv = Mock(side_effect=[b"4", b"2" b"\\n"])
    >>> print(get_delimited_message(tcp_socket))
    42

    :param tcp_socket: a TCP socket to receive data from
    :param delimiter: a character which marks the end of response
    :param encoding: a socket encoding
    :returns: decoded string response
    """
    response = " "
    while response[-1] != delimiter:
        response += tcp_socket.recv(1).decode(encoding)
    return response[1:]


def get_fixed_length_message(
    tcp_socket: socket.socket,
    message_length: int,
    chunk_size: int = 8196,
    encoding: str = "utf-8",
) -> str:
    """
    get a response of a fixed length from a TCP socket

    >>> from unittest.mock import Mock
    >>> tcp_socket = Mock()
    >>> tcp_socket.recv = Mock(
    ...     side_effect=[b'FINISHED {"session_id": "session_id__42"}\\n']
    ... )
    >>> print(get_fixed_length_message(tcp_socket, 42))
    FINISHED {"session_id": "session_id__42"}

    :param tcp_socket: a TCP socket to receive data from
    :param message_length: a number of bytes to read as a message
    :param chunk_size: the maximal number of bytes to get at one time
    :param encoding: a socket encoding
    :returns: decoded string response
    """
    response = b""
    read_length = 0
    while read_length < message_length:
        response += tcp_socket.recv(
            min(chunk_size, message_length - read_length)
        )
        read_length = len(response)
    return response.decode(encoding)


def get_response_from_isabelle(tcp_socket: socket.socket) -> IsabelleResponse:
    """
    get a response from ``isabelle`` server:
    * a carriage-return delimited message or
    * a fixed length message after a carriage-return delimited message with
    only one integer number denoting length

    >>> from unittest.mock import Mock
    >>> tcp_socket = Mock()
    >>> tcp_socket.recv = Mock(
    ...     side_effect=[
    ...         b"4",
    ...         b"2",
    ...         b"\\n",
    ...         b'FINISHED {"session_id": "session_id__42"}\\n',
    ...     ]
    ... )
    >>> print(str(get_response_from_isabelle(tcp_socket)))
    42
    FINISHED {"session_id": "session_id__42"}

    :param tcp_socket: a TCP socket to receive data from
    :returns: a response from ``isabelle``
    """
    response = get_delimited_message(tcp_socket)
    match = re.compile(r"(\d+)\n").match(response)
    length = int(match.group(1)) if match is not None else None
    if length is not None:
        response = get_fixed_length_message(tcp_socket, length)
    match = re.compile(r"(\w+) (.*)").match(response)
    if match is None:
        raise ValueError(f"Unexpected response from Isabelle: {response}")
    return IsabelleResponse(match.group(1), match.group(2), length)


def get_final_message(
    tcp_socket: socket.socket,
    final_message: Set[str],
    log_file: Optional[io.TextIOWrapper] = None,
) -> IsabelleResponse:
    """
    gets responses from ``isabelle`` server until a message of specified
    'final' type arrives

    >>> from unittest.mock import Mock
    >>> tcp_socket = Mock()
    >>> tcp_socket.recv = Mock(
    ...    side_effect=[
    ...        b"O", b"K", b" ", b"i", b"\\n",
    ...        b"4", b"2", b"\\n",
    ...        b'FINISHED {"session_id": "session_id__42"}\\n'
    ...    ]
    ... )
    >>> log_file = Mock()
    >>> log_file.write = Mock()
    >>> print(str(get_final_message(
    ...     tcp_socket, {"FINISHED"}, log_file
    ... )))
    42
    FINISHED {"session_id": "session_id__42"}
    >>> print(log_file.write.mock_calls)
    [call('OK i'), call('42\\nFINISHED {"session_id": "session_id__42"}')]
    >>> tcp_socket.recv = Mock(
    ...     side_effect=[b"5", b"\\n", b"wrong"]
    ... )
    >>> print(get_final_message(tcp_socket, {"FINISHED"}))
    Traceback (most recent call last):
        ...
    ValueError: Unexpected response from Isabelle: wrong

    :param tcp_socket:  a TCP socket to ``isabelle`` server
    :param final_message: a set of possible final message types
    :param log_file: a file for writing a copy of all messages
    :returns: the final response from ``isabelle`` server
    """
    response = IsabelleResponse("", "")
    password_ok_received = False
    while (
        response.response_type not in final_message or not password_ok_received
    ):
        if response.response_type == "OK":
            password_ok_received = True
        response = get_response_from_isabelle(tcp_socket)
        if log_file is not None:
            log_file.write(str(response))
    return response
