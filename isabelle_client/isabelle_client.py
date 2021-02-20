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
import re
import socket
from dataclasses import dataclass
from typing import List, Optional, Set, cast


def get_delimited_message(
    tcp_socket: socket.socket,
    delimiter: str = "\n",
    encoding: str = "utf-8",
) -> str:
    """
    get a delimited (not fixed-length)response from a TCP socket

    :param tcp_socket: a TCP socket to receive data from
    :param response_end_char: a character which marks the end of response
    :param encoding: a socket encoding
    :returns: decoded string response
    """
    response = " "
    while response[-1] != delimiter:
        response += tcp_socket.recv(1).decode(encoding)
    return response[1:]


def get_fixed_length_message(
    tcp_socket: socket.socket,
    message_length: int,
    chunk_size: int = 8196,
    encoding: str = "utf-8",
) -> str:
    """
    get a response of a fixed length from a TCP socket

    :param tcp_socket: a TCP socket to receive data from
    :param message_length: a number of bytes to read as a message
    :param chunk_size: the maximal number of bytes to get at one time
    :param encoding: a socket encoding
    :returns: decoded string response
    """
    response = b""
    read_length = 0
    while read_length < message_length:
        response += tcp_socket.recv(
            min(chunk_size, message_length - read_length)
        )
        read_length = len(response)
    return response.decode(encoding)


def get_response_from_isabelle(tcp_socket: socket.socket) -> str:
    """
    get a response of a fixed length from a TCP socket

    :param tcp_socket: a TCP socket to receive data from
    :returns: decoded string response
    """
    response = get_delimited_message(tcp_socket)
    match = re.compile(r"(\d+)\n").match(response)
    if match is not None:
        response += get_fixed_length_message(tcp_socket, int(match.group(1)))
    return response


@dataclass
class IsabelleResponse:
    """ a response from an ``isabelle`` server """

    response_type: str  # an all capitals word like ``FINISHED`` or ``ERROR``
    response_body: str  # a JSON-formatted response
    # pylint: disable=unsubscriptable-object
    response_length: Optional[int] = None  # a length of JSON response


class IsabelleClient:
    """ a TCP client for an ``isabelle`` server """

    _response_parser = re.compile(r"(\d*)?\n?(\w+) (.*)")

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

    # pylint: disable=unsubscriptable-object
    def get_all_responses(
        self,
        tcp_socket: socket.socket,
        final_message: Set[str],
        log_file: Optional[io.TextIOWrapper] = None,
    ) -> List[str]:
        """
        :param tcp_socket:  a TCP socket to ``isabelle`` server
        :param final_message: a set of possible final message types
        :param log_file: a file for writing a copy of all messages
        :returns: a list of parts of the final message
        """
        parsed_response = ["", ""]
        while parsed_response[1] not in final_message:
            response = get_response_from_isabelle(tcp_socket)
            if log_file is not None:
                log_file.write(response)
            match = self._response_parser.match(response)
            if match is None:
                raise ValueError(
                    f"Unexpected response from Isabelle: {response}"
                )
            parsed_response = list(match.groups())
        return parsed_response

    # pylint: disable=unsubscriptable-object
    def execute_command(
        self,
        command: str,
        log_filename: Optional[str] = None,
        asynchronous: bool = True,
    ) -> IsabelleResponse:
        """
        executes an (asynchronous) command and waits for results

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
            parsed_response = self.get_all_responses(
                tcp_socket, final_message, cast(io.TextIOWrapper, log_file)
            )
            if log_file is not None:
                log_file.close()
        return IsabelleResponse(
            parsed_response[1],
            parsed_response[2],
            int(parsed_response[0]) if parsed_response[0] != "" else None,
        )

    def session_start(self, session_image: str = "HOL") -> str:
        """start a new session

        :param session: a name of a session image
        :returns: a ``session_id``
        """
        arguments = json.dumps({"session": session_image})
        response = self.execute_command(f"session_start {arguments}")
        if response.response_type == "FINISHED":
            return json.loads(response.response_body)["session_id"]
        raise ValueError(response)

    def session_stop(self, session_id: str) -> IsabelleResponse:
        """stop session with given ID

        :param session_id: a string ID of a session
        :returns: ``isabelle`` server response
        """
        arguments = json.dumps({"session_id": session_id})
        return self.execute_command(f"session_stop {arguments}")

    # pylint: disable=unsubscriptable-object
    def use_theories(
        self,
        theories: List[str],
        session_id: Optional[str] = None,
        master_dir: Optional[str] = None,
        log_filename: Optional[str] = None,
    ) -> IsabelleResponse:
        """run the engine on theory files

        :param theories: names of theory files (without extensions!)
        :param session_id: an ID of a session; if ``None``, a new session is
        created and then destroyed after trying to process theories
        :param master_dir: where to look for theory files; if ``None``, uses a
        temp folder of then session
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
