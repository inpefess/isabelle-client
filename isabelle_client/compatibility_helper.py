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
import sys
from typing import Any, Coroutine


def async_run(a_coroutine: Coroutine) -> Any:
    """
    a simple function which models the behaviour of `asyncio.run` method for
    Python 3.6

    :param a_coroutine: some coroutine to await for
    :returns: whatever the coroutine returns
    """
    if sys.version_info.major == 3 and sys.version_info.minor >= 7:
        # pylint: disable=no-member
        result = asyncio.run(a_coroutine)  # type: ignore
    else:
        result = asyncio.get_event_loop().run_until_complete(a_coroutine)
    return result
