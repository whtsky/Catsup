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


class Post(ObjectDict):
    """Post object"""

    def __init__(self, **kwargs):
        super(Post, self).__init__(**kwargs)
        year, month, day = self.date.split('-')

        for x in ['year', 'month', 'day']:
            if x not in self:
                self[x] = locals().get(x)

    @property
    def content(self):
        return self.render(self.source.replace('<!--more-->', ''))

    def render(self, content):
        if self.get('escape', config.config.escape_md):
            md = md_escape
        else:
            md = md_raw
        return md.render(content)


def load_post(filename):
    '''Load a post.return a dict.
    '''
    def _highlightcode(m):
        '''Function for replace liquid style code highlight to github style
        '''
        return "```%s\n%s\n```" % (m.group(1), m.group(2))

    path = os.path.join(config.config.source, filename)
    logging.info('Loading file %s' % path)
    date = filename[:10]
    filename = filename[:-3].lstrip(date).lower()
    post = Post(
        filename=filename,
        tags=[],
        date=date,
        updated=os.stat(path).st_ctime,
    )
    post.permalink = config.config.permalink.format(**post)
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
                tags = line.split(':', 1)[1].strip()

                for tag in tags.split(','):
                    post.tags.append(xhtml_escape(tag.strip().lower()))

            elif 'comment' in line_lower:
                status = line_lower.split(':')[-1].strip()
                if status == 'disabled':
                    post.allow_comment = False

            # Post properties
            elif ':' in line_lower:
                name, value = line.split(':', 1)
                post[name.strip()] = value.strip()

            elif line.startswith('---'):
                content = '\n'.join(lines[i + 1:])

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
    for filename in files:
        post = load_post(filename)
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
