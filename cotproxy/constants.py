#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright 2022 Greg Albrecht <oss@undef.net>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Author:: Greg Albrecht W2GMD <oss@undef.net>
#

"""COTProxy Constants."""

import logging
import os

__author__ = "Greg Albrecht W2GMD <oss@undef.net>"
__copyright__ = "Copyright 2022 Greg Albrecht"
__license__ = "Apache License, Version 2.0"


if bool(os.environ.get("DEBUG")):
    LOG_LEVEL: int = logging.DEBUG
    LOG_FORMAT: logging.Formatter = logging.Formatter(
        (
            "%(asctime)s cotproxy %(levelname)s %(name)s.%(funcName)s:%(lineno)d - "
            "%(message)s"
        )
    )
    logging.debug("cotproxy Debugging Enabled via DEBUG Environment Variable.")
else:
    LOG_LEVEL: int = logging.INFO
    LOG_FORMAT: logging.Formatter = logging.Formatter(
        ("%(asctime)s cotproxy %(levelname)s - %(message)s")
    )

DEFAULT_PASS_ALL: bool = False
DEFAULT_AUTO_ADD: bool = False
DEFAULT_SLEEP_INTERVAL: int = 20
DEFAULT_CPAPI_URL: str = "http://localhost:10415/"
DEFAULT_LISTEN_URL: str = "udp://0.0.0.0:8087"
DEFAULT_KNOWN_CRAFT_FILE: str = "known_craft.csv"
DEFAULT_SEED_FAA_REG: bool = True
