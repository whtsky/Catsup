================
catsup
================

.. image:: https://travis-ci.org/whtsky/catsup.png?branch=master
    :target: https://travis-ci.org/whtsky/catsup

A lightweight static blog generator.

Install
========

Simple way using pip::

    pip install catsup


Or another hard way to install::

    git clone git://github.com/whtsky/catsup.git
    cd catsup
    python setup.py install


Settings
========

The default settings file is at ``~/.catsuprc``,
you can specific it by passing ``--settings=/path/to/settings`` when executing ``catsup <server/build/webhook>``

For simple usage, just copy and rename ``config.py`` to ``~/.catsuprc`` and modify it as you like.

Write a post
============
catsup uses Markdown to write posts.
Filename should like ``year-month-day-title.md``

(For example: ``2000-01-01-catsup.md``)

Post Example::

    #Title

    ====

    Content
    ```python
    print "hi,I'm coding."
    ```

Post properties
================
catsup supports some post properties. Write them before ``---``
 and start with ``-`` .
Example::

    - category: A Category
    - date: 2012-12-24
    - tags: tag1, tag2
    - comment: disabled

The ``category`` property defines the category of the post, but it's not used yet.

The ``date`` property can overwrite the date from the file name.

The ``tags`` property defines the tags of the post.

The ``comment`` property defines whether the post can be commented or not.

Post excerpt
-------------
You can use ``<!--more-->`` to define an excerpt of a post.
Any content before that will be used as excerpt of the post.
And you can choose to display excerpt rather than full content on your homepage.

Build your blog
=================
run ``catsup build``
And you can find your static blog in ``~/build/`` .