cotproxy - Cursor On Target Transformation Proxy.
*************************************************

COTProxy is an inline Cursor On Target (COT) transformation proxy. Given a 
matching UID & Transform, COT Event characteristics can be changed, including 
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

* ``CPAPI_URL``: URL of COTProxyWeb API, for example: ``http://localhost:8080/``
* ``LISTEN_URL``: Protocol, Local IP & Port to listen for COT Events. Default = ``udp://0.0.0.0:8087``.
* ``KNOWN_CRAFT_FILE``: Path to existing Known Craft file to use when seeding COTProxyWeb database. Default = ``known_craft.csv``.
* ``PASS_ALL``: [optional] If True, will pass everything, Transformed or not. Default = ``False``.
* ``AUTO_ADD``: [optional] If True, will automatically create Transforms and Objects for all COT Events. Default = ``False``.
* ``SEED_FAA_REG``: [optional] If True, will set Tail/N-Number on seeded ICAO Hexs from FAA database. Default = ``True``.

There are other configuration parameters, including TLS/SSL, available via `PyTAK <https://github.com/ampledata/pytak#configuration-parameters>`_.


Installing with pyenv
=====================

## In Debian 10/11::

    $ sudo apt-get install make build-essential libssl-dev zlib1g-dev \
        libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm \
        libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev \
        libffi-dev liblzma-dev git
    $ curl https://pyenv.run | bash

Add the following to your ~/.bashrc and restart your shell::

    export PYENV_ROOT="$HOME/.pyenv"
    command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"
    eval "$(pyenv init -)"
    eval "$(pyenv virtualenv-init -)"

Once back in::

    $ pyenv install 3.9.13
    ...Catch up on your expense reports, have a snack, stay hydrated...
    $ pyenv shell 3.9.13
    $ pyenv virtualenv pytakenv
    $ pyenv activate pytakenv
    $ python3 -m pip install --upgrade pip
    $ mkdir ~/src
    $ cd ~/src
    $ git clone https://github.com/ampledata/cotproxy.git
    $ cd cotproxy
    $ python3 setup.py install
    $ cd ~/src
    $ git clone https://github.com/ampledata/cotproxyweb.git
    $ cd cotproxyweb
    $ python3 -m pip install -r requirements.txt
    $ bash setup.sh
    ... When prompted, select an admin password. ...

You should now be able to connect to port :8000/admin from a web browser.

Seed COTProxy Transforms frome existing Known Craft file, given a Known Craft 
file named ``known_ps.csv``::

    $ CPAPI_URL="http://localhost:8000/" KNOWN_CRAFT=known_ps.csv cotproxy-seed


## CentOS 7

1. Update packages::

    sudo yum update
    sudo yum check-update

2. Install required packages::

    sudo yum groupinstall -y "Development Tools"
    sudo yum install -y zlib zlib-devel bzip2-devel openssl-devel sqlite-devel readline-devel libffi-devel lzma-sdk-devel ncurses-devel gdbm-devel db4-devel expat-devel libpcap-devel xz-devel pcre-devel wget

3. Install updated SQLite::

    mkdir -p ~/src
    cd ~/src
    wget https://www.sqlite.org/2019/sqlite-autoconf-3290000.tar.gz
    tar zxvf sqlite-autoconf-3290000.tar.gz
    cd sqlite-autoconf-3290000
    ./configure
    make
    sudo make install

3. Install PyEnv::
    
    curl https://pyenv.run | bash

4. Update ``~/.bash_profile``:

The following chunk of code should be appended to the end of your ``~/.bash_profile``, 
either using a text editor like ``vi``, ``vim``, ``nano`` or ``pico``. Once added, 
reload your environment by running: ``source ~/.bash_profile``::

    export PYENV_ROOT="$HOME/.pyenv"
    command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"
    eval "$(pyenv init -)"
    eval "$(pyenv virtualenv-init -)"
    export PATH=/opt/sqlite/bin:$PATH
    export LD_LIBRARY_PATH=/opt/sqlite/lib
    export LD_RUN_PATH=/opt/sqlite/lib
    export C_INCLUDE_PATH=/opt/sqlite/include
    export CPLUS_INCLUDE_PATH=/opt/sqlite/include

5. Install Python 3.9 environment::

    pyenv install 3.9.13
    pyenv shell 3.9.13
    pyenv virtualenv cpenv

6. Install cotproxy::

    mkdir -p ~/src
    cd ~/src
    wget https://github.com/ampledata/cotproxy/archive/refs/tags/v1.0.0b1.tar.gz
    tar -zvxf v1.0.0b1.tar.gz
    cd cotproxy-1.0.0b1/
    python3 setup.py install

7. Install & Initialize cotproxyweb::

    mkdir -p ~/src
    cd ~/src
    git clone https://github.com/ampledata/cotproxyweb.git
    cd cotproxyweb/
    python3 -m pip install -r requirements.txt
    python3 manage.py migrate
    python3 manage.py createsuperuser \
    --username admin --email admin@undef.net
    python3 manage.py runserver 0:8000

8. From here follow the standard configuration options for ``cotproxy``.


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
