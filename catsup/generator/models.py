import os
import re

from datetime import datetime
from houdini import escape_html
from tornado.util import ObjectDict

from catsup.logger import logger
from catsup.options import g
from catsup.parser import markdown
from catsup.utils import to_unicode
from .utils import Pagination


class CatsupPage(object):
    @property
    def class_name(self):
        return self.__class__.__name__.lower()

    def get_permalink_args(self):
        return {}

    @property
    def permalink(self):
        kwargs = self.__dict__.copy()
        kwargs.update(self.get_permalink_args())
        return g.permalink[self.class_name].format(**kwargs).replace(" ", "-")

    def render(self, renderer, **kwargs):
        if hasattr(self, "template_name"):
            template_name = self.template_name
        else:
            template_name = self.class_name + ".html"
        kwargs[self.class_name] = self
        kwargs.update(self.__dict__)
        renderer.render_to(template_name, self.permalink, **kwargs)


class Tag(CatsupPage):
    def __init__(self, name):
        self.name = name
        self.posts = []

    def add_post(self, post):
        self.posts.append(post)

    @property
    def count(self):
        return len(self.posts)

    def __iter__(self):
        for post in self.posts:
            yield post


class Tags(CatsupPage):
    def __init__(self, tags=None):
        if tags is None:
            tags = {}
        self.tags_dict = tags

    def get(self, name):
        return self.tags_dict.setdefault(
            name,
            Tag(name)
        )

    def render(self, renderer, **kwargs):
        for tag in self.tags:
            tag.render(renderer)
        super(Tags, self).render(renderer, **kwargs)

    @property
    def tags(self):
        if not hasattr(self, "_tags"):
            self._tags = list(self.tags_dict.values())
            self._tags.sort(
                key=lambda x: x.count,
                reverse=True
            )
        return self._tags

    def __iter__(self):
        for tag in self.tags:
            yield tag


class Archive(CatsupPage):
    def __init__(self, year):
        self.year = int(year)
        self.posts = []

    def add_post(self, post):
        self.posts.append(post)

    @property
    def count(self):
        return len(self.posts)

    def __iter__(self):
        for post in self.posts:
            yield post


class Archives(CatsupPage):
    def __init__(self, archives=None):
        if archives is None:
            archives = {}
        self.archives_dict = archives

    def get(self, year):
        return self.archives_dict.setdefault(
            year,
            Archive(year)
        )

    def render(self, renderer, **kwargs):
        for tag in self.archives:
            tag.render(renderer)
        super(Archives, self).render(renderer, **kwargs)

    @property
    def archives(self):
        if not hasattr(self, "_archives"):
            self._archives = list(self.archives_dict.values())
            self._archives.sort(
                key=lambda x: x.year,
                reverse=True
            )
        return self._archives

    def __iter__(self):
        for archive in self.archives:
            yield archive


class Post(CatsupPage):
    DATE_RE = re.compile('\d{4}\-\d{2}\-\d{2}')

    def __init__(self, filename, ext):
        self.meta = ObjectDict()
        path = os.path.join(g.source, "%s%s" % (filename, ext))
        self.filename = filename
        self.parse(path)

    def get_permalink_args(self):
        return self.meta

    def parse(self, path):
        try:
            with open(path, "r") as f:
                lines = f.readlines()
        except IOError:
            logger.error("Can't open file %s" % path)
            exit(1)

        def invailed_post():
            logger.error("%s is not a vailed catsup post" % self.filename)
            exit(1)

        title = lines.pop(0)
        if title.startswith("#"):
            self.title = escape_html(title[1:].strip())
        else:
            invailed_post()

        for i, line in enumerate(lines):
            if ':' in line:  # property
                name, value = line.split(':', 1)
                name = name.strip().lstrip('-').strip().lower()
                self.meta[name] = value.strip()

            elif line.strip().startswith('---'):
                self.md = to_unicode('\n'.join(lines[i + 1:]))
                self.content = markdown(self.md)

                if "time" in self.meta:
                    self.datetime = datetime.strptime(
                        self.meta.pop('time'), "%Y-%m-%d %H:%M")
                elif self.DATE_RE.match(self.filename[:10]):
                    self.datetime = datetime.strptime(
                        self.filename[:10], "%Y-%m-%d"
                    )
                else:
                    ctime = os.stat(path).st_ctime
                    self.datetime = datetime.fromtimestamp(ctime)
                self.date = self.datetime.strftime("%Y-%m-%d")

                self.type = self.meta.pop("type", "post")
                self.tags = []
                if self.type != "page":
                    year = self.datetime.strftime("%Y")
                    g.archives.get(year).add_post(self)

                    for tag in self.meta.pop("tags", "").split(","):
                        tag = tag.strip()
                        tag = g.tags.get(tag)
                        tag.add_post(self)
                        self.tags.append(tag)
                return

        invailed_post()

    @property
    def description(self):
        return self.meta.get(
            "description",
            self.md[:200]
        )

    @property
    def allow_comment(self):
        if self.meta.get("comment", None) == "disabled":
            return False
        return g.config.comment.allow


class Page(CatsupPage):
    def __init__(self, posts):
        self.posts = posts
        self.per_page = g.theme.post_per_page

    @staticmethod
    def get_permalink(page):
        if page == 1:
            return "/"
        return g.permalink["page"].format(page=page)

    @property
    def permalink(self):
        return Page.get_permalink(self.page)

    def render_all(self, renderer):
        count = int((len(self.posts) - 1) / self.per_page) + 1
        for i in range(count):
            page = i + 1
            if page == 1:
                self._permalink = "/"
            self.page = page
            pagination = Pagination(
                page=page,
                posts=self.posts,
                per_page=self.per_page,
                get_permalink=self.get_permalink
            )
            self.render(renderer=renderer, pagination=pagination)


class Feed(CatsupPage):
    def __init__(self, posts):
        self.posts = posts
        self.template_name = "feed.xml"


class NotFound(CatsupPage):
    def __init__(self):
        self.template_name = "404.html"

    @property
    def permalink(self):
        return "/404.html"
