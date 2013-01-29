#coding=utf-8
import os
import re
import logging

from tornado.util import ObjectDict
from tornado.escape import xhtml_escape

from catsup.options import config, g
from catsup.reader.markdown import md_escape, md_raw

highlight_liquid = re.compile('\{%\s?highlight ([\w\-\+]+)\s?%\}\n'
                     '*(.+?)'
                     '\n*\{%\s?endhighlight\s?%\}', re.I | re.S)
excerpt_re = re.compile('(<h[\d]+>.*?)<h[\d]+>')

class Post(ObjectDict):
    """Post object"""
    @property
    def excerpt(self):
        if not config.config.excerpt_index:
            self.have_more = False
            return self.content
        self.have_more = True
        if '<!--more-->' in self.source:
            excerpt = self.source.split('<!--more-->')[0]
            return self.render(excerpt)
        elif '<hr>' in self.content:
            return self.content.split('<hr>')[0]
        elif '<h' in self.content:
            excerpts = excerpt_re.findall(self.content)
            if excerpts:
                return excerpts[0]
        else:
            #TAT
            self.have_more = False
            return self.content

    @property
    def content(self):
        return self.render(self.source.replace('<!--more-->', ''))

    @property
    def description(self):
        if len(self.source) < 200:
            return self.source
        return '%s...' % self.source[:190]

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
                if status in ('no', 'disabled', 'close'):
                    post.allow_comment = False

            # Post properties
            elif ':' in line_lower:
                if '-' in line_lower:
                    # make '-' be optional in properties
                    line = '-'.join(line.split('-')[1:]).strip()
                name, value = line.split(':')[0], ':'.join(line.split(':')[1:])
                post[name.strip()] = value.strip()

            elif line.startswith('---'):
                if i == 0:
                    # provide compatibility with jekyll,
                    # ignore first line if it starts with `---`
                    continue

                content = '\n'.join(lines[i + 1:])
                # Provide compatibility for liquid style code highlight
                content = highlight_liquid.sub(_highlightcode, content)

                post.source = content

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
    g.tags = sorted(tags.values(), key=lambda x: x.post_count, reverse=True)
    g.archives = sorted(archives.values(), key=lambda x: x.name, reverse=True)
