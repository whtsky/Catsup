instances = {}


class Archive(object):
    def __new__(cls, name):
        if name in instances:
            return instances[name]
        archive = super(Archive, cls).__new__(cls)
        instances[name] = archive
        return archive

    def __init__(self, name):
        self.name = name
        if not hasattr(self, "posts"):
            self.posts = []

    def append(self, post):
        self.posts.append(post)

    @property
    def count(self):
        return len(self.posts)

    @staticmethod
    def sort():
        global instances
        archives = sorted(instances.values(), key=lambda x: x.name,
                          reverse=True)
        instances = {}
        return archives

    def __iter__(self):
        for post in self.posts:
            yield post
