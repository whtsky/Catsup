from houdini import escape_html

from catsup.models import Post
from catsup.utils import ObjectDict
from catsup.reader.utils import open_file, not_valid


def parse_meta(lines, path=None):
    lines = [l.strip() for l in lines if l]
    if lines[0].startswith("#"):
        return parse_catsup_meta(lines, path)
    elif lines[0].startswith("---"):
        return parse_liquid_meta(lines, path)
    else:
        not_valid(path)
    return False


def parse_liquid_meta(lines, path=None):
    meta = ObjectDict()
    return meta


def parse_catsup_meta(lines, path=None):
    meta = ObjectDict()
    meta.title = escape_html(lines.pop(0)[1:].strip())
    for line in lines:
        if not line:
            continue
        if ":" not in line:
            not_valid(path)
        name, value = line.split(':', 1)
        name = name.strip().lstrip('-').strip().lower()
        meta[name] = value.strip()
    return meta


def text_reader(path):
    post_file = open_file(path)

    lines = []
    firstline = post_file.readline().strip()
    lines.append(firstline)
    for l in post_file:
        l = l.strip()
        if l.startswith("---"):
            break
        elif l:
            lines.append(l)
    else:
        not_valid(path)
    meta = parse_meta(lines, path)
    content = "".join(post_file)
    return meta, content


def txt_reader(path):
    meta, content = text_reader(path)
    content = escape_html(content).replace("\n", "<br />")
    return Post(
        path=path,
        meta=meta,
        content=content
    )
