from catsup.themes.utils import search_github


def test_search_github():
    theme = search_github("clean")
    assert theme["name"] == "catsup-theme-clean"
    assert theme["clone_url"] == "https://github.com/whtsky/catsup-theme-clean.git"
