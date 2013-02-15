class Archive(object):

    instances = {}
    instance_posts = {}

    def __new__(cls, name):
        if name in Archive.instances:
            return Archive.instances[name]
        archive = super(Archive, cls).__new__(cls, name)
        Archive.instances[name] = archive
        return archive

    def __init__(self, name):
        self.name = name

    def append(self, post):
        self.posts.append(post)

    @property
    def count(self):
        return len(self.posts)

    @property
    def posts(self):
        if self.name in Archive.instance_posts:
            return Archive.instance_posts[self.name]
        posts = []
        Archive.instance_posts[self.name] = posts
        return posts

    @staticmethod
    def sort():
        archives = sorted(Archive.instances.values(), key=lambda x: x.name,
                          reverse=True)
        Archive.archives = {}
        return archives
