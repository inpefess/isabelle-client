# Copyright 2021-2023 Boris Shminke
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
"""A script for generating the video example."""
import os
import sys
import time

if sys.version_info.major == 3 and sys.version_info.minor >= 9:
    # pylint: disable=no-name-in-module, import-error
    from importlib.resources import files  # type: ignore
else:  # pragma: no cover
    from importlib_resources import files  # pylint: disable=import-error

with open(  # type: ignore
    files("isabelle_client").joinpath(
        os.path.join("resources", "example.txt")
    ),
    encoding="utf-8",
) as example:
    lines = example.readlines()

for line in lines:
    if line[:6] == "SLEEP ":
        time.sleep(int(line[6:]))
    else:
        for char in line:
            print(char, end="", flush=True)
            time.sleep(70 / 600)
