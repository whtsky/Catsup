from catsup.logger import logger


def open_file(path):
    try:
        return open(path, "r")
    except IOError:
        logger.error("Can't open file %s" % path)
        exit(1)


def not_valid(path):
    logger.error("%s is not a valid post." % path)
    exit(1)
