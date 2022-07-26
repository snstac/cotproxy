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

"""COTProxy Class Definitions."""

import asyncio
import logging
import xml.etree.ElementTree as ET

import aiohttp

import pytak
import cotproxy


__author__ = "Greg Albrecht W2GMD <oss@undef.net>"
__copyright__ = "Copyright 2022 Greg Albrecht"
__license__ = "Apache License, Version 2.0"


class NetListener(asyncio.Protocol):

    """Starts a network listener for COTProxy."""

    _logger = logging.getLogger(__name__)
    if not _logger.handlers:
        _logger.setLevel(cotproxy.LOG_LEVEL)
        _console_handler = logging.StreamHandler()
        _console_handler.setLevel(cotproxy.LOG_LEVEL)
        _console_handler.setFormatter(cotproxy.LOG_FORMAT)
        _logger.addHandler(_console_handler)
        _logger.propagate = False
    logging.getLogger("asyncio").setLevel(cotproxy.LOG_LEVEL)

    def __init__(self, queue, ready) -> None:
        self.queue = queue
        self.ready = ready
        self.transport = None
        self.address = None

    def connection_made(self, transport):
        """Called when a connection is made."""
        self.address = transport.get_extra_info("peername")
        self._logger.debug("Connection from %s", self.address)
        self.transport = transport
        self.ready.set()

    def connection_lost(self, exc):
        """Called when a connection is lost."""
        self.ready.clear()
        self._logger.exception(exc)
        self._logger.warning("Disconnected from %s", self.address)

    def data_received(self, data):
        """Called when data is received."""
        data = data.decode()
        self._logger.debug("Data received: %r", data)
        for line in data.splitlines():
            self.handle_data(line)

    def datagram_received(self, data, addr):
        """Called when a UDP datagram is received."""
        data = data.decode()
        self._logger.debug("Recieved from %s: '%s'", addr, data)
        for line in data.splitlines():
            self.handle_data(line)

    def handle_data(self, data) -> None:
        """Handles received TCP data."""
        self._logger.debug("Received Data='%s'", data)
        try:
            if "<?xml" in data:
                data = data.strip('<?xml version="1.0" encoding="UTF-8"?>')
                root = cotproxy.parse_cot(data)
                if root:
                    self.queue.put_nowait(root)
            else:
                for event in cotproxy.parse_cot_multi(data):
                    self.queue.put_nowait(event)
        except Exception as exc:
            # print(data)
            self._logger.debug(exc)
            

class NetWorker(pytak.Worker):

    """Starts an incoming network data worker."""

    async def run(self, number_of_iterations=-1):
        """Runs the Thread."""

        listen_url: str = (
            self.config.get("LISTEN_URL", cotproxy.DEFAULT_LISTEN_URL).strip().lower()
        )
        host, port = pytak.parse_url(listen_url)

        if "tcp" in listen_url:
            await self.start_tcp_listener(host, port)
        elif "udp" in listen_url:
            await self.start_udp_listener(host, port)

    async def handle_rx(self, reader, writer):
        while 1:
            data: bytes = await reader.readuntil("</event>".encode("UTF-8"))
            self._logger.debug("RX: %s", data)
            self.queue.put_nowait(data)

    async def start_udp_listener(self, host, port):
        """Starts a UDP Network Listener."""
        self._logger.info("%s listening on UDP %s:%s", self.__class__, host, port)
        loop = asyncio.get_event_loop()
        ready = asyncio.Event()

        await loop.create_datagram_endpoint(
            lambda: NetListener(self.queue, ready),
            local_addr=(host, port),
        )
        await ready.wait()
        while 1:
            await asyncio.sleep(0.01)

    async def start_tcp_listener(self, host, port):
        """Starts a TCP Network Listener."""
        server = await asyncio.start_server(self.handle_rx, host, port)

        addrs = ', '.join(str(sock.getsockname()) for sock in server.sockets)
        self._logger.info(f'Serving on %s', addrs)

        async with server:
            await server.serve_forever()


