from pytest import raises


def test_build(output_exist):
    from catsup.cli import clean, build

    clean(settings="config.json")
    build(settings="config.json")
    assert output_exist("feed.xml")
    assert output_exist("index.html")
    assert output_exist("page.html")
    assert output_exist("sitemap.txt")
    assert output_exist("should-exist")
    assert not output_exist(".should-not-exist")


def test_init():
    import os
    from catsup.cli import init

    os.remove("config.json")
    init("./")


def test_reinit():
    from catsup.cli import init

    with raises(SystemExit):
        init("./")


def test_generate_without_post(output_exist):
    from catsup.cli import clean, build

    clean(settings="config2.json")
    build(settings="config2.json")
    assert not output_exist("page.html")
