#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Cursor On Target Transform Proxy

"""
Cursor On Target Transform Proxy
~~~~


:author: Greg Albrecht W2GMD <oss@undef.net>
:copyright: Copyright 2022 Greg Albrecht
:license: Apache License, Version 2.0
:source: <https://github.com/ampledata/cotproxy>

"""

from .constants import (
    LOG_LEVEL,
    LOG_FORMAT,
    DEFAULT_PASS_ALL,
    DEFAULT_AUTO_ADD,
    DEFAULT_CPAPI_URL,
    DEFAULT_COT_URL,
    DEFAULT_TCP_LISTEN_PORT,
)

from .classes import NetClient, NetWorker, COTProxyWorker

from .functions import parse_cot, transform_cot, get_callsign, parse_cot_multi

__author__ = "Greg Albrecht W2GMD <oss@undef.net>"
__copyright__ = "Copyright 2022 Greg Albrecht"
__license__ = "Apache License, Version 2.0"
