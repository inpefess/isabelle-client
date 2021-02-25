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
import io
import json
import socket
from typing import List, Optional, cast

from isabelle_client.utils import IsabelleResponse, get_final_message


class IsabelleClient:
    """ a TCP client for an ``isabelle`` server """

    def __init__(
        self,
        server_name: str,
        server_address: str,
        server_port: int,
        server_password: str,
    ):
        """
        :param server_name: a human-readable name of the server
        :param server_address: IP or a domain name
        :param server_port: a port number on which the server listens
        :param server_password: a password to access the server through TCP
        """
        self.server_name = server_name
        self.server_address = server_address
        self.server_port = server_port
        self.server_password = server_password

    def execute_command(
        self,
        command: str,
        log_filename: Optional[str] = None,
        asynchronous: bool = True,
    ) -> IsabelleResponse:
        """
        executes an (asynchronous) command and waits for results

        >>> from unittest.mock import Mock, patch, mock_open
        >>> isabelle_client = IsabelleClient("test", "localhost", 1000, "test")
        >>> res = Mock(return_value=IsabelleResponse(
        ...    "FINISHED", '{"session_id": "session_id__42"}', 42
        ... ))
        >>> connect = Mock()
        >>> send = Mock()
        >>> open_mock = mock_open()
        >>> with (
        ...     patch("socket.socket.connect", connect),
        ...     patch("socket.socket.send", send),
        ...     patch("builtins.open", open_mock),
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
        >>> print(open_mock.mock_calls)
        [call('test', 'w'), call().close()]

        :param command: a full text of a command to ``isabelle``
        :param log_filename: a file for saving a copy of all data received from
            the server
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
            tcp_socket.connect((self.server_address, self.server_port))
            tcp_socket.send(
                f"{self.server_password}\n{command}\n".encode("utf-8")
            )
            log_file = (
                open(log_filename, "w") if log_filename is not None else None
            )
            response = get_final_message(
                tcp_socket, final_message, cast(io.TextIOWrapper, log_file)
            )
            if log_file is not None:
                log_file.close()
        return response

    def session_start(
        self, session_image: str = "HOL", log_filename: Optional[str] = None
    ) -> str:
        """
        start a new session

        >>> from unittest.mock import Mock
        >>> isabelle_client = IsabelleClient("test", "localhost", 1000, "test")
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
        :param log_filename: a file for saving a copy of all data received from
            the server
        :returns: a ``session_id``
        """
        arguments = json.dumps({"session": session_image})
        response = self.execute_command(
            f"session_start {arguments}", log_filename
        )
        if response.response_type == "FINISHED":
            return json.loads(response.response_body)["session_id"]
        raise ValueError(f"Unexpected response type: {response.response_type}")

    def session_stop(self, session_id: str) -> IsabelleResponse:
        """
        stop session with given ID

        >>> from unittest.mock import Mock
        >>> isabelle_client = IsabelleClient("test", "localhost", 1000, "test")
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
        log_filename: Optional[str] = None,
    ) -> IsabelleResponse:
        """
        run the engine on theory files

        >>> from unittest.mock import Mock
        >>> isabelle_client = IsabelleClient("test", "localhost", 1000, "test")
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
        :param log_filename: a file for a copy of all server messages
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
                f"use_theories {json.dumps(arguments)}", log_filename
            )
        finally:
            if session_id is None:
                self.session_stop(new_session_id)
        return response

    def echo(self, message: str) -> IsabelleResponse:
        """
        asks a server to echo a message

        >>> from unittest.mock import Mock
        >>> isabelle_client = IsabelleClient("test", "localhost", 1000, "test")
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
        >>> isabelle_client = IsabelleClient("test", "localhost", 1000, "test")
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
        >>> isabelle_client = IsabelleClient("test", "localhost", 1000, "test")
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
