import logging
import sys

from invoke import Collection

from . import es


def setup_logging():
    logging.basicConfig(
        format='[%(asctime)s] %(name)s %(message)s',
        datefmt='%Y-%m-%dT%H:%M:%S',
        stream=sys.stdout,
        level=logging.INFO,
    )

setup_logging()
ns = Collection()
ns.add_collection(es)
