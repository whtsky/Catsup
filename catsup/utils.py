import subprocess

from catsup.options import config, g


class Pagination(object):

    def __init__(self, page):
        self.total_items = g.posts
        self.page = page
        self.per_page = config.config.per_page

    def iter_pages(self, edge=4):
        if self.page <= edge:
            return range(1, min(self.pages, 2 * edge + 1) + 1)
        if self.page + edge > self.pages:
            return range(max(self.pages - 2 * edge, 1), self.pages + 1)
        return range(self.page - edge, min(self.pages, self.page + edge) + 1)

    @property
    def pages(self):
        return int((self.total - 1) / self.per_page) + 1

    @property
    def has_prev(self):
        return self.page > 1

    @property
    def prev_permalink(self):
        if (not g.theme.has_index) and self.prev_num == 1:
            return '/'
        return "/page/%s.html" % self.prev_num

    @property
    def prev_num(self):
        return self.page - 1

    @property
    def has_next(self):
        return self.page < self.pages

    @property
    def next_permalink(self):
        return "/page/%s.html" % self.next_num

    @property
    def next_num(self):
        return self.page + 1

    @property
    def total(self):
        return len(self.total_items)

    @property
    def items(self):
        start = (self.page - 1) * self.per_page
        end = self.page * self.per_page
        return self.total_items[start:end]


def call(cmd, silence=False, **kwargs):
    if isinstance(cmd, str):
        cmd = cmd.split()
    if 'cwd' not in kwargs:
        kwargs['cwd'] = g.cwdpath
    if silence and 'stdout' not in kwargs:
        kwargs["stdout"] = subprocess.PIPE
    return subprocess.call(cmd, **kwargs)


def check_git():
    """
    Check if the environment has git installed
    :return: Bool. True for installed and False for not.
    """
    return call('git --help', silence=True) == 0


def check_rsync():
    """
    Check if the environment has rsynv installed
    :return: Bool. True for installed and False for not.
    """
    return call('rsync --help', silence=True) == 0
