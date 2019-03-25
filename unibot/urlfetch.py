import logging
import os
import requests
from unibot.cache import cache_for

USER_AGENT = 'unibo_orari_bot/{}'.format(os.environ['VERSION'])

class FetchError(Exception):
    pass

@cache_for(minutes=60)
def fetch(url):
    try:
        logging.info("Getting from upstream: {}".format(url))
        res = requests.get(url, timeout=10, headers={'user-agent': USER_AGENT})
    except requests.Timeout:
        logging.warning("Cannot get '{}'. Request timed out".format(url))
        raise FetchError()

    if res.status_code != requests.codes.ok:
        logging.warning("Cannot get '{}'. Request returned {}".format(url, res.status_code))
        raise FetchError()
    return res
