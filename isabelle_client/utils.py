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
from typing import Tuple

from isabelle_client.isabelle__client import IsabelleClient


def get_isabelle_client(server_info: str) -> IsabelleClient:
    """
    get an instance of ``IsabelleClient`` from server info

    >>> server_inf = 'server "test" = 127.0.0.1:10000 (password "pass")'
    >>> print(get_isabelle_client(server_inf).port)
    10000
    >>> get_isabelle_client("wrong")
    Traceback (most recent call last):
        ...
    ValueError: Unexpected server info: wrong

    :param server_info: a line returned by a server on start
    :returns: an ``isabelle`` client
    """
    match = re.compile(
        r"server \".*\" = (.*):(.*) \(password \"(.*)\"\)"
    ).match(server_info)
    if match is None:
        raise ValueError(f"Unexpected server info: {server_info}")
    address, port, password = match.groups()
    isabelle_client = IsabelleClient(address, int(port), password)
    return isabelle_client


async def async_start_isabelle_server() -> Tuple[
    str, asyncio.subprocess.Process
]:
    """
    a technical function

    >>> from unittest.mock import patch, AsyncMock, Mock
    >>> server = Mock()
    >>> server.stdout = Mock()
    >>> server.stdout.readline = AsyncMock(return_value=b"test_info")
    >>> server_builder = AsyncMock(return_value=server)
    >>> with patch("asyncio.create_subprocess_exec", server_builder):
    ...     print(asyncio.run(async_start_isabelle_server())[0])
    test_info
    >>> server_builder.assert_awaited_once()
    >>> server.stdout.readline.assert_awaited_once()
    >>> server.stdout = None
    >>> server_builder = AsyncMock(return_value=server)
    >>> with patch("asyncio.create_subprocess_exec", server_builder):
    ...     print(asyncio.run(async_start_isabelle_server())[0])
    Traceback (most recent call last):
        ...
    ValueError: Failed to start server
    """
    isabelle_server = await asyncio.create_subprocess_exec(
        "isabelle", "server", stdout=asyncio.subprocess.PIPE
    )
    if isabelle_server.stdout is None:
        raise ValueError("Failed to start server")
    server_info = (await isabelle_server.stdout.readline()).decode("utf-8")
    return (server_info, isabelle_server)


def start_isabelle_server() -> Tuple[str, asyncio.subprocess.Process]:
    """
    start ``isabelle`` server

    >>> from unittest.mock import patch, AsyncMock
    >>> with patch(
    ...     "isabelle_client.utils.async_start_isabelle_server",
    ...     AsyncMock(return_value="TestIsabelleServer")
    ... ):
    ...     print(start_isabelle_server())
    TestIsabelleServer

    :return: a line of server info and server process
    """
    return asyncio.run(async_start_isabelle_server())
