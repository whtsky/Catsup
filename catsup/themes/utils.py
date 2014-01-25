import urllib2
import ujson

from catsup.logger import logger


def search_github(name):
    repo_name = "catsup-theme-{name}".format(name=name)
    url = "https://api.github.com/search/repositories?q=" + repo_name
    request = urllib2.Request(url)
    request.add_header("User-Agent", "Catsup Theme Finder")
    try:
        response = urllib2.urlopen(request)
    except urllib2.HTTPError as e:
        logger.warning("Error when connecting to GitHub: {}".format(e.msg))
        return None
    content = response.read()
    json = ujson.loads(content)
    if json["total_count"] == 0:
        return None
    for item in json["items"]:
        if item["name"] == repo_name:
            return {
                "name": item["name"],
                "clone_url": item["clone_url"]
            }
