#coding=utf-8
from __future__ import with_statement

import os
import time
import re
import misaka as m

import logging
from tornado.escape import xhtml_escape
from tornado.util import ObjectDict
from tornado.options import options, define

from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name


def parse_config_file(path):
    if path and os.path.exists(path):
        print('Parsing settings file %s' % path)
        config = {}
        exec(compile(open(path).read(), path, 'exec'), config, config)
        for name in config:
            if name in options:
                options[name].set(config[name])
            else:
                define(name, config[name])
    else:
        print('No settings file provided or it does not exists')
    # execute the codes below no matter whether config file exists or not
    if 'theme_path' not in options:
        define('theme_path', os.path.join(options.themes_path, options.theme_name))
    if 'template_path' not in options:
        define('template_path', os.path.join(options.theme_path, 'template'))
    if 'static_path' not in options:
        define('static_path', os.path.join(options.theme_path, 'static'))
    if options.site_url.endswith('/'):
        options.site_url = options.site_url[:-1]
    if options.static_url.endswith('/'):
        options.static_url = options.static_url[:-1]
    if not (options.site_url == ''
            or options.site_url.startswith('http://')
            or options.site_url.startswith('https://')
            or options.site_url.startswith('//')):
        options.site_url = "//%s" % options.site_url


class Post(ObjectDict):
    """Post object"""
    pass


class CatsupRender(m.HtmlRenderer, m.SmartyPants):
    def block_code(self, text, lang):
        if not lang:
            text = xhtml_escape(text.strip())
            return '\n<pre><code>%s</code></pre>\n' % text
        lexer = get_lexer_by_name(lang, stripall=True)
        formatter = HtmlFormatter()
        return highlight(text, lexer, formatter)

    def autolink(self, link, is_email):
        if is_email:
            return '<a href="mailto:%(link)s">%(link)s</a>' % {'link': link}

        if '.' in link:
            name_extension = link.split('.')[-1].lower()
            if name_extension in ('jpg', 'png', 'git', 'jpeg'):
                return '<img src="%s" />' % link

        return '<a href="%s">%s</a>' % (link, link)

# Allow use raw html in .md files
md = m.Markdown(CatsupRender(flags=m.HTML_USE_XHTML),
    extensions=m.EXT_FENCED_CODE | m.EXT_NO_INTRA_EMPHASIS | m.EXT_AUTOLINK |
               m.EXT_STRIKETHROUGH | m.EXT_SUPERSCRIPT)


def load_post(file_name):
    '''Load a post.return a dict.
    '''
    def _highlightcode(m):
        '''Function for replace liquid style code highlight to github style
        '''
        return "```%s\n%s\n```" % (m.group(1), m.group(2))

    pattern = re.compile('\{%\s?highlight ([\w\-\+]+)\s?%\}\n'
                         '*(.+?)'
                         '\n*\{%\s?endhighlight\s?%\}', re.I | re.S)

    path = os.path.join(options.posts_path, file_name)
    logging.info('Loading file %s' % path)
    post_permalink = file_name[:-3].lower()
    if not options.date_in_permalink:
        post_permalink = file_name[11:-3]
    post = Post(
        file_name=post_permalink,
        tags=[],
        date=file_name[:10],
        comment_disabled=False,
        has_excerpt=False,
        excerpt='',
        format='regular',
        category='',
        permalink='%s/%s.html' % (options.site_url, post_permalink)
    )
    try:
        with open(path, 'r') as f:
            lines = f.readlines()
            for line in lines:
                line_lower = line.lower()
                # Post title
                if line.startswith('#'):
                    post.title = xhtml_escape(line[1:].strip())
                elif 'tags' in line_lower:
                    for tag in line.split(':')[-1].strip().split(','):
                        post.tags.append(xhtml_escape(tag.strip().lower()))
                elif 'comment' in line_lower:
                    status = line_lower.split(':')[-1].strip()
                    if status in ['no', 'disabled', 'close']:
                        post.comment_disabled = True
                # Post properties
                elif ':' in line_lower and '-' in line_lower:
                    line = line.split('-')[1].strip()
                    name, value = line.split(':')
                    post[name.strip()] = value.strip()

                elif line.startswith('---'):
                    content = '\n'.join(f.readlines())
                    if isinstance(content, str):
                        content = content.decode('utf-8')
                    # Provide compatibility for liquid style code highlight
                    content = pattern.sub(_highlightcode, content)
                    # Post excerpt support, use <!--more--> as flag
                    if content.lower().find(u'<!--more-->'):
                        excerpt = content.split(u'<!--more-->')[0]
                        post.excerpt = md.render(excerpt)
                        post.has_excerpt = True
                        content = content.replace(u'<!--more-->',
                            u'<span id="readmore"><!--more--></span>')
                    post.content = md.render(content)
                    post.updated = os.stat(path).st_ctime
                    updated_xml = time.gmtime(post['updated'])
                    post.updated_xml = time.strftime('%Y-%m-%dT%H:%M:%SZ',
                        updated_xml)
                    return post
            logging.warning('The format of post %s is illegal,'
                            ' ignore it.' % path)
    except IOError:
        logging.error('Open file %s failed.' % path)


def load_posts():
    '''load all the posts.return a list.
    Sort with filename.
    '''
    def _cmp_post(p1, p2):
        """
        Post sort compare function
        """
        if p1[:10] == p2[:10]:
            # Posts in the same day
            p1_updated = os.stat(os.path.join(options.posts_path, p1)).st_ctime
            p2_updated = os.stat(os.path.join(options.posts_path, p2)).st_ctime
            if p1_updated > p2_updated:
                return 1
            elif p1_updated < p2_updated:
                return -1
            else:
                return 0
        else:
            if p1 > p2:
                return 1
            elif p1 < p2:
                return -1
            else:
                return 0

    # Post file name must match style 2012-12-24-title.md
    pattern = re.compile('^\d{4}\-\d{2}\-\d{2}\-.+\.md$', re.I)
    post_files = os.listdir(options.posts_path)
    post_files.sort(reverse=True, cmp=_cmp_post)
    posts = []
    for file_name in post_files:
        if pattern.match(file_name):
            post = load_post(file_name)
            if post:
                posts.append(post)
    return posts


def get_infos(posts):
    """return the tag list and archive list.
    """
    tags = {}
    archives = {}
    for post in posts:
        for tag in post.tags:
            if tag in tags:
                tags[tag].posts.append(post)
                tags[tag].post_count += 1
            else:
                tags[tag] = ObjectDict(
                    name=tag,
                    posts=[post],
                    post_count=1
                )
        year = post.date[:4]
        if year in archives:
            archives[year].posts.append(post)
            archives[year].post_count += 1
        else:
            archives[year] = ObjectDict(
                name=year,
                posts=[post],
                post_count=1
            )
    return sorted(tags.itervalues(), key=lambda x: x.post_count, reverse=True),\
           sorted(archives.itervalues(), key=lambda x: x.name, reverse=True)
