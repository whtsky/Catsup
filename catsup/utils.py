#coding=utf-8
from __future__ import with_statement

import os
import time
import re
import logging
import misaka

from tornado.escape import xhtml_escape
from tornado.util import ObjectDict
from tornado.options import options

from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name


class Post(ObjectDict):
    """Post object"""
    pass


class CatsupRender(misaka.HtmlRenderer, misaka.SmartyPants):
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
md = misaka.Markdown(CatsupRender(flags=misaka.HTML_USE_XHTML),
                     extensions=misaka.EXT_FENCED_CODE |
                     misaka.EXT_NO_INTRA_EMPHASIS |
                     misaka.EXT_AUTOLINK |
                     misaka.EXT_STRIKETHROUGH |
                     misaka.EXT_SUPERSCRIPT)


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
        permalink='%s/%s.html' % (options.site_url, post_permalink),
        status=''
    )
    try:
        with open(path, 'r') as f:
            lines = f.readlines()
            for i, line in enumerate(lines):
                line_lower = line.lower()
                # Post title
                if line.startswith('#'):
                    post.title = xhtml_escape(line[1:].strip())
                elif 'tags' in line_lower:
                    tags = line.split(':')[-1].strip()
                    if tags.startswith('[') and tags.endswith(']'):
                        # provide compatibility with jekyll's liquid style tags
                        tags = tags[1:-1]
                    for tag in tags.split(','):
                        post.tags.append(xhtml_escape(tag.strip().lower()))
                elif 'comment' in line_lower:
                    status = line_lower.split(':')[-1].strip()
                    if status in ('no', 'disabled', 'close'):
                        post.comment_disabled = True
                # Post properties
                elif ':' in line_lower:
                    if '-' in line_lower:
                        # make '-' be optional in properties
                        line = line.split('-')[1].strip()
                    name, value = line.split(':')
                    post[name.strip()] = value.strip()

                elif line.startswith('---'):
                    if i == 0:
                        # provide compatibility with jekyll, ignore first line if it starts with `---`
                        continue
                    content = '\n'.join(lines[i + 1:])
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
                                                  u'<span id="readmore"></span>')
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
            if post and post.status.lower() != 'draft':
                # do not load post whose status is draft
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


def write(file_name, page):
    if not file_name.startswith(options.build_path):
        file_name = os.path.join(options.build_path, file_name)
    open(file_name, 'w').write(page)


def update_posts():
    logging.info('Updating posts...')
    os.chdir(options.posts_path)
    if os.path.isdir(os.path.join(options.posts_path, '.git')):
        os.system('git pull')
    elif os.path.isdir(os.path.join(options.posts_path, '.hg')):
        os.system('hg pull')
