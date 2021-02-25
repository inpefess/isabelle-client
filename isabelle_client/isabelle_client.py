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
import json
import re
import socket
from logging import Logger
from typing import List, Optional

from isabelle_client.utils import IsabelleResponse, get_final_message


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

    def execute_command(
        self,
        command: str,
        asynchronous: bool = True,
    ) -> IsabelleResponse:
        """
        executes an (asynchronous) command and waits for results

        >>> from unittest.mock import Mock, patch
        >>> isabelle_client = IsabelleClient("localhost", 1000, "test")
        >>> res = Mock(return_value=IsabelleResponse(
        ...    "FINISHED", '{"session_id": "session_id__42"}', 42
        ... ))
        >>> connect = Mock()
        >>> send = Mock()
        >>> with (
        ...     patch("socket.socket.connect", connect),
        ...     patch("socket.socket.send", send),
        ...     patch("isabelle_client.isabelle_client.get_final_message", res)
        ... ):
        ...    response = isabelle_client.execute_command("test", "test")
        >>> print(response.response_type)
        FINISHED
        >>> print(response.response_body)
        {"session_id": "session_id__42"}
        >>> print(response.response_length)
        42
        >>> print(connect.mock_calls)
        [call(('localhost', 1000))]
        >>> print(send.mock_calls)
        [call(b'test\\ntest\\n')]

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
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_socket:
            tcp_socket.connect((self.address, self.port))
            tcp_socket.send(f"{self.password}\n{command}\n".encode("utf-8"))
            response = get_final_message(
                tcp_socket, final_message, self.logger
            )
        return response

    def session_start(self, session_image: str = "HOL") -> str:
        """
        start a new session

        >>> from unittest.mock import Mock
        >>> isabelle_client = IsabelleClient("localhost", 1000, "test")
        >>> isabelle_client.execute_command = Mock(
        ...     return_value=IsabelleResponse(
        ...     "FINISHED", '{"session_id": "test_session"}', None
        ...     )
        ... )
        >>> print(isabelle_client.session_start())
        test_session
        >>> isabelle_client.execute_command = Mock(
        ...     return_value=IsabelleResponse("OK", "OK")
        ... )
        >>> print(isabelle_client.session_start())
        Traceback (most recent call last):
            ...
        ValueError: Unexpected response type: OK

        :param session: a name of a session image
        :returns: a ``session_id``
        """
        arguments = json.dumps({"session": session_image})
        response = self.execute_command(f"session_start {arguments}")
        if response.response_type == "FINISHED":
            return json.loads(response.response_body)["session_id"]
        raise ValueError(f"Unexpected response type: {response.response_type}")

    def session_stop(self, session_id: str) -> IsabelleResponse:
        """
        stop session with given ID

        >>> from unittest.mock import Mock
        >>> isabelle_client = IsabelleClient("localhost", 1000, "test")
        >>> isabelle_client.execute_command = Mock(
        ...     return_value=IsabelleResponse("FAILED", "")
        ... )
        >>> response = isabelle_client.session_stop("test")
        >>> print(response.response_type)
        FAILED

        :param session_id: a string ID of a session
        :returns: ``isabelle`` server response
        """
        arguments = json.dumps({"session_id": session_id})
        return self.execute_command(f"session_stop {arguments}")

    def use_theories(
        self,
        theories: List[str],
        session_id: Optional[str] = None,
        master_dir: Optional[str] = None,
    ) -> IsabelleResponse:
        """
        run the engine on theory files

        >>> from unittest.mock import Mock
        >>> isabelle_client = IsabelleClient("localhost", 1000, "test")
        >>> isabelle_client.execute_command = Mock(
        ...     return_value=IsabelleResponse(
        ...         "FINISHED", '{"session_id": "test"}'
        ...     )
        ... )
        >>> response = isabelle_client.use_theories(
        ...     ["test"], master_dir="test"
        ... )
        >>> print(response.response_type)
        FINISHED

        :param theories: names of theory files (without extensions!)
        :param session_id: an ID of a session; if ``None``, a new session is
            created and then destroyed after trying to process theories
        :param master_dir: where to look for theory files; if ``None``, uses a
            temp folder of the session
        :returns: ``isabelle`` server response
        """
        new_session_id = (
            self.session_start() if session_id is None else session_id
        )
        try:
            arguments = {"session_id": new_session_id, "theories": theories}
            if master_dir is not None:
                arguments["master_dir"] = master_dir
            response = self.execute_command(
                f"use_theories {json.dumps(arguments)}"
            )
        finally:
            if session_id is None:
                self.session_stop(new_session_id)
        return response

    def echo(self, message: str) -> IsabelleResponse:
        """
        asks a server to echo a message

        >>> from unittest.mock import Mock
        >>> isabelle_client = IsabelleClient("localhost", 1000, "test")
        >>> isabelle_client.execute_command = Mock(
        ...     return_value=IsabelleResponse(
        ...         "OK", json.dumps("test message")
        ...     )
        ... )
        >>> response = isabelle_client.echo("test_message")
        >>> print(response.response_body)
        "test message"

        :param message: any text
        :returns: ``isabelle`` server response
        """
        response = self.execute_command(
            f"echo {json. dumps(message)}", asynchronous=False
        )
        return response

    def help(self) -> IsabelleResponse:
        """
        asks a server to display the list of available commands

        >>> from unittest.mock import Mock
        >>> isabelle_client = IsabelleClient("localhost", 1000, "test")
        >>> isabelle_client.execute_command = Mock(
        ...     return_value=IsabelleResponse(
        ...         "OK", json.dumps(["help", "echo"])
        ...     )
        ... )
        >>> response = isabelle_client.help()
        >>> print(response.response_body)
        ["help", "echo"]

        :returns: ``isabelle`` server response
        """
        response = self.execute_command("help", asynchronous=False)
        return response

    def purge_theories(
        self, session_id: str, theories: List[str]
    ) -> IsabelleResponse:
        """
        asks a server to purge listed theories from it

        >>> from unittest.mock import Mock
        >>> isabelle_client = IsabelleClient("localhost", 1000, "test")
        >>> isabelle_client.execute_command = Mock(
        ...     return_value=IsabelleResponse(
        ...         "OK", json.dumps({"purged": [], "retained": []})
        ...     )
        ... )
        >>> response = isabelle_client.purge_theories("test", [])
        >>> print(response.response_body)
        {"purged": [], "retained": []}

        :param session_id: an ID of the session from which to purge theories
        :param theories: a list of theory names to purge from the server
        :returns: ``isabelle`` server response
        """
        arguments = {"session_id": session_id, "theories": theories}
        response = self.execute_command(
            f"purge_theories {json.dumps(arguments)}", asynchronous=False
        )
        return response


def get_isabelle_client_from_server_info(server_file: str) -> IsabelleClient:
    """
    get an instance of ``IsabelleClient`` from a server info file

    >>> from unittest.mock import mock_open, patch
    >>> with patch("builtins.open", mock_open(read_data="wrong")):
    ...     print(get_isabelle_client_from_server_info("test"))
    Traceback (most recent call last):
        ...
    ValueError: Unexpected server info: wrong
    >>> server_info = 'server "test" = 127.0.0.1:10000 (password "pass")'
    >>> with patch("builtins.open", mock_open(read_data=server_info)):
    ...     print(get_isabelle_client_from_server_info("test").port)
    10000

    :param server_file: a file with server info (a line returned by a server
    on start)
    :returns: an ``isabelle`` client
    """
    with open(server_file, "r") as server_info_file:
        server_info = server_info_file.read()
    match = re.compile(
        r"server \"(.*)\" = (.*):(.*) \(password \"(.*)\"\)"
    ).match(server_info)
    if match is None:
        raise ValueError(f"Unexpected server info: {server_info}")
    _, address, port, password = match.groups()
    isabelle_client = IsabelleClient(address, int(port), password)
    return isabelle_client
