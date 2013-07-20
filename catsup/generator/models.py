import os

from tornado.util import ObjectDict
from catsup.options import g
from catsup.parser import markdown
from catsup.utils import cache
from .utils import Pagination


class CatsupPage(ObjectDict):
    @property
    def class_name(self):
        return self.__class__.__name__.lower()

    @property
    @cache
    def permalink(self):
        return g.permalink[self.class_name].format(**self).replace(" ", "-")

    def render(self, renderer, **kwargs):
        template_name = self.get("template_name",
                                 self.__class__.__name__.lower() + ".html")
        output_name = os.path.join(
            "output",
            self.permalink
        )
        if output_name.endswith("/"):
            output_name += 'index.html'
        output_path = os.path.join(g.output, output_name.lstrip("/"))
        kwargs.update(**self)
        renderer.render_to(template_name, output_path, **kwargs)


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
    def __init__(self, tags):
        self.tags = tags

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
    def __init__(self, archives):
        self.archives = archives


class Post(CatsupPage):
    def render_content(self):
        self.content = markdown(self.md)


class Page(CatsupPage):
    def __init__(self, posts):
        self.posts = posts
        self.per_page = 5

    @staticmethod
    @cache
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
