#coding=utf-8
import os
import re
import logging
import misaka

from tornado.escape import xhtml_escape
from tornado.util import ObjectDict

from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name
from pygments.util import ClassNotFound

from catsup.options import config, g


class Post(ObjectDict):
    """Post object"""
    pass


class CatsupRender(misaka.HtmlRenderer, misaka.SmartyPants):
    def block_code(self, text, lang):
        try:
            lexer = get_lexer_by_name(lang, stripall=True)
        except ClassNotFound:
            text = xhtml_escape(text.strip())
            return '\n<pre><code>%s</code></pre>\n' % text
        else:
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

    path = os.path.join(config.config['posts'], file_name)
    logging.info('Loading file %s' % path)
    post_permalink = file_name[:-3].lower()
    """
    //TODO: custome permalink
    if not options.date_in_permalink:
        post_permalink = file_name[11:-3]
    """
    post = Post(
        file_name=post_permalink,
        tags=[],
        date=file_name[:10],
        comment_disabled=False,
        has_excerpt=False,
        excerpt='',
        category='',
        permalink='/%s.html' % post_permalink,
    )
    try:
        f = open(path, 'r')
    except IOError:
        logging.error('Open file %s failed.' % path)
    else:
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
                    # provide compatibility with jekyll,
                    # ignore first line if it starts with `---`
                    continue
                content = '\n'.join(lines[i + 1:])
                # Provide compatibility for liquid style code highlight
                content = pattern.sub(_highlightcode, content)
                # Post excerpt support, use <!--more--> as flag
                if content.lower().find('<!--more-->'):
                    excerpt = content.split('<!--more-->')[0]
                    post.excerpt = md.render(excerpt)
                    post.has_excerpt = True
                    content = content.replace('<!--more-->',
                                              '<span id="readmore"></span>')
                post.content = md.render(content)
                post.updated = os.stat(path).st_ctime
                f.close()
                return post
        logging.warning('The format of post %s is illegal,'
                        ' ignore it.' % path)


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
            p1 = os.stat(os.path.join(config.config['posts'], p1)).st_ctime
            p2 = os.stat(os.path.join(config.config['posts'], p2)).st_ctime
        return cmp(p1, p2)

    # Post file name must match style 2012-12-24-title.md
    pattern = re.compile('^\d{4}\-\d{2}\-\d{2}\-.+\.md$', re.I)
    files = [x for x in os.listdir(config.config['posts']) if pattern.match(x)]
    files.sort(reverse=True, cmp=_cmp_post)
    posts = []
    for file_name in files:
        post = load_post(file_name)
        if post:
            posts.append(post)
    g.posts = posts

    tags = {}
    archives = {}
    for post in posts:
        for tag in post.tags:
            tag = tag.capitalize()
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
    g.tags = sorted(tags.values(), key=lambda x: x.post_count, reverse=True)
    g.archives = sorted(archives.values(), key=lambda x: x.name, reverse=True)
