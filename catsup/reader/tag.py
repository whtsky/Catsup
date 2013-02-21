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
        self.posts = []

    def append(self, post):
        self.posts.append(post)

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

