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

"""
Cursor On Target Transform Proxy
~~~~

:author: Greg Albrecht W2GMD <oss@undef.net>
:copyright: Copyright 2022 Greg Albrecht
:license: Apache License, Version 2.0
:source: <https://github.com/ampledata/cotproxy>
"""

from .constants import (  # NOQA
    LOG_LEVEL,
    LOG_FORMAT,
    DEFAULT_PASS_ALL,
    DEFAULT_AUTO_ADD,
    DEFAULT_CPAPI_URL,
    DEFAULT_SLEEP_INTERVAL,
    DEFAULT_LISTEN_URL,
    DEFAULT_KNOWN_CRAFT_FILE,
    DEFAULT_SEED_FAA_REG,
)

from .classes import NetListener, NetWorker, COTProxyWorker  # NOQA

from .functions import (  # NOQA
    parse_cot,
    transform_cot,
    get_callsign,
    parse_cot_multi,
    create_tasks,
)

__author__ = "Greg Albrecht W2GMD <oss@undef.net>"
__copyright__ = "Copyright 2022 Greg Albrecht"
__license__ = "Apache License, Version 2.0"
