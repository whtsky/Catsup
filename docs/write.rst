Writing
========

Markup
--------

Catsup support markup of Markdown.

A post consists of three parts:

+ Title
+ Meta
+ Content

Here's an example::

    #Hello World!          <---- This is title

    - tags: hello, world   <---- This is meta
    - comment： disabled

    ---

    Hello, World!          <---- This is content


Title should always on the first line and starts with ``#``

Meta is some information about the post. It's below title and above the first ``---``

Content is everything below the first ``---``

Meta
-----

Metadata that catsup supports natively:

+ tags - tags are seprated by comma
+ description - used for SEO and Twitter Card
+ comment - set to ``disabled`` for forbidding comment
+ permalink - permalink to the post.


