# -*- coding: utf-8 -*-

import os
import re

from datetime import datetime
from houdini import escape_html

from catsup.logger import logger
from catsup.options import g
from catsup.parser import markdown
from catsup.utils import to_unicode, ObjectDict
from .utils import cached_func, Pagination


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
        self.path = os.path.join(g.source, "%s%s" % (filename, ext))
        self.filename = filename
        self.parse()
        self.add_archive_and_tags()

    def add_archive_and_tags(self):
        if self.type != "page":
            year = self.datetime.strftime("%Y")
            g.archives.get(year).add_post(self)

            for tag in self.meta.pop("tags", "").split(","):
                tag = tag.strip()
                tag = g.tags.get(tag)
                tag.add_post(self)
                self.tags.append(tag)

    def get_permalink_args(self):
        return self.meta

    @property
    @cached_func
    def datetime(self):
        if "time" in self.meta:
            return datetime.strptime(
                self.meta.pop('time'), "%Y-%m-%d %H:%M")
        elif self.DATE_RE.match(self.filename[:10]):
            return datetime.strptime(
                self.filename[:10], "%Y-%m-%d"
            )
        else:
            st_ctime = os.stat(self.path).st_ctime
            return datetime.fromtimestamp(st_ctime)

    @property
    @cached_func
    def date(self):
        return self.datetime.strftime("%Y-%m-%d")

    @property
    @cached_func
    def description(self):
        description = self.meta.get(
            "description",
            self.md
        )
        if "***" in description:
            description = description.split("***")[0]
            description = description.replace("\n", "  ")
        else:
            description = description.split("\n")[0]
        if len(description) > 150:
            description = description[:150]
        description = description.strip()
        return escape_html(description)

    @property
    @cached_func
    def allow_comment(self):
        if self.meta.get("comment", None) == "disabled":
            return False
        else:
            return g.config.comment.allow

    @property
    @cached_func
    def type(self):
        return self.meta.get("type", "post")

    def parse(self):
        try:
            with open(self.path, "r") as f:
                lines = f.readlines()
        except IOError:
            logger.error("Can't open file %s" % self.path)
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

                self.tags = []
                return

        invailed_post()


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
