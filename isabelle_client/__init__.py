# Copyright 2021-2024 Boris Shminke
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
"""A Python client to `Isabelle <https://isabelle.in.tum.de>`__ server."""
from isabelle_client.isabelle__client import IsabelleClient
from isabelle_client.socket_communication import IsabelleResponse
from isabelle_client.utils import get_isabelle_client, start_isabelle_server

__version__ = "0.4.9"
