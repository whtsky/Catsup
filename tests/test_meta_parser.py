from nose.tools import raises


def test_catsup_meta_parser():
    from catsup.reader.utils import parse_catsup_meta

    meta_txt = """
    # Hello, world!

    - tags: hello, world
    """
    lines = [l.strip() for l in meta_txt.splitlines() if l]
    meta = parse_catsup_meta(lines)
    assert meta.title == "Hello, world!"
    assert meta.tags == "hello, world"


@raises(SystemExit)
def test_catsup_meta_parser_error_1():
    from catsup.reader.utils import parse_catsup_meta
    parse_catsup_meta(["fsdaf-,-,-,-", "fdsa- 0,"])


@raises(SystemExit)
def test_catsup_meta_parser_error_2():
    from catsup.reader.utils import parse_catsup_meta
    parse_catsup_meta(["#fsdaf-,-,-,-", "fdsa- 0,"])


def test_meta_parser():
    from catsup.reader.utils import parse_meta

    meta_txt = """
    # Hello, world!

    - tags: hello, world
    """

    lines = [l.strip() for l in meta_txt.splitlines() if l]
    meta = parse_meta(lines)
    assert meta.title == "Hello, world!"
    assert meta.tags == "hello, world"


@raises(SystemExit)
def test_parse_unknown_meta():
    from catsup.reader.utils import parse_meta
    parse_meta(["fdsjaklfdsjaklfdsjaklfjdsklfjsa"])