class COTProxyWorker(pytak.QueueWorker):
    """
    Pops unmodified COT from a TF Queue, transforms it if needed, and puts it
    back onto a TX Queue.
    """

    def __init__(self, queue: asyncio.Queue, config, tf_queue: asyncio.Queue) -> None:
        super().__init__(queue, config)
        self.tf_queue = tf_queue
        self.session = None

    async def run(self, number_of_iterations=-1) -> None:
        """Runs this Thread."""
        cpapi_url: str = self.config.get("CPAPI_URL", cotproxy.DEFAULT_CPAPI_URL)
        self._logger.info("%s using: %s", self.__class__, cpapi_url)

        async with aiohttp.ClientSession(cpapi_url) as self.session:
            while 1:
                try:
                    await self.read_queue(use_proxy=True)
                except Exception as exc:
                    self._logger.warning(
                        "Connection to '%s' raised an error: %s", cpapi_url, exc
                    )
                    self._logger.debug(exc)
                    # FIXME: Change to backoff.
                    await asyncio.sleep(2)

    async def read_queue(self, use_proxy: bool = True) -> None:
        """Reads COT from ingress queue and hands off to COT handler."""
        tf_msg: ET.Element = await self.tf_queue.get()
        self._logger.debug('Got tf_msg="%s"', ET.tostring(tf_msg))
        if tf_msg:
            await self.handle_data(tf_msg, use_proxy)

    async def create_co_and_tf(self, event: ET.Element) -> None:
        """
        Creates a COTObject & Transform with the given Event, if neither CO or TF exist.
        """
        uid: str = event.attrib.get("uid")
        callsign: str = cotproxy.get_callsign(event)
        remarks: str = event.find("detail").find("remarks")

        if not uid:
            self._logger.debug("Event had no UID, returning.")
            return

        auto_add: bool = self.config.getboolean("AUTO_ADD", cotproxy.DEFAULT_AUTO_ADD)
        if auto_add:
            self._logger.info("%s added (AUTO_ADD=%s)", uid, auto_add)

            # Create a COT Object
            co_url: str = "/co/"
            async with self.session.post(co_url, json={"uid": uid}) as resp:
                self._logger.debug("%s call status: %s", co_url, resp.status)

            if callsign:
                # Populate the transform
                tf_url: str = "/tf/"
                tf_payload = {
                    "cot_uid": uid,
                    "cot_type": event.attrib.get("type"),
                    "callsign": callsign,
                }
                if remarks:
                    tf_payload["remarks"] = remarks.text
                else:
                    tf_payload["remarks"] = None

                async with self.session.post(tf_url, json=tf_payload) as resp:
                    self._logger.debug("%s call status: %s", tf_url, resp.status)

    async def transform_event(self, event: ET.Element, transform: dict) -> None:
        """
        Transforms a COT event using the given transform.

        Parameters
        ----------
        event : `xml.etree.ElementTree.Element`
            Incoming COT event to transform.
        transform : `dict`
            Data struct of transforms to apply to event.
        """
        if transform.get("active", False):
            self._logger.info("%s Transforming", event.attrib.get("uid"))
            icon = transform.get("icon")
            if icon:
                transform["icon"] = await self.get_icon(icon)
            event: ET.Element = cotproxy.transform_cot(event, transform)

        if isinstance(event, ET.Element):
            await self.put_queue(ET.tostring(event))
        else:
            self._logger.warning("Incoming event was not ET.Element")

    async def get_icon(self, icon) -> None:
        endpoint: str = f"/icon/{icon}"
        async with self.session.get(endpoint) as response:
            if response.status == 200:
                resp = await response.json()
                iconset_uuid = resp["iconset"]
                endpoint = f"/iconset/{iconset_uuid}"
                async with self.session.get(endpoint) as response:
                    resp = await response.json()
                    return f"{iconset_uuid}/{resp['name']}/{icon}"
                
    async def handle_data(self, data: ET.Element, use_proxy: bool = True) -> None:
        """
        Handles data from a queue. In this case, that data is unprocessed COT Events.

        If the Event's UID:
        - Matches an existing Transform: Hand Event off to `transform_event()`.
        - Does not match an existing Transform: Hand Event off to `create_co_and_tf()`.
        Finally, the Event will get handed-off to `pass_all()`.

        Parameters
        ----------
        data : `xml.etree.ElementTree.Element`
            An unprocessed Cursor-On-Target Event.
        use_proxy : `bool`
            Determines if we should even query the COTProxy API.
        """
        uid: str = data.attrib.get("uid")
        if not uid:
            self._logger.debug("Event had no UID, returning.")
            return

        if use_proxy:
            tf_url: str = f"/tf/{uid}"
            async with self.session.get(tf_url) as response:
                # If a Transform for this COT UID doesn't exist:
                if response.status == 404:
                    await self.create_co_and_tf(data)
                # If a Transform for this COT UID does exist, try to Transform:
                elif response.status == 200:
                    await self.transform_event(data, await response.json())
        await self.pass_all(data)

    async def pass_all(self, event: ET.ElementTree) -> None:
        """Passes non-transformed COT Events, if self.pass_all is True."""
        if self.config.getboolean("PASS_ALL", cotproxy.DEFAULT_PASS_ALL):
            await self.put_queue(ET.tostring(event))
