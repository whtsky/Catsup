from catsup.models import Post
from catsup.utils import to_unicode, ObjectDict
from catsup.reader.utils import split_content, parse_yaml_meta


def html_reader(path):
    meta, content = split_content(path)
    if not meta:
        meta = ObjectDict()
    else:
        meta = parse_yaml_meta(meta, path)
    return Post(
        path=path,
        meta=meta,
        content=to_unicode(content)
    )
