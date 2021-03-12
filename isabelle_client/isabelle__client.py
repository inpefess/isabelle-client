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
import json
from logging import Logger
from typing import Any, Dict, List, Optional, Union

from isabelle_client.socket_communication import (
    IsabelleResponse,
    get_final_message,
)


class IsabelleClient:
    """ a TCP client for an ``isabelle`` server """

    def __init__(
        self,
        address: str,
        port: int,
        password: str,
        logger: Optional[Logger] = None,
    ):
        """
        :param address: IP or a domain name
        :param port: a port number on which the server listens
        :param password: a password to access the server through TCP
        """
        self.address = address
        self.port = port
        self.password = password
        self.logger = logger

    async def execute_command(
        self,
        command: str,
        asynchronous: bool = True,
    ) -> IsabelleResponse:
        """
        executes a command and waits for results

        >>> from unittest.mock import Mock, patch, AsyncMock
        >>> logger = Mock()
        >>> logger.info = Mock()
        >>> isabelle_client = IsabelleClient("localhost", 1000, "test", logger)
        >>> res = AsyncMock(return_value=IsabelleResponse(
        ...    "FINISHED", '{"session_id": "session_id__42"}', 42
        ... ))
        >>> test_writer = Mock()
        >>> test_writer.drain = AsyncMock()
        >>> connection = AsyncMock(return_value=(Mock(), test_writer))
        >>> with (
        ...     patch("asyncio.open_connection", connection),
        ...     patch(
        ...         "isabelle_client.isabelle__client.get_final_message",
        ...         res
        ...     )
        ... ):
        ...    test_response = asyncio.run(
        ...     isabelle_client.execute_command("test")
        ... )
        >>> print(test_response.response_type)
        FINISHED
        >>> print(test_response.response_body)
        {"session_id": "session_id__42"}
        >>> print(test_response.response_length)
        42
        >>> print(connection.mock_calls)
        [call('localhost', 1000)]
        >>> print(test_writer.write.mock_calls)
        [call(b'test\\ntest\\n')]
        >>> print(logger.info.mock_calls)
        [call('test\\ntest\\n')]

        :param command: a full text of a command to ``isabelle``
        :param asynchronous: if ``False``, waits for ``OK``; else waits for
            ``FINISHED``
        :returns: ``isabelle`` server response
        """
        final_message = (
            {"FINISHED", "FAILED", "ERROR"}
            if asynchronous
            else {"OK", "ERROR"}
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
        dirs: List[str] = None,
        verbose: bool = False,
        **kwargs,
    ) -> IsabelleResponse:
        """
        build a session from ROOT file

        >>> from unittest.mock import AsyncMock
        >>> isabelle_client = IsabelleClient("localhost", 1000, "test")
        >>> isabelle_client.execute_command = AsyncMock(
        ...     return_value=IsabelleResponse(
        ...     "FINISHED", '{"ok": true}', None
        ...     )
        ... )
        >>> print(isabelle_client.session_build(
        ...     session="test_session", dirs=["."], verbose=True, options=[]
        ... ))
        FINISHED {"ok": true}

        :param session: a name of the session from ROOT file
        :param dirs: where to look for ROOT files
        :param verbose: set to ``True`` for extra verbosity
        :param kwargs: additional arguments
            (see Isabelle System manual for details)
        :returns: an ``isabelle`` response
        """
        arguments: Dict[str, Union[str, List[str], bool]] = {
            "session": session,
            "verbose": verbose,
        }
        if dirs is not None:
            arguments["dirs"] = dirs
        for name in kwargs:
            arguments[name] = kwargs[name]
        response = asyncio.run(
            self.execute_command(f"session_build {json.dumps(arguments)}")
        )
        return response

    def session_start(self, session: str = "HOL", **kwargs) -> str:
        """
        start a new session

        >>> from unittest.mock import AsyncMock
        >>> isabelle_client = IsabelleClient("localhost", 1000, "test")
        >>> isabelle_client.execute_command = AsyncMock(
        ...     return_value=IsabelleResponse(
        ...     "FINISHED", '{"session_id": "test_session"}', None
        ...     )
        ... )
        >>> print(isabelle_client.session_start())
        test_session
        >>> isabelle_client.execute_command = AsyncMock(
        ...     return_value=IsabelleResponse("OK", "OK")
        ... )
        >>> print(isabelle_client.session_start(verbose=True))
        Traceback (most recent call last):
            ...
        ValueError: Unexpected response type: OK

        :param session: a name of a session to start
        :param kwargs: additional arguments
            (see Isabelle System manual for details)
        :returns: a ``session_id``
        """
        arguments = {"session": session}
        for name in kwargs:
            arguments[name] = kwargs[name]
        response = asyncio.run(
            self.execute_command(f"session_start {json.dumps(arguments)}")
        )
        if response.response_type == "FINISHED":
            return json.loads(response.response_body)["session_id"]
        raise ValueError(f"Unexpected response type: {response.response_type}")

    def session_stop(self, session_id: str) -> IsabelleResponse:
        """
        stop session with given ID

        >>> from unittest.mock import AsyncMock
        >>> isabelle_client = IsabelleClient("localhost", 1000, "test")
        >>> isabelle_client.execute_command = AsyncMock(
        ...     return_value=IsabelleResponse("FAILED", "")
        ... )
        >>> test_response = isabelle_client.session_stop("test")
        >>> print(test_response.response_type)
        FAILED

        :param session_id: a string ID of a session
        :returns: ``isabelle`` server response
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
    ) -> IsabelleResponse:
        """
        run the engine on theory files

        >>> from unittest.mock import AsyncMock
        >>> isabelle_client = IsabelleClient("localhost", 1000, "test")
        >>> isabelle_client.execute_command = AsyncMock(
        ...     return_value=IsabelleResponse(
        ...         "FINISHED", '{"session_id": "test"}'
        ...     )
        ... )
        >>> test_response = isabelle_client.use_theories(
        ...     ["test"], master_dir="test", watchdog_timeout=0
        ... )
        >>> print(test_response.response_type)
        FINISHED

        :param theories: names of theory files (without extensions!)
        :param session_id: an ID of a session; if ``None``, a new session is
            created and then destroyed after trying to process theories
        :param master_dir: where to look for theory files; if ``None``, uses a
            temp folder of the session
        :param kwargs: additional arguments
            (see Isabelle System manual for details)
        :returns: ``isabelle`` server response
        """
        new_session_id = (
            self.session_start() if session_id is None else session_id
        )
        arguments: Dict[str, Union[List[str], int, str]] = {
            "session_id": new_session_id,
            "theories": theories,
        }
        for name in kwargs:
            arguments[name] = kwargs[name]
        if master_dir is not None:
            arguments["master_dir"] = master_dir
        response = asyncio.run(
            self.execute_command(f"use_theories {json.dumps(arguments)}")
        )
        if session_id is None:
            self.session_stop(new_session_id)
        return response

    def echo(self, message: Any) -> IsabelleResponse:
        """
        asks a server to echo a message

        >>> from unittest.mock import AsyncMock
        >>> isabelle_client = IsabelleClient("localhost", 1000, "test")
        >>> isabelle_client.execute_command = AsyncMock(
        ...     return_value=IsabelleResponse(
        ...         "OK", json.dumps("test message")
        ...     )
        ... )
        >>> test_response = isabelle_client.echo("test_message")
        >>> print(test_response.response_body)
        "test message"

        :param message: any text
        :returns: ``isabelle`` server response
        """
        response = asyncio.run(
            self.execute_command(
                f"echo {json. dumps(message)}", asynchronous=False
            )
        )
        return response

    def help(self) -> IsabelleResponse:
        """
        asks a server to display the list of available commands

        >>> from unittest.mock import AsyncMock
        >>> isabelle_client = IsabelleClient("localhost", 1000, "test")
        >>> isabelle_client.execute_command = AsyncMock(
        ...     return_value=IsabelleResponse(
        ...         "OK", json.dumps(["help", "echo"])
        ...     )
        ... )
        >>> test_response = isabelle_client.help()
        >>> print(test_response.response_body)
        ["help", "echo"]

        :returns: ``isabelle`` server response
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
    ) -> IsabelleResponse:
        """
        asks a server to purge listed theories from it

        >>> from unittest.mock import AsyncMock
        >>> isabelle_client = IsabelleClient("localhost", 1000, "test")
        >>> isabelle_client.execute_command = AsyncMock(
        ...     return_value=IsabelleResponse(
        ...         "OK", json.dumps({"purged": [], "retained": []})
        ...     )
        ... )
        >>> test_response = isabelle_client.purge_theories(
        ...     "test", [], "dir", True
        ... )
        >>> print(test_response.response_body)
        {"purged": [], "retained": []}

        :param session_id: an ID of the session from which to purge theories
        :param theories: a list of theory names to purge from the server
        :param master_dir:  the master directory as in ``use_theories``
        :param purge_all: set to ``True`` attempts to purge all presently
            loaded theories
        :returns: ``isabelle`` server response
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

    def cancel(self, task: str) -> IsabelleResponse:
        """
        asks a server to try to cancel a task with a given ID

        >>> from unittest.mock import AsyncMock
        >>> isabelle_client = IsabelleClient("localhost", 1000, "test")
        >>> isabelle_client.execute_command = AsyncMock(
        ...     return_value=IsabelleResponse(
        ...         "OK", ""
        ...     )
        ... )
        >>> test_response = isabelle_client.cancel("test_task")
        >>> print(test_response.response_body)
        <BLANKLINE>

        :param task: a task ID
        :returns: ``isabelle`` server response
        """
        arguments = {"task": task}
        response = asyncio.run(
            self.execute_command(
                f"cancel {json.dumps(arguments)}", asynchronous=False
            )
        )
        return response

    def shutdown(self) -> IsabelleResponse:
        """
        asks a server to shutdown immediately

        >>> from unittest.mock import AsyncMock
        >>> isabelle_client = IsabelleClient("localhost", 1000, "test")
        >>> isabelle_client.execute_command = AsyncMock(
        ...     return_value=IsabelleResponse(
        ...         "OK", ""
        ...     )
        ... )
        >>> test_response = isabelle_client.shutdown()
        >>> print(test_response.response_body)
        <BLANKLINE>

        :returns: ``isabelle`` server response
        """
        response = asyncio.run(
            self.execute_command("shutdown", asynchronous=False)
        )
        return response
