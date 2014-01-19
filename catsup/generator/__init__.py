import time
import os
import catsup.parser

from catsup.logger import logger
from catsup.generator.renderer import Renderer
from catsup.reader import get_reader
from catsup.options import g
from catsup.utils import smart_copy
from catsup.models import *


class Generator(object):
    def __init__(self, config_path, local=False, base_url=None):
        self.config_path = config_path
        self.local = local

        self.base_url = base_url
        g.generator = self

        self.posts = []
        self.pages = []
        self.non_post_files = []
        self.archives = []
        self.tags = []
        self.caches = []
        self.config = {}
        self.renderer = None
        self.reset()

    def reset(self):
        self.posts = []
        self.pages = []
        self.non_post_files = []
        self.archives = g.archives = Archives()
        self.tags = g.tags = Tags()
        self.load_config()
        self.load_posts()
        self.load_renderer()
        self.caches = {
            "static_url": {},
            "url_for": {}
        }

    def load_config(self):
        self.config = g.config = catsup.parser.config(
            self.config_path,
            local=self.local,
            base_url=self.base_url
        )

    def load_posts(self):
        for f in os.listdir(g.source):
            if f.startswith("."):  # hidden file
                continue
            filename, ext = os.path.splitext(f)
            ext = ext.lower()[1:]
            reader = get_reader(ext)
            if reader is not None:
                logger.info('Loading file %s' % filename)
                path = os.path.join(g.source, f)
                post = reader(path)
                if post.type == "page":
                    self.pages.append(post)
                else:
                    self.posts.append(post)
            else:
                self.non_post_files.append(f)
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
            post.add_archive_and_tags()
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
        static_path = self.config.config.static_output

        smart_copy(
            os.path.join(g.theme.path, 'static'),
            static_path
        )
        smart_copy(
            self.config.config.static_source,
            static_path
        )
        for f in self.non_post_files:
            smart_copy(
                os.path.join(g.source, f),
                os.path.join(self.config.config.output, f)
            )

    def generate(self):
        started_loading = time.time()
        self.reset()
        finish_loading = time.time()
        logger.info(
            "Loaded config and %s posts in %.3fs" %
            (len(self.posts), finish_loading - started_loading)
        )
        if self.posts:
            self.generate_posts()
            self.generate_tags()
            self.generate_archives()
            self.generate_feed()
            self.generate_pages()
        else:
            logger.warning("Can't find any post.")
        self.generate_other_pages()
        self.copy_static_files()
        self.renderer.render_sitemap()
        finish_generating = time.time()
        logger.info(
            "Generated %s posts in %.3fs" %
            (len(self.posts), finish_generating - finish_loading)
        )
        logger.info(
            "Generating finished in %.3fs" %
            (finish_generating - started_loading)
        )
