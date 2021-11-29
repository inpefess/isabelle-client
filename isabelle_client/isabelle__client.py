"""
Copyright 2021 Boris Shminke

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    https://www.apache.org/licenses/LICENSE-2.0

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

from isabelle_client.compatibility_helper import async_run
from isabelle_client.socket_communication import (
    IsabelleResponse,
    get_final_message,
)


class IsabelleClient:
    """ a TCP client for an Isabelle server """

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
    ) -> List[IsabelleResponse]:
        """
        executes a command and waits for results

        >>> logger = getfixture("mock_logger")
        >>> isabelle_client = IsabelleClient(
        ...     "localhost", 9999, "test_password", logger
        ... )
        >>> test_response = async_run(
        ...     isabelle_client.execute_command("test_command")
        ... )
        >>> print(test_response[-1].response_type)
        FINISHED
        >>> print(test_response[-1].response_body)
        {"session_id": "test_session_id"}
        >>> print(test_response[-1].response_length)
        43
        >>> print(logger.info.mock_calls)
        [call('test_password\\ntest_command\\n'),
        call('OK "connection OK"'),
        call('43\\nFINISHED {"session_id": "test_session_id"}')]

        :param command: a full text of a command to Isabelle
        :param asynchronous: if ``False``, waits for ``OK``; else waits for
            ``FINISHED``
        :returns: a list of Isabelle server responses
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

        >>> isabelle_client = IsabelleClient(
        ...     "localhost", 9999, "test_password"
        ... )
        >>> print(isabelle_client.session_build(
        ...     session="test_session", dirs=["."], verbose=True, options=[]
        ... )[-1])
        43
        FINISHED {"session_id": "test_session_id"}

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
        response = async_run(
            self.execute_command(f"session_build {json.dumps(arguments)}")
        )
        return response

    def session_start(self, session: str = "HOL", **kwargs) -> str:
        """
        start a new session

        >>> isabelle_client = IsabelleClient("localhost", 9998, "test")
        >>> print(isabelle_client.session_start(verbose=True))
        Traceback (most recent call last):
            ...
        ValueError: Unexpected response type: FAILED
        >>> isabelle_client = IsabelleClient("localhost", 9999, "test")
        >>> print(isabelle_client.session_start())
        test_session_id

        :param session: a name of a session to start
        :param kwargs: additional arguments
            (see Isabelle System manual for details)
        :returns: a ``session_id``
        """
        arguments = {"session": session}
        arguments.update(kwargs)
        response_list = async_run(
            self.execute_command(f"session_start {json.dumps(arguments)}")
        )
        if response_list[-1].response_type == "FINISHED":
            return json.loads(response_list[-1].response_body)["session_id"]
        raise ValueError(
            f"Unexpected response type: {response_list[-1].response_type}"
        )

    def session_stop(self, session_id: str) -> IsabelleResponse:
        """
        stop session with given ID

        >>> isabelle_client = IsabelleClient("localhost", 9999, "test")
        >>> test_response = isabelle_client.session_stop("test")
        >>> print(test_response[-1].response_type)
        FINISHED

        :param session_id: a string ID of a session
        :returns: Isabelle server response
        """
        arguments = json.dumps({"session_id": session_id})
        response = async_run(self.execute_command(f"session_stop {arguments}"))
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

        >>> isabelle_client = IsabelleClient("localhost", 9999, "test")
        >>> test_response = isabelle_client.use_theories(
        ...     ["test"], master_dir="test", watchdog_timeout=0
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
        response = async_run(
            self.execute_command(f"use_theories {json.dumps(arguments)}")
        )
        if session_id is None:
            self.session_stop(new_session_id)
        return response

    def echo(self, message: Any) -> IsabelleResponse:
        """
        asks a server to echo a message

        >>> isabelle_client = IsabelleClient("localhost", 9999, "test")
        >>> test_response = isabelle_client.echo("test_message")
        >>> print(test_response[-1].response_body)
        "test_message"

        :param message: any text
        :returns: Isabelle server response
        """
        response = async_run(
            self.execute_command(
                f"echo {json. dumps(message)}", asynchronous=False
            )
        )
        return response

    def help(self) -> IsabelleResponse:
        """
        asks a server to display the list of available commands

        >>> isabelle_client = IsabelleClient("localhost", 9999, "test")
        >>> test_response = isabelle_client.help()
        >>> print(test_response[-1].response_body)
        ["echo", "help"]

        :returns: Isabelle server response
        """
        response = async_run(self.execute_command("help", asynchronous=False))
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

        >>> isabelle_client = IsabelleClient("localhost", 9999, "test")
        >>> test_response = isabelle_client.purge_theories(
        ...     "test", [], "dir", True
        ... )
        >>> print(test_response[-1].response_body)
        {"purged": [], "retained": []}

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
        response = async_run(
            self.execute_command(
                f"purge_theories {json.dumps(arguments)}", asynchronous=False
            )
        )
        return response

    def cancel(self, task: str) -> IsabelleResponse:
        """
        asks a server to try to cancel a task with a given ID

        >>> isabelle_client = IsabelleClient("localhost", 9999, "test")
        >>> test_response = isabelle_client.cancel("test_task")
        >>> print(test_response[-1].response_body)
        <BLANKLINE>

        :param task: a task ID
        :returns: Isabelle server response
        """
        arguments = {"task": task}
        response = async_run(
            self.execute_command(
                f"cancel {json.dumps(arguments)}", asynchronous=False
            )
        )
        return response

    def shutdown(self) -> IsabelleResponse:
        """
        asks a server to shutdown immediately

        >>> isabelle_client = IsabelleClient("localhost", 9999, "test")
        >>> test_response = isabelle_client.shutdown()
        >>> print(test_response[-1].response_body)
        <BLANKLINE>

        :returns: Isabelle server response
        """
        response = async_run(
            self.execute_command("shutdown", asynchronous=False)
        )
        return response
