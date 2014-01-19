import yaml

from houdini import escape_html

from catsup.logger import logger
from catsup.utils import update_nested_dict, ObjectDict, to_unicode


def parse_meta(lines, path=None):
    lines = [l.strip() for l in lines if l]
    if lines[0].startswith("#"):
        return parse_catsup_meta(lines, path)
    elif lines[0].startswith("---"):
        return parse_yaml_meta(lines, path)
    else:
        not_valid(path)


def parse_yaml_meta(lines, path=None):
    title_line = lines.pop(0)
    if not title_line.startswith("---"):
        not_valid(path)
    meta = yaml.load("\n".join(lines))
    return update_nested_dict(ObjectDict(), meta)


def parse_catsup_meta(lines, path=None):
    meta = ObjectDict()
    title_line = lines.pop(0)
    if title_line[0] != "#":
        not_valid(path)
    meta.title = escape_html(title_line[1:].strip())
    for line in lines:
        if not line:
            continue
        if ":" not in line:
            not_valid(path)
        name, value = line.split(':', 1)
        name = name.strip().lstrip('-').strip().lower()
        meta[name] = value.strip()
    return meta


def open_file(path):
    try:
        return open(path, "r")
    except IOError:
        logger.error("Can't open file %s" % path)
        exit(1)


def not_valid(path):
    logger.error("%s is not a valid post." % path)
    exit(1)


def split_content(path):
    file = open_file(path)

    lines = [file.readline().strip()]
    no_meta = False

    for l in file:
        l = l.strip()
        if l.startswith("---"):
            break
        elif l:
            lines.append(l)
    else:
        no_meta = True
    if no_meta:
        return [], to_unicode("\n".join(lines))
    else:
        return lines, to_unicode("".join(file))
