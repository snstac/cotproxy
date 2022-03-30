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

import cotproxy


__author__ = 'Greg Albrecht W2GMD <oss@undef.net>'
__copyright__ = 'Copyright 2022 Greg Albrecht'
__license__ = 'Apache License, Version 2.0'


@pytest.fixture
def sample_xml():
    with open('tests/sample.xml') as sample:
        return sample.read()


def test_parse_cot(sample_xml):
    root = cotproxy.parse_cot(sample_xml)
    assert isinstance(root, ET.Element)
    assert root.attrib.get('uid') == 'MMSI-993692001'
    # print(root.attrib.get('uid'))
    # for child in root:
    #     print(child.tag, child.attrib)


def test_transform_cot(sample_xml):
    original = cotproxy.parse_cot(sample_xml)
    transform = {'callsign': 'TACO1', 'cot_uid': 'MMSI-1234'}
    new_cot = cotproxy.transform_cot(original, transform)
    # print(ET.dump(new_cot))
    assert new_cot.find('detail').attrib['callsign'] == transform['callsign']
    assert new_cot.find('detail').find('contact').attrib['callsign'] == transform['callsign']
