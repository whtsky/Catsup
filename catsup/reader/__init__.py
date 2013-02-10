import os
import re
import logging

from tornado.util import ObjectDict
from tornado.escape import xhtml_escape

from catsup.options import config, g
from catsup.reader.markdown import md_escape, md_raw
from .utils import get_description, get_summary
from .archive import Archive
from .tag import Tag

highlight_liquid = re.compile('\{%\s?highlight ([\w\-\+]+)\s?%\}\n'
                     '*(.+?)'
                     '\n*\{%\s?endhighlight\s?%\}', re.I | re.S)


class Post(ObjectDict):
    """Post object"""
    @property
    def content(self):
        return self.render(self.source.replace('<!--more-->', ''))

    def render(self, content):
        if self.get('escape', config.config.escape_md):
            md = md_escape
        else:
            md = md_raw
        return md.render(content)


def load_post(file_name):
    '''Load a post.return a dict.
    '''
    def _highlightcode(m):
        '''Function for replace liquid style code highlight to github style
        '''
        return "```%s\n%s\n```" % (m.group(1), m.group(2))

    path = os.path.join(config.config.source, file_name)
    logging.info('Loading file %s' % path)
    post_permalink = file_name[:-3].lower()
    post = Post(
        file_name=post_permalink,
        tags=[],
        date=file_name[:10],
        permalink='/%s.html' % post_permalink,
        updated=os.stat(path).st_ctime,
    )
    try:
        f = open(path, 'r')
    except IOError:
        logging.error('Open file %s failed.' % path)
    else:
        lines = f.readlines()
        if lines[0].startswith('---'):
            # Support jekyll style.
            lines.pop(0)

        for i, line in enumerate(lines):
            line_lower = line.lower()
            # Post title
            if line.startswith('#'):
                post.title = xhtml_escape(line[1:].strip())
            elif 'tags' in line_lower:
                tags = line.split(':')[-1].strip().strip('[]')
                # provide compatibility with jekyll's liquid style tags

                for tag in tags.split(','):
                    post.tags.append(xhtml_escape(tag.strip().lower()))

            elif 'comment' in line_lower:
                status = line_lower.split(':')[-1].strip()
                if status == 'disabled':
                    post.allow_comment = False

            # Post properties
            elif ':' in line_lower:
                line = line.strip().lstrip('-').strip()
                name, value = line.split(':', 1)
                post[name.strip()] = value.strip()

            elif line.startswith('---'):
                content = '\n'.join(lines[i + 1:])
                # Provide compatibility for liquid style code highlight
                content = highlight_liquid.sub(_highlightcode, content)

                post.source = content

                if 'summary' not in post:
                    post.summary = get_summary(post)
                if 'description' not in post:
                    post.description = get_description(post)

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
            p1 = os.stat(os.path.join(config.config.source, p1)).st_ctime
            p2 = os.stat(os.path.join(config.config.source, p2)).st_ctime
        return cmp(p1, p2)

    # Post file name must match style 2012-12-24-title.md
    pattern = re.compile('^\d{4}\-\d{2}\-\d{2}\-.+\.md$', re.I)
    files = [x for x in os.listdir(config.config.source) if pattern.match(x)]
    files.sort(reverse=True, cmp=_cmp_post)
    posts = []
    for file_name in files:
        post = load_post(file_name)
        if post:
            posts.append(post)
    g.posts = posts

    for post in posts:
        for tag in post.tags:
            Tag(tag).append(post)

        year = post.date[:4]
        Archive(year).append(post)

    g.tags = Tag.sort()
    g.archives = Archive.sort()
