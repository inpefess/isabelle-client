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
import re
import socket
from dataclasses import dataclass
from typing import Optional


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


def get_response_from_isabelle(tcp_socket: socket.socket) -> str:
    """
    get a response of a fixed length from a TCP socket

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
    >>> print(get_response_from_isabelle(tcp_socket))
    42
    FINISHED {"session_id": "session_id__42"}

    :param tcp_socket: a TCP socket to receive data from
    :returns: decoded string response
    """
    response = get_delimited_message(tcp_socket)
    match = re.compile(r"(\d+)\n").match(response)
    if match is not None:
        response += get_fixed_length_message(tcp_socket, int(match.group(1)))
    return response


@dataclass
class IsabelleResponse:
    """
    a response from an ``isabelle`` server

    >>> print(IsabelleResponse("OK", '{"ok": "true"}').response_length)
    None

    :param response_type: an all capitals word like ``FINISHED`` or ``ERROR``
    :param response_body: a JSON-formatted response
    :param response_length: a length of JSON response
    """

    response_type: str
    response_body: str
    # pylint: disable=unsubscriptable-object
    response_length: Optional[int] = None
