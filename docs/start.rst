.. _get-started:

Get Started
================

This section needs you have catsup installed.If you don't, please go and :ref:`Install it <installation>`

Create a site
---------------
It's pretty simple to create a site using catsup ::

    cd ~
    mkdir site
    cd site
    catsup init

You'll be asked some questions. These questions have default value, so if you don't want to change them,
just hit enter.

Create a post
----------------

Create a post ::

    touch posts/2013-02-08-helloworld.md

.. attention:: Post's filename should like ``year-month-day-title.md``. ``2013-2-2-hi.md`` is not vailed.

Then edit it with your favorite editor ::

    mate posts/2013-02-08-helloworld.md

Build your site
----------------
Now you have written your first post.Let's build your site ::

    cd ~/site
    catsup build

You can also preview your site using :ref:`Preview Server <preview-server>`
