import re
import os
import time
import shutil
from datetime import datetime
import catsup.parser

from houdini import escape_html
from catsup.logger import logger
from catsup.renderer import Renderer
from catsup.utils import to_unicode, smart_copy
from .models import *


class Generator(object):
    def __init__(self, config_path):
        self.config_path = config_path

    def reset(self):
        self.load_config()
        self.load_posts()
        self.load_tags_and_archives()
        self.load_renderer()

    def load_config(self):
        self.config = catsup.parser.config(self.config_path)

    def load_post(self, filename):
        path = os.path.join(g.source, filename)
        logger.info('Loading file %s' % filename)
        try:
            f = open(path, 'r')
        except IOError:
            logger.error("Can't open file %s" % path)
            return

        post = Post(filename=filename)

        lines = f.readlines()
        f.close()

        for i, line in enumerate(lines):
            line_lower = line.lower()
            if line.startswith('#'):  # title
                post.title = escape_html(line[1:].strip())

            elif ':' in line_lower:  # property
                name, value = line.split(':', 1)
                post[name.strip()] = value.strip()

            elif line.startswith('---'):
                content = '\n'.join(lines[i + 1:])
                post.md = to_unicode(content)
                post.render_content()

                if "tags" in post:
                    tag_names = post["tags"].split(",")
                    post.tags = []
                    for tag in tag_names:
                        tag = tag.strip()
                        tag = self.tags.setdefault(
                            tag.lower(),
                            Tag(tag)
                        )
                        post.tags.append(tag)
                        tag.add_post(post)
                if "time" in post:
                    post.datetime = datetime.strptime(
                        post.pop('time'), "%Y-%m-%d %H:%M")
                elif re.match('^\d{4}\-\d{2}\-\d{2}\-.+\.md', filename):
                    post.datetime = datetime.strptime(
                        filename[:10], "%Y-%m-%d")
                else:
                    ctime = os.stat(path).st_ctime
                    post.datetime = datetime.fromtimestamp(ctime)
                year = post.datetime.strftime("%Y")
                archive = self.archives.setdefault(year, Archive(year))
                archive.add_post(post)
                post.archive = archive
                post.date = post.datetime.strftime("%Y-%m-%d")
                post.year, post.month, post.day = post.date.split('-')
                return post
        logger.warning("Invalid post %s. Ignore." % filename)

    def load_posts(self):
        self.posts = []
        self.tags = {}
        self.archives = {}

        self.static_files = []

        for filename in os.listdir(g.source):
            if filename.startswith("."):  # hidden file
                continue
            if filename.endswith(".md") or filename.endswith(".markdown"):
                self.posts.append(self.load_post(filename))
            else:
                self.static_files.append(filename)
        self.posts.sort(
            key=lambda x: x.datetime,
            reverse=True
        )

    def load_tags_and_archives(self):
        self.tags = self.tags.values()
        self.tags.sort(
            key=lambda x: x.count,
            reverse=True
        )
        self.archives = self.archives.values()
        self.archives.sort(
            key=lambda x: x.year,
            reverse=True
        )

    def load_renderer(self):
        templates_path = [
            g.public_templates_path,
            os.path.join(g.theme.path, 'templates')
        ]
        self.renderer = Renderer(
            templates_path=templates_path,
            generator=self
        )

    def generate_feed(self):
        feed = Feed(self.posts)
        feed.render(self.renderer)

    def generate_pages(self):
        page = Page(self.posts)
        page.render_all(self.renderer)

    def generate_posts(self):
        for post in self.posts:
            post.render(self.renderer)

    def generate_tags(self):
        for tag in self.tags:
            tag.render(self.renderer)
        Tags(self.tags).render(self.renderer)

    def generate_archives(self):
        for archive in self.archives:
            archive.render(self.renderer)
        Archives(self.archives).render(self.renderer)

    def generate_other_pages(self):
        pass

    def copy_static_files(self):
        static_path = os.path.join(
            self.config.config.output,
            "static"
        )

        smart_copy(
            os.path.join(g.theme.path, 'static'),
            static_path
        )
        for f in self.static_files:
            source = os.path.join(
                self.config.config.source,
                f
            )
            target = os.path.join(
                self.config.config.output,
                f
            )
            smart_copy(source, target)

    def generate(self):
        self.reset()
        t = time.time()
        self.generate_feed()
        self.generate_pages()
        self.generate_posts()
        self.generate_tags()
        self.generate_archives()
        self.copy_static_files()
        logger.info("Generating finished in %.3fs" % (time.time() - t))
