from __future__ import with_statement

import os
import time
import re
import misaka as m
import tornado.escape
from tornado.util import ObjectDict

from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name


def load_config(filename='config.py'):
    catsup_path = os.path.dirname(__file__)

    config = ObjectDict(
        catsup_path=catsup_path,
        posts_path=os.path.join(catsup_path, '_posts'),
        common_template_path=os.path.join(catsup_path, 'template'),
        deploy_path=os.path.join(catsup_path, 'deploy'),
        comment_system='disqus',
        disqus_shortname='catsup',
        duoshuo_shortname='catsup',
        feed='feed.xml',
        post_per_page=3,
        gzip=True,
        static_url='static',
        theme_name='sealscript',
        google_analytics=''
    )

    execfile(filename, {}, config)

    if 'theme_path' not in config:
        config.theme_path = os.path.join(catsup_path, 'themes',
            config.theme_name)

    if 'template_path' not in config:
        config.template_path = os.path.join(config.theme_path, 'template')

    if 'static_path' not in config:
        config.static_path = os.path.join(config.theme_path, 'static')

    if config.site_url.endswith('/'):
        config.site_url = config.site_url[:-1]
    if config.static_url.endswith('/'):
        config.static_url = config.static_url[:-1]

    return config


class CatsupRender(m.HtmlRenderer, m.SmartyPants):
    def block_code(self, text, lang):
        if not lang:
            text = tornado.escape.xhtml_escape(text.strip())
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

md = m.Markdown(CatsupRender(flags=m.HTML_ESCAPE | m.HTML_USE_XHTML),
    extensions=m.EXT_FENCED_CODE | m.EXT_NO_INTRA_EMPHASIS | m.EXT_AUTOLINK |
               m.EXT_STRIKETHROUGH | m.EXT_SUPERSCRIPT)


def load_post(file_name, config):
    '''Load a post.return a dict.
    '''
    path = os.path.join(config['posts_path'], file_name)
    print('Loading file %s' % path)
    post = {'file_name': file_name[:-3],
        'tags': [],
        'date': file_name[:10],
        'comment_open' : True,
        'has_excerpt' : False }
    try:
        with open(path, 'r') as file:
            while True:
                line = file.readline()
                line_lower = line.lower()
                # Post title
                if line.startswith('#'):
                    post['title'] = line[1:].strip()
                # Post category(unused)
                elif 'category' in line_lower:
                    post['category'] = line.split(':')[-1].strip()
                # Post tags
                elif 'tags' in line_lower:
                    for tag in line.split(':')[-1].strip().split(','):
                        post['tags'].append(tag.strip())
                # Post date specificed
                elif 'date' in line_lower:
                    post['date'] = line.split(':')[-1].strip()
                # Allow comment of not
                elif 'comment' in line_lower:
                    status = line_lower.split(':')[-1].strip()
                    if status in ['no', 'false', '0', 'close']:
                        post['comment_open'] = False
                # Here many cause an infinite loop if the post has no --- in it
                elif line.startswith('---'):
                    content = '\n'.join(file.readlines())
                    if isinstance(content, str):
                        content = content.decode('utf-8')
                    # Post excerpt support, use <!--more--> as flag
                    if content.lower().find(u'<!--more-->'):
                        post['excerpt'] = md.render(content.split(u'<!--more-->')[0])
                        post['has_excerpt'] = True
                        content = content.replace(u'<!--more-->', '')
                    post['content'] = md.render(content)
                    post['updated'] = os.stat(path).st_ctime
                    updated_xml = time.gmtime(post['updated'])
                    post['updated_xml'] = time.strftime('%Y-%m-%dT%H:%M:%SZ',
                        updated_xml)
                    break; # exit the infinite loop
    except IOError:
        print('Open file %s failed.' % path)
    return post

def load_posts(config):
    '''load all the posts.return a list.
    Sort with filename.
    '''
    # Post file name must match style 2012-12-24-title.md
    pattern = re.compile('^\d{4}\-\d{2}\-\d{2}\-.+\.md', re.I)
    post_files = os.listdir(config['posts_path'])
    post_files.sort(reverse=True)
    posts = []
    for file_name in post_files:
        if pattern.match(file_name):
            post = load_post(file_name, config)
            posts.append(post)
    return posts


def get_infos(posts):
    """return the tag list and archive list.
    """
    tags = {}
    archives = {}
    for post in posts:
        for tag in post['tags']:
            if tag in tags:
                tags[tag].append(post)
            else:
                tags[tag] = [post]
        year = post['date'][:4]
        if year in archives:
            archives[year].append(post)
        else:
            archives[year] = [post]

    return sorted(tags.items(), key=lambda x: len(x[1]), reverse=True),\
           sorted(archives.items(), key=lambda x: x[0], reverse=True)


class FakeHandler(object):

    def __init__(self, config):
        self.settings = config
