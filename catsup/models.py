# -*- coding: utf-8 -*-

import os
import re

from datetime import datetime

from catsup.options import g
from catsup.utils import html_to_raw_text
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

    def __init__(self, path, meta, content):
        self.path = path
        self.filename, _ = os.path.splitext(os.path.basename(path))
        self.meta = meta
        self.content = content
        self.tags = []
        self.date = self.datetime.strftime("%Y-%m-%d")

        filename, _ = os.path.splitext(os.path.basename(path))
        if self.DATE_RE.match(filename[:10]):
            self.meta.setdefault("date", filename[:10])
            self.filename = filename[11:]
        else:
            self.filename = filename

        if "date" in self.meta:
            self.date = self.meta.date
        else:
            self.date = self.datetime.strftime("%Y-%m-%d")

    def add_archive_and_tags(self):
        year = self.datetime.strftime("%Y")
        g.archives.get(year).add_post(self)

        for tag in self.meta.pop("tags", "").split(","):
            tag = tag.strip()
            tag = g.tags.get(tag)
            tag.add_post(self)
            self.tags.append(tag)

    @property
    def permalink(self):
        if "permalink" in self.meta:
            return self.meta.permalink
        return super(Post, self).permalink

    def get_permalink_args(self):
        args = self.meta.copy()
        args.update(
            title=self.title,
            datetime=self.datetime
        )
        return args

    @property
    def datetime(self):
        import os
        if "time" in self.meta:
            return datetime.strptime(
                self.meta.time, "%Y-%m-%d %H:%M"
            )
        elif "date" in self.meta:
            return datetime.strptime(
                self.meta.date, "%Y-%m-%d"
            )
        st_ctime = os.stat(self.path).st_ctime
        return datetime.fromtimestamp(st_ctime)

    @property
    def description(self):
        if "description" not in self.meta:
            description = self.meta.get(
                "description",
                self.content
            ).replace("\n", "")
            description = html_to_raw_text(description)
            if "<br" in description:
                description = description.split("<br")[0]
            elif "</p" in description:
                description = description.split("</p")[0]
            if len(description) > 150:
                description = description[:150]
            self.meta.description = description.strip()
        return self.meta.description

    @property
    def allow_comment(self):
        if self.meta.get("comment", None) == "disabled":
            return False
        else:
            return g.config.comment.allow

    @property
    def title(self):
        return self.meta.get("title", self.filename)

    @property
    def type(self):
        return self.meta.type


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
