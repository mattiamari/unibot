import logging
import string
import re
import json

from unibot.urlfetch import fetch

QUERY_ALLOWED_CHARS = string.ascii_letters + string.digits + 'àèéìòù '
QUERY_MIN_LENGTH = 4
SCHEDULE_SUBDIR_URL = {'it': 'orario-lezioni', 'en': 'timetable'}
AVAILABLE_CURRICULA_URL = '@@available_curricula?anno={}&curricula='
SCHEDULE_URL = '@@orario_reale_json?anno={}&curricula={}'

courses = None

class QueryTooShortError(Exception):
    def __init__(self, query):
        super().__init__("Search query '{}' is too short".format(query))

try:
    with open('assets/courses.json', 'r') as f:
        courses = json.load(f)
except Exception as e:
    logging.error("Can't load courses because '{}'".format(str(e)))

def get_url_curricula(course_id, year):
    course = get_course(course_id)
    if course is None:
        return None
    curricula_part = AVAILABLE_CURRICULA_URL.format(year)
    return '{}/{}/{}'.format(course['url'], SCHEDULE_SUBDIR_URL[course['lang']], curricula_part)

def get_url_schedule(course_id, year, curricula=''):
    course = get_course(course_id)
    if course is None:
        return None
    schedule_part = SCHEDULE_URL.format(year, curricula)
    return '{}/{}/{}'.format(course['url'], SCHEDULE_SUBDIR_URL[course['lang']], schedule_part)

def get_course(course_id):
    return next(x for x in courses if x['id'] == course_id)

def get_curricula(course_id, year):
    url = get_url_curricula(course_id, year)
    return fetch(url).json()

def search(query):
    query = ''.join(c if c not in string.punctuation else ' ' for c in query)
    query = ''.join(c for c in query if c in QUERY_ALLOWED_CHARS)
    query = ' '.join(query.split())
    if len(query) < QUERY_MIN_LENGTH:
        raise QueryTooShortError(query)
    query = query.replace(' ', '.*')
    regx = re.compile(query, flags=re.IGNORECASE)
    return [c for c in courses if regx.search(c['title'])]
