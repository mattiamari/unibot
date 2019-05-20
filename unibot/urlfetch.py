import logging
import os
import requests

USER_AGENT = f"UniBot/{os.environ['BOT_VERSION']}"


class FetchError(Exception):
    pass


def fetch(url):
    try:
        logging.info("Getting from upstream: %s", url)
        res = requests.get(url, timeout=10, headers={'user-agent': USER_AGENT})
    except requests.Timeout:
        logging.warning("Cannot get '%s'. Request timed out", url)
        raise FetchError()

    if res.status_code != requests.codes.ok:
        logging.warning("Cannot get '%s'. Request returned %s", url, res.status_code)
        raise FetchError()
    return res
