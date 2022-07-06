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

"""COTProxy Utils."""

import argparse
from configparser import ConfigParser, SectionProxy
import csv
from enum import unique
import json
import logging
import os
import urllib.request

from collections import Counter
from typing import Union
from urllib.request import Request

with_pandas: bool = False
try:
    import pandas as pd

    with_pandas = True
except:
    pass

import cotproxy

__author__ = "Greg Albrecht W2GMD <oss@undef.net>"
__copyright__ = "Copyright 2022 Greg Albrecht"
__license__ = "Apache License, Version 2.0"


class CPAPI:

    """API Wrapper class for COTProxyWeb."""

    _logger = logging.getLogger(__name__)
    if not _logger.handlers:
        _logger.setLevel(cotproxy.LOG_LEVEL)
        _console_handler = logging.StreamHandler()
        _console_handler.setLevel(cotproxy.LOG_LEVEL)
        _console_handler.setFormatter(cotproxy.LOG_FORMAT)
        _logger.addHandler(_console_handler)
        _logger.propagate = False
    logging.getLogger("asyncio").setLevel(cotproxy.LOG_LEVEL)

    def __init__(
        self, url: str, kc_file: str = cotproxy.DEFAULT_KNOWN_CRAFT_FILE
    ) -> None:
        self.url = url.rstrip("/")
        self.known_craft = read_known_craft(kc_file)
        self._logger.info("Using URL %s with Known Craft %s", self.url, kc_file)

    def request(
        self, endpoint: str, payload: dict, method: Union[str, None] = None
    ) -> Request:
        """
        Handles making a call to one of the COTProxy API endpoints.

        Parameters
        ----------
        endpoint : `str`
            API endpoint path (e.g. 'tf', 'co')
        payload : `dict`
            Key/Value data to delivery to endpoint.

        Returns
        -------
        `urllib.request.Request`
            Results of `urlopen()` call.
        """
        url = f"{self.url}/{endpoint}/"

        json_payload = json.dumps(payload)
        json_payload_b = json_payload.encode("utf-8")  # needs to be bytes

        req = urllib.request.Request(url, method=method)
        req.add_header("Content-Type", "application/json; charset=utf-8")

        response = urllib.request.urlopen(req, json_payload_b)
        self._logger.debug(response)
        return response

    def create_cotobject(self, payload: dict) -> bool:
        """
        Creates a COT Object.

        Parameters
        ----------
        payload : `dict`
            Data to use to populate the COT Object.

        Returns
        -------
        `bool`
            True if COT Object creation was successful.
        """
        endpoint: str = "co"
        cot_uid: str = payload.get("cot_uid")
        if self.exists(endpoint, cot_uid):
            return True
        try:
            self.request(endpoint, payload)
            self._logger.info("Created COTObject: %s", cot_uid)
        except Exception as exc:
            return False
        return True

    def create_transform(self, payload: dict) -> bool:
        """
        Creates a COT Object.

        Parameters
        ----------
        payload : `dict`
            Data to use to populate the COT Object.

        Returns
        -------
        `bool`
            True if COT Object creation was successful.
        """
        cot_uid: str = payload.get("cot_uid")
        try:
            self.request("tf", payload)
            self._logger.info("Created Transform for: %s", cot_uid)
        except Exception as exc:
            return False
        return True

    def create_iconset(self, uuid: str, name: str) -> Request:
        """
        Creates a COTProxy IconSet.

        Parameters
        ----------
        uuid : `str`
            UUID of the IconSet.
        name : `str`
            Name of the IconSet.

        Returns
        -------
        `urllib.request.Request`
            Results of `make_cp_request()` call.
        """
        endpoint: str = "iconset"
        if self.exists(endpoint, uuid):
            return
        payload = {"uuid": uuid, "name": name}
        self._logger.info("Creating IconSet %s/%s", uuid, name)
        return self.request(endpoint, payload)

    def create_icon(self, iconset_uuid: str, name: str) -> Request:
        """
        Creates a COTProxy Icon within an IconSet

        Parameters
        ----------
        iconset_uuid : str
            UUID of the IconSet to which to add this Icon.
        name : str
            Name of the icon file.

        Returns
        -------
        `urllib.request.Request`
            Results of `make_cp_request()` call.
        """
        endpoint: str = "icon"
        if self.exists(endpoint, name):
            return
        payload: dict = {"iconset": iconset_uuid, "name": name}
        self._logger.info("Creating Icon %s/%s", iconset_uuid, name)
        return self.request(endpoint, payload)

    def exists(self, endpoint: str, pkey: str) -> bool:
        """
        Determines if a _ already exists for the given Primary Key.

        Parameters
        ----------
        pkey : `str`
            Primary Key of _ to test for.

        Returns
        -------
        `bool`
            True if existing _ exists, False otherwise.
        """
        if not pkey:
            return False

        try:
            url = "/".join([self.url, endpoint, pkey])
            urllib.request.urlopen(url)
        except urllib.request.HTTPError as exc:
            if exc.code == 404:
                return False
            else:
                raise
        return True

    def seed_icons(self) -> None:
        """
        Seeds Icon & IconSets from Known Craft file.

        Parameters
        ----------
        """
        for icon in [*Counter([x.get("ICON") for x in self.known_craft]).keys()]:
            icon_split = icon.split("/")
            if len(icon_split) > 1:
                is_uid, is_name, icon_name = icon.split("/")
                self.create_iconset(is_uid, is_name)
                self.create_icon(is_uid, icon_name)

    def seed_known_craft(self) -> None:
        """
        Seeds the COTProxy Transforms with an existing Known Craft file.

        NB NB NB: Only works with ICAO-based known craft.

        Parameters
        ----------
        known_craft : `list[dict]`
            List of known craft dict entries.
        """
        self.seed_icons()
        for craft in self.known_craft:
            payload = create_cp_payload(craft)
            cot_uid = payload.get("cot_uid")
            if not self.exists("tf", cot_uid):
                self.create_cotobject(payload)
                self.create_transform(payload)

    def seed_faa_reg(self, seed_all: bool = False) -> None:
        if not with_pandas:
            self._logger.warning(
                "Pandas not installed, install with: python3 -m pip install cotproxy[with_pandas]"
            )
            return

        endpoint: str = "co"
        self._logger.info("Seeding with FAA Registration database")
        faa_main = pd.read_csv("ReleasableAircraft/MASTER.TXT", dtype=str)
        reduced_main = faa_main[
            ["N-NUMBER", "TYPE REGISTRANT", "UNIQUE ID", "MODE S CODE HEX"]
        ]
        # make sure indexes pair with number of rows
        reset_main = reduced_main.reset_index()
        for index, row in reset_main.iterrows():
            cot_uid: str = f"ICAO-{row['MODE S CODE HEX']}".strip()
            n_number: str = f"N{row['N-NUMBER']}".strip()
            payload: dict = {
                "uid": cot_uid,
                "cot_uid": cot_uid,
                "n_number": n_number,
            }

            if self.exists(endpoint, cot_uid):
                self._logger.info("Updating COTObject: %s (%s)", cot_uid, n_number)
                self.request(f"{endpoint}/{cot_uid}", payload, method="PUT")


