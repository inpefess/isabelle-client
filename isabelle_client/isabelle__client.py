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
Isabelle Client
================

A Python client to `Isabelle <https://isabelle.in.tum.de>`__ server
"""
import asyncio
import json
from enum import Enum
from logging import Logger
from typing import Any, Dict, List, Optional, Union

from isabelle_client.socket_communication import (
    IsabelleResponse,
    get_final_message,
)


class SynchronousResultType(Enum):
    """Synchronous results of a server reply."""

    OK = "OK"
    ERROR = "ERROR"


class AsynchronousResultType(Enum):
    """Asynchronous results of a server reply."""

    FAILED = "FAILED"
    FINISHED = "FINISHED"


class IsabelleClient:
    """A TCP client for an Isabelle server."""

    def __init__(
        self,
        address: str,
        port: int,
        password: str,
        logger: Optional[Logger] = None,
    ):
        """
        Create a client to Isabelle server.

        :param address: IP or a domain name
        :param port: a port number on which the server listens
        :param password: a password to access the server through TCP
        :param logger: a Python logger to store all requests to
            and replies from the server
        """
        self.address = address
        self.port = port
        self.password = password
        self.logger = logger

    async def execute_command(
        self,
        command: str,
        asynchronous: bool = True,
    ) -> List[IsabelleResponse]:
        r"""
        Execute a command and waits for results.

        >>> logger = getfixture("mock_logger")  # noqa: F821
        >>> isabelle_client = IsabelleClient(
        ...     "localhost", 9999, "test_password", logger
        ... )
        >>> test_response = asyncio.run(
        ...     isabelle_client.execute_command("unknown command")
        ... )
        >>> print(test_response[-1].response_type)
        ERROR
        >>> print(test_response[-1].response_body)
        "Bad command 'unknown'"
        >>> # error messages don't return the response length
        >>> print(test_response[-1].response_length)
        None
        >>> print(logger.info.mock_calls)
        [call('test_password\nunknown command\n'),
         call('OK {"isabelle_id":"mock","isabelle_name":"Isabelle2022"}'),
         call('ERROR "Bad command \'unknown\'"')]

        :param command: a full text of a command to Isabelle
        :param asynchronous: if ``False``, waits for ``OK``; else waits for
            ``FINISHED``
        :returns: a list of Isabelle server responses
        """
        final_message = (
            {
                AsynchronousResultType.FINISHED.value,
                AsynchronousResultType.FAILED.value,
                SynchronousResultType.ERROR.value,
            }
            if asynchronous
            else {
                SynchronousResultType.OK.value,
                SynchronousResultType.ERROR.value,
            }
        )
        reader, writer = await asyncio.open_connection(self.address, self.port)
        command = f"{self.password}\n{command}\n"
        writer.write(command.encode("utf-8"))
        await writer.drain()
        if self.logger is not None:
            self.logger.info(command)
        response = await get_final_message(reader, final_message, self.logger)
        return response

    def session_build(
        self,
        session: str,
        dirs: Optional[List[str]] = None,
        verbose: bool = False,
        **kwargs,
    ) -> List[IsabelleResponse]:
        """
        Build a session from ROOT file.

        >>> isabelle_client = IsabelleClient(
        ...     "localhost", 9999, "test_password"
        ... )
        >>> print(isabelle_client.session_build(
        ...     session="test_session", dirs=["."], verbose=True, options=[]
        ... )[-1])
        400
        FINISHED {"ok":true,"return_code":0,"sessions":[{"session":"Pure",...}

        :param session: a name of the session from ROOT file
        :param dirs: where to look for ROOT files
        :param verbose: set to ``True`` for extra verbosity
        :param kwargs: additional arguments
            (see Isabelle System manual for details)
        :returns: an Isabelle response
        """
        arguments: Dict[str, Union[str, List[str], bool]] = {
            "session": session,
            "verbose": verbose,
        }
        if dirs is not None:
            arguments["dirs"] = dirs
        arguments.update(kwargs)
        response = asyncio.run(
            self.execute_command(f"session_build {json.dumps(arguments)}")
        )
        return response

    def session_start(self, session: str = "Main", **kwargs) -> str:
        """
        Start a new session.

        >>> isabelle_client = IsabelleClient("localhost", 9998, "test")
        >>> print(isabelle_client.session_start(verbose=True))
        Traceback (most recent call last):
            ...
        ValueError: Unexpected response type: ERROR
        >>> isabelle_client = IsabelleClient("localhost", 9999, "test")
        >>> print(isabelle_client.session_start())
        167dd6d8-1eeb-4315-8022-c8c527d9bd87

        :param session: a name of a session to start
        :param kwargs: additional arguments
            (see Isabelle System manual for details)
        :returns: a ``session_id``
        :raises ValueError: if the server response is malformed
        """
        arguments = {"session": session}
        arguments.update(kwargs)
        response_list = asyncio.run(
            self.execute_command(f"session_start {json.dumps(arguments)}")
        )
        if (
            response_list[-1].response_type
            == AsynchronousResultType.FINISHED.value
        ):
            return json.loads(response_list[-1].response_body)["session_id"]
        raise ValueError(
            f"Unexpected response type: {response_list[-1].response_type}"
        )

    def session_stop(self, session_id: str) -> List[IsabelleResponse]:
        """
        Stop session with given ID.

        >>> isabelle_client = IsabelleClient("localhost", 9999, "test")
        >>> test_response = isabelle_client.session_stop("test")
        >>> print(test_response[-1].response_type)
        FINISHED

        :param session_id: a string ID of a session
        :returns: Isabelle server response
        """
        arguments = json.dumps({"session_id": session_id})
        response = asyncio.run(
            self.execute_command(f"session_stop {arguments}")
        )
        return response

    def use_theories(
        self,
        theories: List[str],
        session_id: Optional[str] = None,
        master_dir: Optional[str] = None,
        **kwargs,
    ) -> List[IsabelleResponse]:
        """
        Run the engine on theory files.

        >>> isabelle_client = IsabelleClient("localhost", 9999, "test")
        >>> test_response = isabelle_client.use_theories(
        ...     ["Mock"], master_dir="test", watchdog_timeout=0
        ... )
        >>> print(test_response[-1].response_type)
        FINISHED

        :param theories: names of theory files (without extensions!)
        :param session_id: an ID of a session; if ``None``, a new session is
            created and then destroyed after trying to process theories
        :param master_dir: where to look for theory files; if ``None``, uses a
            temp folder of the session
        :param kwargs: additional arguments
            (see Isabelle System manual for details)
        :returns: Isabelle server response
        """
        new_session_id = (
            self.session_start() if session_id is None else session_id
        )
        arguments: Dict[str, Union[List[str], int, str]] = {
            "session_id": new_session_id,
            "theories": theories,
        }
        arguments.update(kwargs)
        if master_dir is not None:
            arguments["master_dir"] = master_dir
        response = asyncio.run(
            self.execute_command(f"use_theories {json.dumps(arguments)}")
        )
        if session_id is None:
            self.session_stop(new_session_id)
        return response

    def echo(self, message: Any) -> List[IsabelleResponse]:
        """
        Ask a server to echo a message.

        >>> isabelle_client = IsabelleClient("localhost", 9999, "test")
        >>> test_response = isabelle_client.echo("test_message")
        >>> print(test_response[-1].response_body)
        "test_message"

        :param message: any text
        :returns: Isabelle server response
        """
        response = asyncio.run(
            self.execute_command(
                f"echo {json. dumps(message)}", asynchronous=False
            )
        )
        return response

    def help(self) -> List[IsabelleResponse]:
        """
        Ask a server to display the list of available commands.

        >>> isabelle_client = IsabelleClient("localhost", 9999, "test")
        >>> test_response = isabelle_client.help()
        >>> print(test_response[-1].response_body)
        ["cancel","echo","help","purge_theories","session_build",...]

        :returns: Isabelle server response
        """
        response = asyncio.run(
            self.execute_command("help", asynchronous=False)
        )
        return response

    def purge_theories(
        self,
        session_id: str,
        theories: List[str],
        master_dir: Optional[str] = None,
        purge_all: Optional[bool] = None,
    ) -> List[IsabelleResponse]:
        """
        Ask a server to purge listed theories from it.

        >>> isabelle_client = IsabelleClient("localhost", 9999, "test")
        >>> test_response = isabelle_client.purge_theories(
        ...     "test", [], "dir", True
        ... )
        >>> print(test_response[-1].response_body)
        {"purged":[{"node_name":"/tmp/Mock.thy",...}],"retained":[]}

        :param session_id: an ID of the session from which to purge theories
        :param theories: a list of theory names to purge from the server
        :param master_dir:  the master directory as in ``use_theories``
        :param purge_all: set to ``True`` attempts to purge all presently
            loaded theories
        :returns: Isabelle server response
        """
        arguments: Dict[str, Union[str, List[str], bool]] = {
            "session_id": session_id,
            "theories": theories,
        }
        if master_dir is not None:
            arguments["master_dir"] = master_dir
        if purge_all is not None:
            arguments["all"] = purge_all
        response = asyncio.run(
            self.execute_command(
                f"purge_theories {json.dumps(arguments)}", asynchronous=False
            )
        )
        return response

    def cancel(self, task: str) -> List[IsabelleResponse]:
        """
        Ask a server to try to cancel a task with a given ID.

        >>> isabelle_client = IsabelleClient("localhost", 9999, "test")
        >>> test_response = isabelle_client.cancel("test_task")
        >>> print(test_response[-1].response_body)
        <BLANKLINE>

        :param task: a task ID
        :returns: Isabelle server response
        """
        arguments = {"task": task}
        response = asyncio.run(
            self.execute_command(
                f"cancel {json.dumps(arguments)}", asynchronous=False
            )
        )
        return response

    def shutdown(self) -> List[IsabelleResponse]:
        """
        Ask a server to shutdown immediately.

        >>> isabelle_client = IsabelleClient("localhost", 9999, "test")
        >>> test_response = isabelle_client.shutdown()
        >>> print(test_response[-1].response_body)
        <BLANKLINE>

        :returns: Isabelle server response
        """
        response = asyncio.run(
            self.execute_command("shutdown", asynchronous=False)
        )
        return response
