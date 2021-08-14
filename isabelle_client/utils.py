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
import re
from typing import Optional, Tuple

from isabelle_client.compatibility_helper import async_run
from isabelle_client.isabelle__client import IsabelleClient


def get_isabelle_client(server_info: str) -> IsabelleClient:
    """
    get an instance of ``IsabelleClient`` from server info

    >>> server_inf = 'server "test" = 127.0.0.1:10000 (password "pass")'
    >>> print(get_isabelle_client(server_inf).port)
    10000
    >>> get_isabelle_client("wrong")
    Traceback (most recent call last):
        ...
    ValueError: Unexpected server info: wrong

    :param server_info: a line returned by a server on start
    :returns: an Isabelle client
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
    start Isabelle server

    >>> import os
    >>> os.environ["PATH"] = "tests:$PATH"
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

    async def async_call():
        isabelle_server = await asyncio.create_subprocess_exec(
            "isabelle", *(args.split(" ")), stdout=asyncio.subprocess.PIPE
        )
        return (await isabelle_server.stdout.readline()).decode(
            "utf-8"
        ), isabelle_server

    return async_run(async_call())
