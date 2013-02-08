.. _get-started:

Get Started
================

This section needs you have catsup installed.If you don't, please go and :ref:`Install it <installation>`

Create a blog
---------------
It's pretty simple to create a blog using catsup ::

    cd ~
    mkdir blog
    cd blog
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

Build your blog
----------------
Now you have written your first post.Let's build your blog ::

    cd ~/blog
    catsup build

You can also preview your blog before build it using :ref:`Preview Server <preview-server>`
