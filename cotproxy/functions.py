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

"""COTProxy Functions."""

import asyncio
import platform
import xml.etree.ElementTree as ET

from configparser import SectionProxy
from typing import Set

import pytak
import cotproxy


__author__ = "Greg Albrecht W2GMD <oss@undef.net>"
__copyright__ = "Copyright 2022 Greg Albrecht"
__license__ = "Apache License, Version 2.0"


def create_tasks(
    config: SectionProxy, clitool: pytak.CLITool
) -> Set[pytak.Worker,]:
    """
    Creates specific coroutine task set for this application.

    Parameters
    ----------
    config : `configparser.SectionProxy`
        Configuration options & values.
    clitool : `pytak.CLITool`
        A PyTAK Worker class instance.

    Returns
    -------
    `set`
        Set of PyTAK Worker classes for this application.
    """
    tf_queue: asyncio.Queue = asyncio.Queue()
    net_worker = cotproxy.NetWorker(tf_queue, config)
    tf_worker = cotproxy.COTProxyWorker(clitool.tx_queue, config, tf_queue)
    return set([net_worker, tf_worker])


def parse_cot(msg: str) -> ET.Element:
    root = ET.fromstring(msg)
    return root


def parse_cot_multi(msg: str) -> ET.Element:
    root = ET.fromstring("<root>" + msg + "</root>")
    return root


def get_callsign(msg) -> str:
    return msg.find("detail").attrib.get(
        "callsign", msg.find("detail").find("contact").attrib.get("callsign")
    )


def transform_cot(original: ET.Element, transform: dict) -> ET.Element:
    """
    Transforms the original COT Event using the given transform definition.
    """
    tfd: bool = False
    callsign = transform.get("callsign")
    if callsign:
        tfd = True
        original.find("detail").attrib["callsign"] = callsign
        original.find("detail").find("contact").attrib["callsign"] = callsign

    cot_type = transform.get("cot_type")
    if cot_type:
        tfd = True
        original.attrib["type"] = cot_type

    remark = transform.get("remark")
    if remark:
        tfd = True
        original.set("remark", remark)

    # <usericon iconsetpath="66f14976-4b62-4023-8edb-d8d2ebeaa336/Public
    #  Safety Air/CIV_FIXED_ISR.png"/>
    icon = transform.get("icon")
    if icon:
        tfd = True
        usericon = ET.Element("usericon")
        usericon.set("iconsetpath", icon)
        original.find("detail").append(usericon)

    video = transform.get("video")
    if video:
        tfd = True
        __video = ET.Element("__video")
        __video.set("url", video.get("url"))
        original.append(__video)

    _cotproxy_ = ET.Element("_cotproxy_")
    _cotproxy_.set("tfd", str(tfd))
    _cotproxy_.set("node", platform.node())
    original.append(_cotproxy_)

    return original
