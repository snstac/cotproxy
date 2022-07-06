cotproxy - Cursor On Target Transformation Proxy.
*************************************************

COTProxy is an inline Cursor On Target (COT) transformation proxy. Given a 
matching UID & Transform, COT Event charactaristics can be changed, including 
Callsign, Type, Icon, Video, et al. COTProxy's transform configurations are 
managed via the COTProxyWeb front-end.

Concept:

.. image:: https://raw.githubusercontent.com/ampledata/cotproxy/main/docs/cotproxy-concept.png
   :alt: COTProxy concept diagram.
   :target: https://raw.githubusercontent.com/ampledata/cotproxy/main/docs/cotproxy-concept.png


Support Development
===================

**Tech Support**: Email support@undef.net or Signal/WhatsApp: +1-310-621-9598

This tool has been developed for the Disaster Response, Public Safety and
Frontline Healthcare community. This software is currently provided at no-cost
to users. Any contribution you can make to further this project's development
efforts is greatly appreciated.

.. image:: https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png
    :target: https://www.buymeacoffee.com/ampledata
    :alt: Support Development: Buy me a coffee!


Installation
============

COTProxy is available as a Debian ``.deb`` package. This is the preferred way to 
install COTProxy as it will pull in all of the required OS-level dependencies::

    $ sudo apt update
    $ wget https://github.com/ampledata/pytak/releases/latest/download/python3-pytak_latest_all.deb
    $ sudo apt install -f ./python3-pytak_latest_all.deb
    $ wget https://github.com/ampledata/cotproxy/releases/latest/download/python3-cotproxy_latest_all.deb
    $ sudo apt install -f ./python3-cotproxy_latest_all.deb

Install from the Python Package Index (PyPI) [Advanced Users]::

    $ pip install cotproxy

Install from this source tree [Developers]::

    $ git clone https://github.com/ampledata/cotproxy.git
    $ cd cotproxy/
    $ python setup.py install


Usage
=====

COTProxy can be configured using an INI-style config file, or using 
Environment Variables. Configuration Parameters are as follows:

* ``CPAPI_URL``: (``str``) URL of COTProxyWeb API, for example: ``http://localhost:8080/``
* ``LISTEN_URL``: (``str``) Protocol, Local IP & Port to listen for COT Events. Default = ``udp://0.0.0.0:8087``.
* ``KNOWN_CRAFT_FILE``: (``str``) Path to existing Known Craft file to use when seeding COTProxyWeb database. Default = ``known_craft.csv``.
* ``PASS_ALL``: (``bool``) [optional] If True, will pass everything, Transformed or not. Default = ``False``.
* ``AUTO_ADD``: (``bool``) [optional] If True, will automatically create Transforms and Objects for all COT Events. Default = ``False``.
* ``SEED_FAA_REG``: (``bool``) [optional] If True, will set N-Number on seeded ICAO Hexs from FAA database. Default = ``True``.

There are other configuration parameters, including TLS/SSL, available via `PyTAK <https://github.com/ampledata/pytak#configuration-parameters>`_.

Source
======
Github: https://github.com/ampledata/cotproxy


Author
======
Greg Albrecht W2GMD oss@undef.net

https://ampledata.org/


Copyright
=========
COTProxy is Copyright 2022 Greg Albrecht


License
=======
COTProxy is licensed under the Apache License, Version 2.0. See LICENSE for details.
