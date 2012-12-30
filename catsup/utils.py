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
    if not path:
        return
    config = {}
    exec(compile(open(path).read(), path, 'exec'), config, config)
    for name in config:
        if name in options:
            options[name].set(config[name])
        else:
            define(name, config[name])


class Post(ObjectDict):
    """Post object"""
    def has_format(self, format):
        if not hasattr(self, 'format'):
            return False
        if self['format'] == format.lower():
            return True

    @property
    def is_regular(self):
        return self.has_format('regular')

    @property
    def is_aside(self):
        return self.has_format('aside')

    @property
    def is_gallery(self):
        return self.has_format('gallery')

    @property
    def is_link(self):
        return self.has_format('link')

    @property
    def is_status(self):
        return self.has_format('status')

    @property
    def is_image(self):
        return self.has_format('image')

    @property
    def is_video(self):
        return self.has_format('video')

    @property
    def is_audio(self):
        return self.has_format('audio')

    @property
    def is_chat(self):
        return self.has_format('chat')

    @property
    def is_quote(self):
        return self.has_format('quote')


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
        comment_open=True,
        has_excerpt=False,
        excerpt='',
        format='regular',
        category='',
        permalink='%s/%s.html' % (options.site_url, post_permalink)
    )
    try:
        with open(path, 'r') as f:
            # test if the post includes a string ---
            fcontent = f.read()
            if fcontent.find("\n---") == -1:
                logging.warning('The format of post %s is illegal,'
                                ' ignore it.' % path)
                return
            else:
                # fallback to the file's beginning
                f.seek(0, os.SEEK_SET)
                del fcontent
            while True:
                line = f.readline()
                line_lower = line.lower()
                # Post title
                if line.startswith('#'):
                    post.title = xhtml_escape(line[1:].strip())
                # Yet another post title property for compatibility of jekyll
                elif 'title' in line_lower:
                    post.title = xhtml_escape(line.split(':')[-1].strip())
                # Post format
                elif 'format' in line_lower:
                    post_format = line_lower.split(':')[-1].strip()
                    if post_format not in ('regular', 'aside', 'gallery',
                                           'link', 'image', 'quote',
                                           'status', 'video', 'audio', 'chat'):
                        post_format = 'regular'
                    post.format = post_format
                # Post category(unused)
                elif 'category' in line_lower:
                    post.category = xhtml_escape(line.split(':')[-1].strip())
                # Post tags
                elif 'tags' in line_lower:
                    for tag in line.split(':')[-1].strip().split(','):
                        post.tags.append(xhtml_escape(tag.strip().lower()))
                # Post date specificed
                elif 'date' in line_lower:
                    post.date = xhtml_escape(line.split(':')[-1].strip())
                # Allow comment of not
                elif 'comment' in line_lower:
                    status = line_lower.split(':')[-1].strip()
                    if status in ['no', 'false', '0', 'close']:
                        post.comment_open = False
                # Here many cause an infinite loop if the post has no --- in it
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
                    break  # exit the infinite loop
    except IOError:
        logging.error('Open file %s failed.' % path)
    return post


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
