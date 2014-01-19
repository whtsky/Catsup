.. _post-syntax:

Post Syntax
=============

Catsup currently supports 3 types of post: :ref:`Markdown <post-markdown-syntax>`, :ref:`Text <post-text-syntax>` and :ref:`HTML <post-html-syntax>`.

.. _post-markdown-syntax:

Markdown Post
--------------

Overview
~~~~~~~~~

Post's extension should be either ``.md`` or ``.markdown`` .

A sample post looks like ::

    # Hello, World!                          <---- This is title

    - time: 2013-08-25 23:30                 <---- This is meta
    - tags: hello world

    ---

    Hello, World!                            <---- This is content
    This is my first post in catsup.
    I'm writing in **MarkDown** !
    <strong>HTML is supported, too</strong>

    ```python
    print("I love python")
    ```

A post consists of three parts:

+ Title
+ :ref:`Meta <post-meta>`
+ Content

Title
~~~~~~~~~~~~~~~~~~~~~~

Title should always on the first line and starts with ``#``

Content
~~~~~~~~~~~~~~~~~~~~~~

Everything below the separator is the content. Content should be written in Markdown.

Code Highlight
~~~~~~~~~~~~~~~~~~~~~~

Catsup supports GitHub's style code highlight, like this ::

    ```python
    print("Hello World!")
    ```

.. _post-text-syntax:

Text Post
--------------

Sometimes you may just want to write something without considering the syntax. Then you should use Text Post.

Text post's extension should be ``.txt`` .

The simplest text post looks like ::

    Hello!
    This is a text post.

If you want to write meta in a text post, write the meta in YAML format ::

    ---
    title: Hello, World!
    tags: Hello, World
    time: 2014-01-04 20:56
    ---

    Hello, World! I'm a text post.


.. _post-html-syntax:

HTML Post
--------------

HTML post is like :ref:`Text Post <post-text-syntax>`, but you can use HTML in the content.

HTML post's extension should be ``.txt`` .

A HTML post looks like ::

    ---
    title: Hello, World!
    tags: Hello, World
    time: 2014-01-04 20:56
    ---

    <p>I'm writing HTML in catsup</p>


.. _post-meta:

Meta
--------

Meta is some information about the post.
Note that meta is optional, and if your post have meta, remember to put a :ref:`separator <post-separator>` below the meta.

+ time: When the post is written. like ``2013-08-25 11:10``
+ tags: Tags of the post. Separated by comma, like ``Python, Program``
+ type: Set to ``page`` to turn this post into a page.
+ description: Description of the post.
+ comment: Set to ``disabled`` to forbid comment
+ permalink: Permalink to the post, link ``/this-post``

.. _post-separator:

The separator
----------------

The separator separates meta and content. It should be at least *three* ``-`` ::

    ---

It's okay to make it longer ::

    ----------------

Page
--------

Page is a kind of post. Turn an ordinary post into page by adding ``- type: page`` in post's meta.

So, what's the difference between page and post?

+ Page do not have tags
+ Page do not display in Archives Pages and Index Pages
+ In general, pages will be linked in every page's navigation.