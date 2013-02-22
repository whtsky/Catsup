from catsup.utils import config

instances = {}


class Tag(object):
    def __new__(cls, name):
        if name.lower() in instances:
            return instances[name.lower()]
        tag = super(Tag, cls).__new__(cls)
        instances[name.lower()] = tag
        return tag

    def __init__(self, name):
        self.name = name
        if not hasattr(self, "posts"):
            self.posts = []
        self.permalink = config.permalink.tag.format(name=name)

    def append(self, post):
        self.posts.append(post)
        post.tags.append(self)

    @property
    def count(self):
        return len(self.posts)

    @staticmethod
    def sort():
        global instances
        tags = sorted(instances.values(),
                      key=lambda x: x.count, reverse=True)
        instances = {}
        return tags

    def __iter__(self):
        for post in self.posts:
            yield post

    def __repr__(self):
        return self.name