def read_known_craft(kc_file: Union[str, None] = None) -> list:
    """
    Reads a known_craft file into an iterable list of Python dics.

    Parameters
    ----------
    kc_file : `str`
        Path to known_craft file to read-in.

    Returns
    -------
    `list[dict]`
        List of known_craft key/values.
    """
    kc_file: str = kc_file or cotproxy.DEFAULT_KNOWN_CRAFT_FILE
    all_rows = []
    with open(kc_file) as csv_fd:
        reader = csv.DictReader(csv_fd)
        for row in reader:
            all_rows.append(row)
    return all_rows


def create_cp_payload(craft: dict) -> dict:
    """Creates Payload for COTProxyWeb API."""
    craft: dict = {k.lower().strip(): v for k, v in craft.items()}

    cot_uid: str = f"ICAO-{craft['hex']}"

    craft["hex"] = craft["hex"].strip()
    craft["icon"] = craft["icon"].split("/")[-1]
    craft["cot_type"] = craft["cot"]
    craft["uid"] = cot_uid
    craft["cot_uid"] = cot_uid
    craft["active"] = True

    return craft


def _seed(config):
    """Seeds COTProxyWeb database from existing Known Craft file."""
    kc_file: str = config.get("KNOWN_CRAFT", cotproxy.DEFAULT_KNOWN_CRAFT_FILE)
    if not os.path.exists(kc_file):
        logging.error("File does not exist: %s", kc_file)

    cp_api = CPAPI(config.get("CPAPI_URL"), kc_file)
    cp_api.seed_known_craft()
    if config.getboolean("SEED_FAA_REG", cotproxy.DEFAULT_SEED_FAA_REG):
        cp_api.seed_faa_reg()


def seed():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-c",
        "--CONFIG_FILE",
        dest="CONFIG_FILE",
        default="config.ini",
        type=str,
        help="Optional configuration file. Default: config.ini",
    )
    parser.add_argument(
        "-s",
        "--KNOWN_CRAFT",
        dest="KNOWN_CRAFT",
        default=cotproxy.DEFAULT_KNOWN_CRAFT_FILE,
        type=str,
        help=f"Optional Known Craft CSV file. Default: {cotproxy.DEFAULT_KNOWN_CRAFT_FILE}",
    )
    namespace = parser.parse_args()
    cli_args = {k: v for k, v in vars(namespace).items() if v is not None}

    # Read config:
    env_vars = os.environ
    config: ConfigParser = ConfigParser(env_vars)

    config_file = cli_args.get("CONFIG_FILE")
    if os.path.exists(config_file):
        logging.info("Reading configuration from %s", config_file)
        config.read(config_file)
    else:
        config.add_section("cotproxy")

    config: SectionProxy = config["cotproxy"]
    _seed(config)
