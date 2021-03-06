..
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


Package Documentation
=====================

Isabelle Response
-----------------
.. autoclass:: isabelle_client.IsabelleResponse
   :special-members: __init__
   :members:


Isabelle Client
---------------
.. autoclass:: isabelle_client.IsabelleClient
   :special-members: __init__
   :members:

socket_communication
--------------------
.. currentmodule:: isabelle_client.socket_communication

A collection of functions for TCP communication.

.. autofunction:: get_response_from_isabelle
.. autofunction:: get_final_message

utils
-----
.. currentmodule:: isabelle_client.utils

A collection of different useful functions.

.. autofunction:: start_isabelle_server
.. autofunction:: get_isabelle_client
