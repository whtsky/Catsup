def add_slash(url):
    if '//' in url:
        return url.rstrip('/') + '/'
    return '/%s/' % url.strip('/')
