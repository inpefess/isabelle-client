# Copyright 2021-2023 Boris Shminke
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
Utilities
==========

A collection of different useful functions.
"""
import asyncio
import os
import re
import socketserver
import sys
from typing import Optional, Tuple

from isabelle_client.isabelle__client import IsabelleClient

if sys.version_info.major == 3 and sys.version_info.minor >= 9:
    # pylint: disable=no-name-in-module, import-error
    from importlib.resources import files  # type: ignore
else:  # pragma: no cover
    from importlib_resources import files  # pylint: disable=import-error


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
) -> Tuple[str, asyncio.subprocess.Process]:
    """
    Start Isabelle server.

    >>> import os
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
    if sys.platform == "win32":
        return start_isabelle_server_win32(args)  # pragma: no cover

    async def async_call() -> Tuple[str, asyncio.subprocess.Process]:
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
) -> Tuple[str, asyncio.subprocess.Process]:  # pragma: no cover
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

    async def async_call() -> Tuple[str, asyncio.subprocess.Process]:
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
        request = self.request.recv(1024).decode("utf-8").split("\n")[0]
        if request == "ping":
            self.request.sendall(b"5\n")
            self.request.sendall(b"# !!!")
        else:
            self.request.sendall(b'OK "connection OK"\n')
            self.request.sendall(b"7\n")
            self.request.sendall(b"FAILED\n")


class DummyTCPHandler(socketserver.BaseRequestHandler):
    """A dummy handler to mock Isabelle server."""

    _request_response = {
        "shutdown": b"OK",
        "cancel": b"OK",
        "purge_theories": b'OK {"purged": [], "retained": []}',
        "help": b'OK ["echo", "help"]',
    }

    def handle(self):
        """Return something similar to what Isabelle server does."""
        request = self.request.recv(1024).decode("utf-8").split("\n")[1]
        command = request.split(" ")[0]
        self.request.sendall(b'OK "connection OK"\n')
        if command == "echo":
            self.request.sendall(f"OK{request.split(' ')[1]}\n".encode())
        self.request.sendall(
            self._request_response.get(
                command, b'43\nFINISHED {"session_id": "test_session_id"}\n'
            )
        )


class ReusableDummyTCPServer(socketserver.TCPServer):
    """Ignore TIME-WAIT during testing."""

    allow_reuse_address = True
