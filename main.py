import logging
import sys
from typing import List

from __init__ import __version__

logger = logging.getLogger(__name__)


def main():
    configure_logging()
    logger.info(f"Starting program version: {__version__}")
    do_something(["test", "test2"])


def configure_logging():
    FORMAT = "%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s"
    logging.basicConfig(
        format=FORMAT,
        datefmt="%Y-%m-%d:%H:%M:%S",
        stream=sys.stdout,
        level=logging.INFO,
    )
    logger.info("hello")


def do_something(things: List[str]):
    """do_something documentation"""
    for thing in things:
        logger.info(f"hello world {thing}")


if __name__ == "__main__":
    main()
