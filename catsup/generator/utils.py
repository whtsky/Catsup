class Pagination(object):
    def __init__(self, page, posts, per_page, get_permalink):
        self.total_items = posts
        self.page = page
        self.per_page = per_page
        self.get_permalink = get_permalink

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
        return self.get_permalink(self.prev_num)

    @property
    def prev_num(self):
        return self.page - 1

    @property
    def has_next(self):
        return self.page < self.pages

    @property
    def next_permalink(self):
        return self.get_permalink(self.next_num)

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
