# Copyright 2021-2022 Boris Shminke
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
# noqa: D205
"""Fixtures for unit tests live here."""
import socketserver
import threading
from typing import Generator, Tuple
from unittest.mock import Mock

from pytest import fixture


class BuggyTCPHandler(socketserver.BaseRequestHandler):
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

    # pylint: disable=too-many-statements
    def handle(self):
        """Return something similar to what Isabelle server does."""
        request = self.request.recv(1024).decode("utf-8").split("\n")[1]
        command = request.split(" ")[0]
        self.request.sendall(b'OK "connection OK"\n')

        if command == "echo":
            self.request.sendall(
                f"OK{request.split(' ')[1]}\n".encode("utf-8")
            )
        elif command in {"shutdown", "cancel"}:
            self.request.sendall(b"OK")
        elif command == "purge_theories":
            self.request.sendall(b'OK {"purged": [], "retained": []}')
        elif command == "help":
            self.request.sendall(b'OK ["echo", "help"]')
        else:
            self.request.sendall(b"43\n")
            self.request.sendall(
                b'FINISHED {"session_id": "test_session_id"}\n'
            )


class ReusableTCPServer(socketserver.TCPServer):
    """Ignore TIME-WAIT during testing."""

    allow_reuse_address = True


@fixture(autouse=True, scope="session")
def tcp_servers() -> Generator[
    Tuple[ReusableTCPServer, ReusableTCPServer], None, None
]:
    """
    Get a simplistic TCP server mocking Isabelle server behaviour.

    :returns: an instance of a mock working server and a mock buggy server
    """
    with ReusableTCPServer(
        ("localhost", 9999), DummyTCPHandler
    ) as server, ReusableTCPServer(
        ("localhost", 9998), BuggyTCPHandler
    ) as buggy_server:
        thread = threading.Thread(target=server.serve_forever)
        thread.daemon = True
        thread.start()
        buggy_thread = threading.Thread(target=buggy_server.serve_forever)
        buggy_thread.daemon = True
        buggy_thread.start()
        yield server, buggy_server


@fixture
def mock_logger():
    """Get a mock for logger to spy on ``info`` calls."""
    logger = Mock()
    logger.info = Mock()
    return logger
