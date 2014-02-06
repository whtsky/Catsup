# -*- coding:utf-8 -*-

import codecs

from catsup.logger import logger
from catsup.utils import to_unicode


def open_file(path):
    try:
        return codecs.open(path, "r", encoding="utf-8")
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
