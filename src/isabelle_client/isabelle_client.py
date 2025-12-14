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
Isabelle Client
================

A Python client to `Isabelle <https://isabelle.in.tum.de>`__ server
"""  # noqa: D205, D400

import asyncio
import json
from logging import Logger

from isabelle_client.data_models import (
    ASYNCHRONOUS_FINAL_MESSAGES,
    SYNCHRONOUS_FINAL_MESSAGES,
    HelpResult,
    IsabelleResponse,
    IsabelleResponseType,
    NotificationResponse,
    PurgeTheoriesResponse,
    SessionBuildErrorResponse,
    SessionBuildRegularResponse,
    SessionStartErrorResponse,
    SessionStartRegularResponse,
    SessionStopErrorResponse,
    SessionStopRegularResponse,
    SimpleIsabelleResponse,
    TaskOK,
    UseTheoriesErrorResponse,
    UseTheoriesResponse,
)
from isabelle_client.socket_communication import (
    get_final_message,
    get_response_from_isabelle,
)


class IsabelleClient:
    """
    A TCP client for an Isabelle server.

    :param address: IP or a domain name
    :param port: a port number on which the server listens
    :param password: a password to access the server through TCP
    :param logger: a Python logger to store all requests to
        and replies from the server
    """

    def __init__(  # noqa: D107
        self,
        address: str,
        port: int,
        password: str,
        logger: Logger | None = None,
    ) -> None:
        self.address = address
        self.port = port
        self.password = password
        self.logger = logger

    async def execute_command(
        self,
        command: str,
        asynchronous: bool = True,
    ) -> list[IsabelleResponse]:
        r"""
        Execute a command and waits for results.

        >>> logger = getfixture("mock_logger")
        >>> isabelle_client = IsabelleClient(
        ...     "localhost", 9999, "test_password", logger
        ... )
        >>> test_response = asyncio.run(
        ...     isabelle_client.execute_command("unknown command")
        ... )
        >>> print(test_response[-1].response_type.value)
        ERROR
        >>> print(test_response[-1].response_body)
        Bad command 'unknown'
        >>> # error messages don't return the response length
        >>> print(test_response[-1].response_length)
        None
        >>> print(logger.info.mock_calls)
        [call('test_password\nunknown command\n'),
         call('OK {"isabelle_id": "mock", "isabelle_name": "Isabelle2024"}'),
         call('ERROR "Bad command \'unknown\'"')]

        :param command: a full text of a command to Isabelle
        :param asynchronous: if ``False``, waits for ``OK``; else waits for
            ``FINISHED``
        :returns: a list of Isabelle server responses
        """
        final_message = (
            ASYNCHRONOUS_FINAL_MESSAGES
            if asynchronous
            else SYNCHRONOUS_FINAL_MESSAGES
        )
        reader, writer = await asyncio.open_connection(self.address, self.port)
        command = f"{self.password}\n{command}\n"
        writer.write(command.encode("utf-8"))
        await writer.drain()
        password_ok = await get_response_from_isabelle(reader)
        if self.logger is not None:
            self.logger.info(command)
            self.logger.info(str(password_ok))
        return [
            message
            async for message in get_final_message(
                reader, final_message, self.logger
            )
        ]

    def session_build(  # noqa: PLR0913, PLR0917
        self,
        session: str,
        preferences: str | None = None,
        options: list[str] | None = None,
        dirs: list[str] | None = None,
        include_sessions: list[str] | None = None,
        verbose: bool = False,
    ) -> list[
        TaskOK
        | SessionBuildRegularResponse
        | SessionBuildErrorResponse
        | NotificationResponse
    ]:
        r"""
        Build a session from ROOT file.

        >>> isabelle_client = IsabelleClient(
        ...     "localhost", 9999, "test_password"
        ... )
        >>> print(isabelle_client.session_build(
        ...     session="test_session", preferences=""
        ... )[-1])
        400
        FINISHED {"ok":true,"return_code":0,"sessions":[{"session":"Pure",...}

        :param session: a name of the session from ROOT file
        :param preferences: references are loaded from the file
            ``$ISABELLE_HOME_USER/etc/preferences`` by default
        :param options: individual updates to ``preferences`` of the
            form the name=value or name (the latter abbreviates name=true);
            see also command-line option -o for isabelle build.
        :param dirs: additional directories for session ROOT and ROOTS files
        :param include_sessions: field specifies sessions whose theories should
            be included in the overall name space of session-qualified theory
            names.
        :param verbose: set to ``True`` for extra verbosity
        :returns: an Isabelle response
        """
        arguments: dict[str, str | list[str] | bool] = {
            "session": session,
            "options": [] if options is None else options,
            "dirs": [] if dirs is None else dirs,
            "include_sessions": []
            if include_sessions is None
            else include_sessions,
            "verbose": verbose,
        }
        if preferences is not None:
            arguments["preferences"] = preferences
        raw_responses = asyncio.run(
            self.execute_command(f"session_build {json.dumps(arguments)}")
        )
        return [
            SessionBuildRegularResponse(**raw_response.model_dump())
            if raw_response.response_type == IsabelleResponseType.FINISHED
            else (
                SessionBuildErrorResponse(**raw_response.model_dump())
                if raw_response.response_type == IsabelleResponseType.ERROR
                else (
                    TaskOK(**raw_response.model_dump())
                    if raw_response.response_type == IsabelleResponseType.OK
                    else NotificationResponse(**raw_response.model_dump())
                )
            )
            for raw_response in raw_responses
        ]

    def session_start(  # noqa: PLR0913, PLR0917
        self,
        session: str = "Main",
        preferences: str | None = None,
        options: list[str] | None = None,
        dirs: list[str] | None = None,
        include_sessions: list[str] | None = None,
        verbose: bool = False,
        print_mode: list[str] | None = None,
    ) -> list[
        TaskOK
        | SessionStartRegularResponse
        | SessionStartErrorResponse
        | NotificationResponse
    ]:
        r"""
        Start a new session.

        >>> isabelle_client = IsabelleClient("localhost", 9999, "test")
        >>> print(
        ...    isabelle_client.session_start(
        ...        preferences=[])[-1].response_body.session_id)
        167dd6d8-1eeb-4315-8022-c8c527d9bd87

        :param session: a name of a session to start
        :param preferences: references are loaded from the file
            ``$ISABELLE_HOME_USER/etc/preferences`` by default
        :param options: individual updates to ``preferences`` of the
            form the name=value or name (the latter abbreviates name=true);
            see also command-line option -o for isabelle build.
        :param dirs: additional directories for session ROOT and ROOTS files
        :param include_sessions: field specifies sessions whose theories should
            be included in the overall name space of session-qualified theory
            names.
        :param verbose: set to ``True`` for extra verbosity
        :param print_mode: identifiers of print modes to be made active for
            this session
        :returns: Isabelle server response
        """
        arguments: dict[str, str | list[str] | bool] = {
            "session": session,
            "options": [] if options is None else options,
            "dirs": [] if dirs is None else dirs,
            "include_sessions": []
            if include_sessions is None
            else include_sessions,
            "verbose": verbose,
            "print_mode": [] if print_mode is None else print_mode,
        }
        if preferences is not None:
            arguments["preferences"] = preferences
        raw_responses = asyncio.run(
            self.execute_command(f"session_start {json.dumps(arguments)}")
        )
        return [
            SessionStartRegularResponse(**raw_response.model_dump())
            if raw_response.response_type == IsabelleResponseType.FINISHED
            else (
                SessionStartErrorResponse(**raw_response.model_dump())
                if raw_response.response_type == IsabelleResponseType.FAILED
                else (
                    TaskOK(**raw_response.model_dump())
                    if raw_response.response_type == IsabelleResponseType.OK
                    else NotificationResponse(**raw_response.model_dump())
                )
            )
            for raw_response in raw_responses
        ]

    def session_stop(
        self, session_id: str
    ) -> list[
        TaskOK
        | SessionStopErrorResponse
        | SessionStopRegularResponse
        | NotificationResponse
    ]:
        """
        Stop session with given ID.

        >>> isabelle_client = IsabelleClient("localhost", 9999, "test")
        >>> test_response = isabelle_client.session_stop("test")
        >>> print(test_response[-1].response_type.value)
        FINISHED

        :param session_id: a string ID of a session
        :returns: Isabelle server response
        """
        arguments = json.dumps({"session_id": session_id})
        raw_responses = asyncio.run(
            self.execute_command(f"session_stop {arguments}")
        )
        return [
            SessionStopRegularResponse(**raw_response.model_dump())
            if raw_response.response_type == IsabelleResponseType.FINISHED
            else (
                SessionStopErrorResponse(**raw_response.model_dump())
                if raw_response.response_type == IsabelleResponseType.FAILED
                else (
                    TaskOK(**raw_response.model_dump())
                    if raw_response.response_type == IsabelleResponseType.OK
                    else NotificationResponse(**raw_response.model_dump())
                )
            )
            for raw_response in raw_responses
        ]

    def use_theories(  # noqa: PLR0913, PLR0917
        self,
        session_id: str,
        theories: list[str],
        master_dir: str | None = None,
        pretty_margin: float = 76.0,
        unicode_symbols: bool | None = None,
        export_pattern: str | None = None,
        check_delay: float = 0.5,
        check_limit: int | None = None,
        watchdog_timeout: float = 600.0,
        nodes_status_delay: float = -1.0,
    ) -> list[TaskOK | UseTheoriesResponse | UseTheoriesErrorResponse]:
        r"""
        Run the engine on theory files.

        >>> isabelle_client = IsabelleClient("localhost", 9999, "test")
        >>> test_response = isabelle_client.use_theories(
        ...     session_id="test", theories=["Mock"], master_dir="test"
        ... )
        >>> print(test_response[-1].response_type.value)
        FINISHED

        :param session_id: an ID of a session; if ``None``, a new session is
            created and then destroyed after trying to process theories
        :param theories: names of theory files (without extensions!)
        :param master_dir: where to look for theory files; if ``None``, uses a
            temp folder of the session
        :param pretty_margin: pretty formatting of emitted messages
        :param unicode_symbols: use Unicode symbols in emitted messages
        :param export_pattern: see the Isabelle server manual for details
        :param check_delay: status of PIDE processing is checked every
            ``check_delay`` seconds
        :param check_limit: bound on PIDE processing check attempts, ``0`` for
            unbounded
        :param watchdog_timeout: the timespan (in seconds) after the last
            command status change of Isabelle/PIDE, before finishing with a
            potentially non-terminating or deadlocked execution
        :param nodes_status_delay: enables continuous notifications if positive
            (in seconds)
        :returns: Isabelle server response
        """
        arguments = {
            key: value
            for key, value in {
                "session_id": session_id,
                "theories": theories,
                "master_dir": master_dir,
                "pretty_margin": pretty_margin,
                "unicode_symbols": unicode_symbols,
                "export_pattern": export_pattern,
                "check_delay": check_delay,
                "check_limit": check_limit,
                "watchdog_timeout": watchdog_timeout,
                "nodes_status_delay": nodes_status_delay,
            }.items()
            if value is not None
        }
        raw_responses = asyncio.run(
            self.execute_command(f"use_theories {json.dumps(arguments)}")
        )
        return [
            UseTheoriesResponse(**raw_response.model_dump())
            if raw_response.response_type == IsabelleResponseType.FINISHED
            else (
                UseTheoriesErrorResponse(**raw_response.model_dump())
                if raw_response.response_type == IsabelleResponseType.FAILED
                else TaskOK(**raw_response.model_dump())
            )
            for raw_response in raw_responses
        ]

    def echo(self, message: str | list | dict) -> list[IsabelleResponse]:
        """
        Ask a server to echo a message.

        >>> isabelle_client = IsabelleClient("localhost", 9999, "test")
        >>> test_response = isabelle_client.echo("test_message")
        >>> print(test_response[-1].response_body)
        test_message

        :param message: any text
        :returns: Isabelle server response
        """
        return asyncio.run(
            self.execute_command(
                f"echo {json.dumps(message)}", asynchronous=False
            )
        )

    def help(self) -> list[HelpResult]:
        """
        Ask a server to display the list of available commands.

        >>> isabelle_client = IsabelleClient("localhost", 9999, "test")
        >>> test_response = isabelle_client.help()
        >>> print(test_response[-1].response_body)
        ['cancel', 'echo', 'help', 'purge_theories', 'session_build', ...]

        :returns: Isabelle server response
        """
        raw_results = asyncio.run(
            self.execute_command("help", asynchronous=False)
        )
        return [
            HelpResult(**raw_result.model_dump()) for raw_result in raw_results
        ]

    def purge_theories(
        self,
        session_id: str,
        theories: list[str],
        master_dir: str | None = None,
        purge_all: bool | None = None,
    ) -> list[PurgeTheoriesResponse]:
        """
        Ask a server to purge listed theories from it.

        >>> isabelle_client = IsabelleClient("localhost", 9999, "test")
        >>> test_response = isabelle_client.purge_theories(
        ...     "test", [], "dir", True
        ... )
        >>> print(test_response[-1].response_body.model_dump())
        {'purged': [{'node_name': '/tmp/Mock.thy', ...}], 'retained': []}

        :param session_id: an ID of the session from which to purge theories
        :param theories: a list of theory names to purge from the server
        :param master_dir:  the master directory as in ``use_theories``
        :param purge_all: set to ``True`` attempts to purge all presently
            loaded theories
        :returns: Isabelle server response
        """
        arguments: dict[str, str | list[str] | bool] = {
            "session_id": session_id,
            "theories": theories,
        }
        if master_dir is not None:
            arguments["master_dir"] = master_dir
        if purge_all is not None:
            arguments["all"] = purge_all
        raw_responses = asyncio.run(
            self.execute_command(
                f"purge_theories {json.dumps(arguments)}", asynchronous=False
            )
        )
        return [
            PurgeTheoriesResponse(**raw_response.model_dump())
            for raw_response in raw_responses
        ]

    def cancel(self, task: str) -> SimpleIsabelleResponse:
        """
        Ask a server to try to cancel a task with a given ID.

        >>> isabelle_client = IsabelleClient("localhost", 9999, "test")
        >>> test_response = isabelle_client.cancel("test_task")
        >>> print(test_response)
        response_type=<IsabelleResponseType.OK: 'OK'>

        :param task: a task ID
        :returns: Isabelle server response
        """
        arguments = {"task": task}
        return SimpleIsabelleResponse(
            response_type=asyncio.run(
                self.execute_command(
                    f"cancel {json.dumps(arguments)}", asynchronous=False
                )
            )[0].response_type
        )

    def shutdown(self) -> SimpleIsabelleResponse:
        """
        Ask a server to shutdown immediately.

        >>> isabelle_client = IsabelleClient("localhost", 9999, "test")
        >>> test_response = isabelle_client.shutdown()
        >>> print(test_response)
        response_type=<IsabelleResponseType.OK: 'OK'>

        :returns: Isabelle server response
        """
        return SimpleIsabelleResponse(
            response_type=asyncio.run(
                self.execute_command("shutdown", asynchronous=False)
            )[0].response_type
        )
