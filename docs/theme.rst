Theme
========

Overview
---------

Install a theme ::

    catsup install git_repo

Install a theme in global ::

    catsup install git_repo -g

Update a installed theme ::

    catsup install theme_name

List all themes installed ::

    catsup themes


Structure
----------

Catsup uses Jinja2 as a Template Engine.You need to learn it if you want to design your own theme.

You can learn how to design your theme by demo:

+ https://github.com/whtsky/catsup-theme-sealscript

A catsup theme should look like ::

    ├── README.md                      <-------- how to install/customize your theme.Used in GitHub.
    ├── static                         <-------- static files
    │   ├── css
    │   │   ├── pygments_style.css     <-------- catsup uses Pygments to highlight code
    │   │   └── style.css
    ├── templates                      <-------- template files
    │   ├── post.html
    │   ├── page.html
    ├── filters.py                     <--------- filters defined by theme
    └── theme.py                       <--------- meta file

Only ``post.html`` and ``page.html`` are required.

Meta File
-----------

A demo meta file ::

    name = 'sealscript'
    author = 'Lyric'
    homepage = 'https://github.com/whtsky/catsup-theme-sealscript'
    vars = {
        "github": "whtsky",
    }

A theme meta consists of :

+ name
+ author
+ homepage
+ vars

What's Vars for?
~~~~~~~~~~~~~~~~~~

Your theme may need some var that user defined in config file.
But **they may miss some var**, so you need to give a default value in theme's meta file.

Variables
----------

Global Variables
~~~~~~~~~~~~~~~~~~

+ site: ``site`` in user's config file.
+ author: ``author`` in user's config file.
+ config: ``config`` in user's config file.
+ comment: ``commment`` in user's config file.
+ theme: ``theme.vars`` in user's config file.

If you want more:

+ g.posts: posts sorted with date.
+ g.tags: tags sorted with posts' count
+ g.archives: archives sorted with year

Templatable Variables
~~~~~~~~~~~~~~~~~~~~~~

Templatable variables are only accessed in specify templates.

+ pagination: available in ``page.html``
+ post: available in ``post.html``
+ prev, next: available in ``post.html``, ``tag.html`` and ``archive.html``

Filters and Functions
----------------------

Catsup has a build-in function: ``static_url`` ::

    <link rel="stylesheet" href="{{ static_url("css/style.css") }}" type="text/css" />

Every function in ``filters.py`` will be a filter.Catsup also has some build-in filter:

+ xmldatetime
+ capitalize

Template Marco
---------------
Catsup has some powerful marco to make your job easier

+ render_comment(post): render post's comment part.
+ meta(post): render post's meta tag.Should be used id ``<head>``.
+ analytics(): render google analytics code.

Use them like ::

    <html>
        <head>
            <title>{{ title }}</title>
            {% from 'utils.html' import meta, analytics %}
            {{ meta() }}
            {{ analytics() }}
        </head>
        <body>
            <article>
                <h1>{{ title }}</h1>
                {{ content }}
                {% from 'utils.html' import render_comment %}
                {{ render_comment() }}
            </article>
        </body>
    </html>

This is a simple ``post.html`` template using catsup's template marco.Isn't that simple?