from catsup.utils import cache


@cache
def xmldatetime(t):
    return t.strftime('%Y-%m-%dT%H:%M:%SZ')
