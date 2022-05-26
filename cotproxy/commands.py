#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""COTProxy Commands."""

import argparse
import asyncio
import configparser
import logging
import os
import sys

from urllib.parse import urlparse, ParseResult

import pytak

import cotproxy

# Python 3.6 support:
if sys.version_info[:2] >= (3, 7):
    from asyncio import get_running_loop
else:
    from asyncio import _get_running_loop as get_running_loop


__author__ = "Greg Albrecht W2GMD <oss@undef.net>"
__copyright__ = "Copyright 2022 Greg Albrecht"
__license__ = "Apache License, Version 2.0"


async def main(config):
    tx_queue: asyncio.Queue = asyncio.Queue()  # aka event_queue
    rx_queue: asyncio.Queue = asyncio.Queue()
    tf_queue: asyncio.Queue = asyncio.Queue()  # aka msg_queue

    cot_url: ParseResult = urlparse(config["cotproxy"].get("COT_URL"))

    # Create our RX & TX Protocols:
    rx_proto, tx_proto = await pytak.protocol_factory(cot_url)

    # Create our RX & TX COT Event Queue Workers:
    tx_worker = pytak.EventTransmitter(tx_queue, tx_proto)
    rx_worker = pytak.EventReceiver(rx_queue, rx_proto)

    msg_worker = cotproxy.NetWorker(tf_queue, config)
    tf_worker = cotproxy.COTProxyWorker(tf_queue, tx_queue, config)

    await tx_queue.put(pytak.hello_event("cotproxy"))

    done, _ = await asyncio.wait(
        set([rx_worker.run(), tx_worker.run(), msg_worker.run(), tf_worker.run()]),
        return_when=asyncio.FIRST_COMPLETED,
    )

    for task in done:
        print(f"Task completed: {task}")


def cli():
    """Command Line interface for Cursor On Target Transform Proxy."""

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-c", "--CONFIG_FILE", dest="CONFIG_FILE", default="config.ini", type=str
    )
    namespace = parser.parse_args()
    cli_args = {k: v for k, v in vars(namespace).items() if v is not None}

    # Read config:
    env_vars = os.environ
    env_vars["COT_URL"] = env_vars.get("COT_URL", cotproxy.DEFAULT_COT_URL)
    env_vars["DEBUG"] = env_vars.get("DEBUG", 0)
    config = configparser.ConfigParser(env_vars)

    config_file = cli_args.get("CONFIG_FILE")
    if os.path.exists(config_file):
        logging.info("Reading configuration from %s", config_file)
        config.read(config_file)
    else:
        config.add_section("cotproxy")

    if sys.version_info[:2] >= (3, 7):
        asyncio.run(main(config)) #, debug=config["cotproxy"].getboolean("DEBUG"))
    else:
        loop = get_running_loop()
        try:
            loop.run_until_complete(main(config))
        finally:
            loop.close()


if __name__ == "__main__":
    cli()
