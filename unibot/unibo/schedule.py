import logging

from unibot.unibo.schedule_model import Schedule
from unibot.unibo.schedule_parsers import JsonParser, HtmlParser

from unibot.cache import cache_for
from unibot.urlfetch import fetch
from unibot.unibo.courses import get_courses


PARSERS = {'json': JsonParser, 'html': HtmlParser}


@cache_for(minutes=60)
def get_schedule(course_id, year, curricula=''):
    course = get_courses().get(course_id)
    src_url = course.get_url_schedule(year, curricula)
    src_data = fetch(src_url)
    logging.info(f"Parsing '{src_url}' using parser '{course.parser}'")
    events = get_parser(course.parser).parse(src_data)
    events = _remove_duplicates(events)
    return Schedule(events)


def get_parser(parser_type):
    return PARSERS[parser_type]()


def _remove_duplicates(events):
    seen = set()
    return [e for e in events if not (e in seen or seen.add(e))]
