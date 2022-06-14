#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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

DEFAULT_CPAPI_URL: str = "http://localhost:8080"
DEFAULT_COT_URL: str = "udp://239.2.3.1:6969"  # ATAK Default multicast

DEFAULT_LISTEN_URL: str = "udp://0.0.0.0:8087"
