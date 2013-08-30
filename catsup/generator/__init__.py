import time
import os
import tempfile
import catsup.parser

from catsup.logger import logger
from catsup.generator.renderer import Renderer
from catsup.options import g
from catsup.utils import smart_copy
from .models import *


class Generator(object):
    def __init__(self, config_path, local=False, base_url=None):
        self.config_path = config_path
        self.local = local
        self.base_url = base_url

    def reset(self):
        self.archives = g.archives = Archives()
        self.tags = g.tags = Tags()
        self.load_config()
        self.load_posts()
        self.load_renderer()

    def load_config(self):
        self.config = g.config = catsup.parser.config(
            self.config_path,
            local=self.local,
            base_url=self.base_url
        )

    def load_post(self, filename, ext):
        logger.info('Loading file %s' % filename)

        post = Post(filename, ext)
        if post.type == "page":
            self.pages.append(post)
        else:
            self.posts.append(post)

    def load_posts(self):
        self.posts = []
        self.pages = []

        self.static_files = []

        for f in os.listdir(g.source):
            if f.startswith("."):  # hidden file
                continue
            filename, ext = os.path.splitext(f)
            if ext.lower() in ['.md', '.markdown']:
                self.load_post(filename, ext)
            else:
                self.static_files.append(f)
        self.posts.sort(
            key=lambda x: x.datetime,
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
        for page in self.pages:
            page.render(self.renderer)

    def generate_tags(self):
        self.tags.render(self.renderer)

    def generate_archives(self):
        self.archives.render(self.renderer)

    def generate_other_pages(self):
        NotFound().render(self.renderer)

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
        if self.local:
            g.output = self.config.config.output = tempfile.mkdtemp()
        if self.posts:
            self.generate_feed()
            self.generate_pages()
            self.generate_posts()
            self.generate_tags()
            self.generate_archives()
        else:
            logger.warning("Can't find any post.")
        self.generate_other_pages()
        self.copy_static_files()
        logger.info(
            "Generated %s posts in %.3fs" %
            (len(self.posts), time.time() - t)
        )