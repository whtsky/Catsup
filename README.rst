catsup
----------------

.. image:: https://pypip.in/d/catsup/badge.png
        :target: https://crate.io/packages/catsup/

Catsup is a lightweight static website generator which aims to be simple and elegant.
Documentation is available at RTFD: https://catsup.readthedocs.org/en/latest/

Quick Start
===============

First, install catsup via pip ::

    $ pip install catsup

Then, craete a new catsup site ::

    $ mkdir site
    $ cd site
    $ catsup init

Edit the config file ::

    vim config.json

Write some posts ::

    $ vim posts/hello-world.md
    $ cat posts/hello-world.md
    # Hello World

    - tags: hello world, catsup
    - time: 2013-08-30 12:00

    ---

    Hello, World!

Build your site and deploy ::

    catsup build && catsup deploy

For more information, please read the document: https://catsup.readthedocs.org/en/latest/