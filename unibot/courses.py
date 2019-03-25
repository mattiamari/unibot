import string
import re
import json

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
    return next(x for x in COURSES if x['id'] == course_id)

def search(query):
    query = ''.join(c for c in query if c in QUERY_ALLOWED_CHARS)
    query = ' '.join(query.split())
    query = query.replace(' ', '.*')
    regx = re.compile(query, flags=re.IGNORECASE)
    return [c for c in COURSES if regx.search(c['title'])]

QUERY_ALLOWED_CHARS = string.ascii_letters + string.digits + 'àèéìòù '
SCHEDULE_SUBDIR_URL = {'it': 'orario-lezioni', 'en': 'timetable'}
AVAILABLE_CURRICULA_URL = '@@available_curricula?anno={}&curricula='
SCHEDULE_URL = '@@orario_reale_json?anno={}&curricula={}'

COURSES = None
with open('assets/courses.json', 'r') as f:
    COURSES = json.load(f)
