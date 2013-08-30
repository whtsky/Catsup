.. _post-syntax:

Post Syntax
=============

Overview
-----------

A post's extension should be either ``.md`` or ``.markdown`` .

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
+ Meta
+ Content

Title
--------

Title should always on the first line and starts with ``#``

.. _post-meta:

Meta
-------

Meta is some information about the post. It's below title and above the separator.


+ time: When the post is written. like ``2013-08-25 11:10``
+ tags: Tags of the post. Separated by comma, like ``Python, Program``
+ type: Set to ``page`` to turn this post into a page.
+ description: Description of the post.
+ comment: Set to ``disabled`` to forbid comment
+ permalink: Permalink to the post, link ``/this-post``

The separator
---------------

The separator separates meta and content. It should be at least *three* ``-`` ::

    ---

It's okay to make it longer ::

    ----------------

Content
-----------

Everything below the separator is the content. Content should be written in Markdown.

Code Highlight
-----------------

Catsup supports GitHub's style code highlight, like this ::

    ```python
    print("Hello World!")
    ```


Page
--------

Page is a kind of post. Turn an ordinary post into page by adding ``- type: page`` in post's meta.

So, what's the difference between page and post?

+ Page do not have tags
+ Page do not display in Archives Pages and Index Pages
+ In general, pages will be linked in every page's navigation.