#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import asyncio
from cmath import isnan
import enum
import inspect
import urllib
import xml.etree.ElementTree as ET

from unittest import mock

import pytest

import cotproxy.utils


__author__ = "Greg Albrecht W2GMD <oss@undef.net>"
__copyright__ = "Copyright 2022 Greg Albrecht"
__license__ = "Apache License, Version 2.0"


@pytest.fixture
def sample_xml():
    with open("tests/sample.xml") as sample:
        return sample.read()


def test_read_known_craft():
    known_craft: list = cotproxy.utils.read_known_craft()
    assert isinstance(known_craft, list) == True


def test_get_icons():
    known_craft: list = cotproxy.utils.read_known_craft()
    assert isinstance(known_craft, list) == True
    icons = cotproxy.utils.get_icons(known_craft)
    assert icons == True
