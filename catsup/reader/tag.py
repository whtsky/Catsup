class Tag(object):

    instances = {}
    instance_posts = {}

    def __new__(cls, name):
        if name.lower() in Tag.instances:
            return Tag.instances[name.lower()]
        tag = super(Tag, cls).__new__(cls, name)
        Tag.instances[name.lower()] = tag
        return tag

    def __init__(self, name):
        self.name = name

    def append(self, post):
        self.posts.append(post)

    @property
    def count(self):
        return len(self.posts)

    @property
    def posts(self):
        if self.name in Tag.instance_posts:
            return Tag.instance_posts[self.name]
        posts = []
        Tag.instance_posts[self.name] = posts
        return posts

    @staticmethod
    def sort():
        tags = sorted(Tag.instances.values(),
                      key=lambda x: x.count, reverse=True)
        Tag.tags = {}
        return tags

    def __iter__(self):
        for post in self.posts:
            yield post

