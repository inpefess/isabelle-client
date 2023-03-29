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
# noqa: D205
"""Fixtures for unit tests live here."""
import threading
from typing import Generator, Tuple
from unittest.mock import Mock

from pytest import fixture

from isabelle_client.utils import (
    BuggyDummyTCPHandler,
    DummyTCPHandler,
    ReusableDummyTCPServer,
)


@fixture(autouse=True, scope="session")
def tcp_servers() -> (
    Generator[
        Tuple[ReusableDummyTCPServer, ReusableDummyTCPServer], None, None
    ]
):
    """
    Get a simplistic TCP server mocking Isabelle server behaviour.

    :returns: an instance of a mock working server and a mock buggy server
    """
    with ReusableDummyTCPServer(
        ("localhost", 9999), DummyTCPHandler
    ) as server, ReusableDummyTCPServer(
        ("localhost", 9998), BuggyDummyTCPHandler
    ) as buggy_server:
        thread = threading.Thread(target=server.serve_forever)
        thread.daemon = True
        thread.start()
        buggy_thread = threading.Thread(target=buggy_server.serve_forever)
        buggy_thread.daemon = True
        buggy_thread.start()
        yield server, buggy_server


@fixture
def mock_logger() -> Mock:
    """
    Get a mock for logger to spy on ``info`` calls.

    :returns: mock logger
    """
    logger = Mock()
    logger.info = Mock()
    return logger
