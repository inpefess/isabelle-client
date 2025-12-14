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
import re
import socketserver
import sys
import tempfile
from enum import Enum
from importlib.resources import files
from pathlib import Path
from uuid import uuid4

from isabelle_client.isabelle_client import IsabelleClient

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
        msg = f"Unexpected server info: {server_info}"
        raise ValueError(msg)
    address, port, password = match.groups()
    return IsabelleClient(address, int(port), password)


def start_isabelle_server(
    log_file: str | None = None,
    name: str | None = None,
    port: int | None = None,
) -> tuple[str, asyncio.subprocess.Process]:
    """
    Start Isabelle server.

    >>> import os
    >>> os.environ["PATH"] = "src/isabelle_client/resources:$PATH"
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
        + (f" -p {port!s}" if port is not None else "")
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
        msg = "No stdout while starting the server."  # pragma: no cover
        raise ValueError(msg)  # pragma: no cover

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
    # pyrefly: ignore [deprecated, missing-attribute]
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

    async def async_call() -> tuple[str, asyncio.subprocess.Process]:
        """
        Start Isabelle server in Cygwin asynchronously.

        :returns: a line of server info and server process
        :raises ValueError: if no stdout seen after starting the server
        """
        isabelle_server = await asyncio.create_subprocess_exec(
            str(
                files("isabelle_client")
                .joinpath("resources")
                .joinpath("Cygwin-Isabelle.bat")
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
        msg = "No stdout while starting the server."
        raise ValueError(msg)

    return asyncio.run(async_call())


class BuggyDummyTCPHandler(socketserver.BaseRequestHandler):
    """A dummy handler to mock bugs in Isabelle server response."""

    def handle(self) -> None:
        """Return something weird."""
        self.request.recv(4096).decode("utf-8").split("\n")[1]
        self.request.sendall(b"5\n")
        self.request.sendall(b"# !!!")


class DummyTCPHandler(socketserver.BaseRequestHandler):
    """A dummy handler to mock Isabelle server."""

    def _mock_command_execution(self, command: str, arguments: str) -> None:
        filename = command
        if (
            command == IsabelleServerCommands.USE_THEORIES.value
            and (theory_name := json.loads(arguments)["theories"][0]) != "Mock"
        ):
            filename += f".{theory_name}"
        self.request.sendall(
            files("isabelle_client")
            .joinpath("resources")
            .joinpath("isabelle-responses")
            .joinpath(filename)
            .read_text()
            .encode()
        )

    def handle(self) -> None:
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


def get_or_create_working_directory(working_directory: str | None) -> Path:
    """
    Get existing or create a randomly named directory.

    :param working_directory: directory name
    :returns: (possibly new) directory name
    """
    new_working_directory = (
        Path(working_directory)
        if working_directory is not None
        else Path(tempfile.mkdtemp()) / str(uuid4())
    )
    if not Path(new_working_directory).exists():
        Path(new_working_directory).mkdir()
    return new_working_directory
