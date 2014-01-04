from catsup.reader import get_reader, markdown_reader, txt_reader


def test_reader_choser():
    assert get_reader("md") == markdown_reader
    assert get_reader("markdown") == markdown_reader
    assert get_reader("txt") == txt_reader

