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
Utilities
==========

A collection of different useful functions.
"""  # noqa: D205, D400

import asyncio
import json
import os
import re
import socketserver
import sys
from enum import Enum
from importlib.resources import files
from typing import Optional

from isabelle_client.isabelle__client import IsabelleClient

MS_WINDOWS = "win32"


class IsabelleServerCommands(Enum):
    """Supported Isabelle server commands."""

    HELP = "help"
    USE_THEORIES = "use_theories"
    ECHO = "echo"


def get_isabelle_client(server_info: str) -> IsabelleClient:
    """
    Get an instance of ``IsabelleClient`` from server info.

    >>> server_inf = 'server "test" = 127.0.0.1:10000 (password "pass")'
    >>> print(get_isabelle_client(server_inf).port)
    10000
    >>> get_isabelle_client("wrong")
    Traceback (most recent call last):
        ...
    ValueError: Unexpected server info: wrong

    :param server_info: a line returned by a server on start
    :returns: an Isabelle client
    :raises ValueError: if the server response is malformed
    """
    match = re.compile(
        r"server \".*\" = (.*):(.*) \(password \"(.*)\"\)"
    ).match(server_info)
    if match is None:
        raise ValueError(f"Unexpected server info: {server_info}")
    address, port, password = match.groups()
    isabelle_client = IsabelleClient(address, int(port), password)
    return isabelle_client


def start_isabelle_server(
    log_file: Optional[str] = None,
    name: Optional[str] = None,
    port: Optional[int] = None,
) -> tuple[str, asyncio.subprocess.Process]:
    """
    Start Isabelle server.

    >>> os.environ["PATH"] = "isabelle_client/resources:$PATH"
    >>> print(start_isabelle_server()[0])
    server "isabelle" = 127.0.0.1:9999 (password "test_password")
    <BLANKLINE>

    :param log_file: a log file for exceptional output of internal server and
        session operations
    :param name: explicit server name (default: isabelle)
    :param port: explicit server port
    :returns: a line of server info and server process
    """
    args = (
        "server"
        + (f" -L {log_file}" if log_file is not None else "")
        + (f" -p {str(port)}" if port is not None else "")
        + (f" -n {name}" if name is not None else "")
    )
    if sys.platform == MS_WINDOWS:
        return start_isabelle_server_win32(args)  # pragma: no cover

    async def async_call() -> tuple[str, asyncio.subprocess.Process]:
        """
        Start Isabelle server asynchronously.

        :returns: a line of server info and server process
        :raises ValueError: if no stdout seen after starting the server
        """
        isabelle_server = await asyncio.create_subprocess_exec(
            "isabelle", *(args.split(" ")), stdout=asyncio.subprocess.PIPE
        )
        if isabelle_server.stdout is not None:
            return (await isabelle_server.stdout.readline()).decode(
                "utf-8"
            ), isabelle_server
        raise ValueError(
            "No stdout while startnig the server."
        )  # pragma: no cover

    return asyncio.run(async_call())


def start_isabelle_server_win32(
    args: str,
) -> tuple[str, asyncio.subprocess.Process]:  # pragma: no cover
    """
    Start Isabelle server on Windows.

    :param args: Isabelle server arguments string
    :returns: a line of server info and server process
    """
    # this line enables asyncio.create_subprocess_exec on Windows:
    # https://docs.python.org/3/library/asyncio-platforms.html#asyncio-windows-subprocess
    asyncio.set_event_loop_policy(
        asyncio.WindowsProactorEventLoopPolicy()  # type: ignore
    )

    async def async_call() -> tuple[str, asyncio.subprocess.Process]:
        """
        Start Isabelle server in Cygwin asynchronously.

        :returns: a line of server info and server process
        :raises ValueError: if no stdout seen after starting the server
        """
        isabelle_server = await asyncio.create_subprocess_exec(
            str(
                files("isabelle_client").joinpath(
                    os.path.join("resources", "Cygwin-Isabelle.bat")
                )
            ),
            args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        if isabelle_server.stdout is not None:
            server_info = (await isabelle_server.stdout.readline()).decode(
                "utf-8"
            )
            return server_info, isabelle_server
        raise ValueError("No stdout while startnig the server.")

    return asyncio.run(async_call())


class BuggyDummyTCPHandler(socketserver.BaseRequestHandler):
    """A dummy handler to mock bugs in Isabelle server response."""

    def handle(self):
        """Return something weird."""
        request = self.request.recv(4096).decode("utf-8").split("\n")[1]
        if request == IsabelleServerCommands.HELP.value:
            self.request.sendall(b"5\n")
            self.request.sendall(b"# !!!")
        else:
            self.request.sendall(
                b'OK {"isabelle_id":"mock","isabelle_name":"Isabelle2024"}\n'
            )
            self.request.sendall(b"ERROR UNEXPECTED\n")


class DummyTCPHandler(socketserver.BaseRequestHandler):
    """A dummy handler to mock Isabelle server."""

    def _mock_command_execution(self, command: str, arguments: str):
        filename = command
        if command == IsabelleServerCommands.USE_THEORIES.value:
            if (theory_name := json.loads(arguments)["theories"][0]) != "Mock":
                filename += f".{theory_name}"
        with open(
            str(
                files("isabelle_client").joinpath(
                    os.path.join("resources", "isabelle-responses", filename)
                )
            ),
            encoding="utf8",
        ) as mock_response_file:
            self.request.sendall(mock_response_file.read().encode())

    def handle(self):
        """Return something similar to what Isabelle server does."""
        request = self.request.recv(4096).decode("utf-8").split("\n")[1]
        command = request.split(" ")[0]
        arguments = request[len(command) :]
        self.request.sendall(
            b'OK {"isabelle_id":"mock","isabelle_name":"Isabelle2024"}\n'
        )
        if command == IsabelleServerCommands.ECHO.value:
            self.request.sendall(f"OK {arguments[1:]}\n".encode())
        else:
            self._mock_command_execution(command, arguments)


class ReusableDummyTCPServer(socketserver.TCPServer):
    """Ignore TIME-WAIT during testing."""

    allow_reuse_address = True
