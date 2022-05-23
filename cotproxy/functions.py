import xml.etree.ElementTree as ET


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


def transform_cot(original, transform) -> ET.Element:
    uid = transform.get("uid")
    detail = original.find("detail")
    # assert uid == detail.attrib['uid']
    callsign = transform.get("callsign")
    if callsign:
        original.find("detail").attrib["callsign"] = callsign
        original.find("detail").find("contact").attrib["callsign"] = callsign

    cot_type = transform.get("cot_type")
    if cot_type:
        original.attrib["type"] = cot_type

    return original
