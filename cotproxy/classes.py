#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Cursor On Target Transform Proxy Class Definitions."""

import asyncio
import logging
import urllib
import xml.etree.ElementTree as ET

import aiohttp
import pytak

import cotproxy


__author__ = "Greg Albrecht W2GMD <oss@undef.net>"
__copyright__ = "Copyright 2022 Greg Albrecht"
__license__ = "Apache License, Version 2.0"


class NetClient(asyncio.Protocol):
    """
    Listens for TCP data and puts it onto a msg queue.
    """

    _logger = logging.getLogger(__name__)
    if not _logger.handlers:
        _logger.setLevel(cotproxy.LOG_LEVEL)
        _console_handler = logging.StreamHandler()
        _console_handler.setLevel(cotproxy.LOG_LEVEL)
        _console_handler.setFormatter(cotproxy.LOG_FORMAT)
        _logger.addHandler(_console_handler)
        _logger.propagate = False
    logging.getLogger("asyncio").setLevel(cotproxy.LOG_LEVEL)

    def __init__(self, ready, msg_queue, opts) -> None:
        self.transport = None
        self.address = None
        self.ready = ready
        self.msg_queue = msg_queue

    def handle_message(self, data) -> None:
        # self._logger.debug('Received Data="%s"', data)
        if "<?xml" in data:
            root = cotproxy.parse_cot(data)
            if root:
                self.msg_queue.put_nowait(root)
        else:
            for event in cotproxy.parse_cot_multi(data):
                self.msg_queue.put_nowait(event)

    def connection_made(self, transport):
        self.address = transport.get_extra_info("peername")
        self._logger.debug("Connection from %s", self.address)
        self.transport = transport
        self.ready.set()

    def data_received(self, data):
        message = data.decode()
        self._logger.debug("Data received: {!r}".format(message))
        self.handle_message(message)

    def connection_lost(self, exc):
        self.ready.clear()
        self._logger.exception(exc)
        self._logger.warning("Disconnected from %s", self.address)


class NetWorker(pytak.Worker):

    """Starts a NetClient TCP Protocol server."""

    def __init__(self, msg_queue: asyncio.Queue, config) -> None:
        super().__init__(msg_queue)
        self.msg_queue = msg_queue

        self.config = config["cotproxy"]

        self.tcp_port = int(
            self.config.get("TCP_LISTEN_PORT") or cotproxy.TCP_LISTEN_PORT
        )
        self.listen_host = self.config.get("LISTEN_HOST") or "0.0.0.0"

    async def run(self):
        """Runs this Thread."""
        self._logger.info("Running NetWorker")
        loop = asyncio.get_event_loop()

        ready = asyncio.Event()
        server = await loop.create_server(
            lambda: NetClient(ready, self.msg_queue, self.config),
            self.listen_host,
            self.tcp_port,
        )

        await ready.wait()

        while 1:
            await asyncio.sleep(0.01)


class COTProxyWorker(pytak.MessageWorker):
    """
    Pops unmodified COT from a TF Queue, transforms it if needed, and puts it
    back onto a TX Queue.
    """

    def __init__(
        self, tf_queue: asyncio.Queue, tx_queue: asyncio.Queue, config
    ) -> None:
        super().__init__(tx_queue)
        self.event_queue = tx_queue
        self.tf_queue = tf_queue
        self.session = None

        self.config = config["cotproxy"]
        self.cpapi_url = self.config.get("CPAPI_URL", cotproxy.DEFAULT_CPAPI_URL)
        self.pass_all = bool(
            int(self.config.get("PASS_ALL", cotproxy.DEFAULT_PASS_ALL))
        )
        self.auto_add = bool(
            int(self.config.get("AUTO_ADD", cotproxy.DEFAULT_AUTO_ADD))
        )

    async def run(self) -> None:
        self._logger.info("Running COTProxyWorker")
        try:
            async with aiohttp.ClientSession(self.cpapi_url) as self.session:
                while 1:
                    tf_msg: ET.Element = await self.tf_queue.get()
                    self._logger.debug('tf_msg="%s"', ET.tostring(tf_msg))
                    if tf_msg:
                        await self._handle_msg(tf_msg)
        except Exception as exc:
            self._logger.warn(
                "Connection to %s raised an error: %s", self.cpapi_url, exc
            )
            self._logger.warn("Will continue without proxy.")
            self._logger.debug(exc)
            while 1:
                tf_msg: ET.Element = await self.tf_queue.get()
                self._logger.debug('tf_msg="%s"', ET.tostring(tf_msg))
                if tf_msg:
                    await self._handle_msg(tf_msg, use_proxy=False)

    async def _create_cotobject(self, event: ET.Element) -> None:
        uid: str = event.attrib.get("uid")
        callsign: str = cotproxy.get_callsign(event)

        if bool(int(self.config.get("AUTO_ADD"))) and uid:
            self._logger.info("Adding UID=%s", uid)

            # Create a COT Object
            co_url: str = "/co/"
            async with self.session.post(co_url, json={"uid": uid}) as resp:
                self._logger.debug("CO Call: %s", resp.status)

            if callsign:
                # Populate the transform
                tf_url: str = "/tf/"
                tf_payload = {
                    "cot_uid": uid,
                    "cot_type": event.attrib.get("type"),
                    "callsign": callsign,
                }
                self._logger.info(tf_payload)
                async with self.session.post(tf_url, json=tf_payload) as resp:
                    self._logger.debug("TF Call: %s", resp.status)

    async def _transform_event(self, event: ET.Element, tf: dict):
        if tf.get("active"):
            self._logger.info("Transforming UID=%s", event.attrib.get("uid"))
            new_event: ET.Element = cotproxy.transform_cot(event, tf)
            self._logger.info(ET.tostring(new_event))
        else:
            new_event = event
        await self._put_event_queue(ET.tostring(new_event))

    async def _handle_msg(self, event: ET.Element, use_proxy: bool = True) -> None:
        """
        Handles the original COT Event (event).

        If the Event's UID matches a Transform in COT Proxy, we'll hand
        it off to the transform method.

        If the Event's UID does not match a Transform, hand it off to the
        create_object method.

        :param event: Original COT, as popped from the Queue.
        """
        uid: str = event.attrib.get("uid")
        if not uid:
            return

        # If use_proxy is False, default to 'pass through' mode.
        if use_proxy:
            tf_url: str = f"/tf/{uid}.json"
            async with self.session.get(tf_url) as response:
                # self._logger.debug('response=%s', response)
                if response.status == 404:
                    await self._create_cotobject(event)
                    if self.pass_all:
                        await self._put_event_queue(ET.tostring(event))
                elif response.status == 200:
                    await self._transform_event(event, await response.json())
                else:
                    if self.pass_all:
                        await self._put_event_queue(ET.tostring(event))
        else:
            if self.pass_all:
                await self._put_event_queue(ET.tostring(event))
