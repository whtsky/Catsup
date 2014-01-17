import requests

from catsup.logger import logger


def search_github(name):
    repo_name = "catsup-theme-{name}".format(name=name)
    response = requests.get("https://api.github.com/search/repositories?q={repo_name}".format(repo_name=repo_name), headers={
        "User-Agent": "Catsup Theme Finder"
    })
    try:
        response.raise_for_status()
    except requests.HTTPError:
        logger.warning("Error when connecting to GitHub.")
        return None
    json = response.json()
    if json["total_count"] == 0:
        return None
    for item in json["items"]:
        if item["name"] == repo_name:
            return {
                "name": item["name"],
                "clone_url": item["clone_url"]
            }
