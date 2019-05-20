import logging
import string
import re
import json
import sys

from unibot.urlfetch import fetch
from unibot.cache import cache_for


QUERY_ALLOWED_CHARS = string.ascii_letters + string.digits + 'àèéìòù '
QUERY_MIN_LENGTH = 4
SCHEDULE_SUBDIR_URL = {'it': 'orario-lezioni', 'en': 'timetable'}
EXAMS_SUBDIR_URL = {'it': 'appelli', 'en': 'exam-dates'}
AVAILABLE_CURRICULA_URL = '@@available_curricula?anno={}&curricula='
SCHEDULE_URL = {'json': '@@orario_reale_json?anno={}&curricula={}',
                'html': '?anno={}&curricula={}'}


class QueryTooShortError(Exception):
    def __init__(self, query):
        super().__init__(f"Search query '{query}' is too short")


class CourseNotFoundError(Exception):
    def __init__(self, course_id):
        super().__init__(f"Course '{course_id}' not found")


class NotSupportedError(Exception):
    def __init__(self, course_id, reason):
        super().__init__(f"Course '{course_id}' is not supported")
        self.reason = reason


class Course:
    def __init__(self, course_id, title, lang, campus, url, parser='json', url_lastminute=None, supported=True, not_supported_reason=''):
        self.course_id = course_id
        self.title = title
        self.lang = lang
        self.campus = campus
        self.url = url
        self.parser = parser
        self.url_lastminute = url_lastminute
        self.supported = supported
        self.not_supported_reason = not_supported_reason

    @property
    def search_name(self):
        return f"{self.title} - {self.course_id} - {self.campus}"

    def is_supported(self):
        return self.supported

    def has_lastminute(self):
        return bool(self.url_lastminute)

    def get_url_curricula(self, year):
        if not self.supported:
            raise NotSupportedError(self.course_id, self.not_supported_reason)
        curricula_part = AVAILABLE_CURRICULA_URL.format(year)
        return f"{self.url}/{SCHEDULE_SUBDIR_URL[self.lang]}/{curricula_part}"

    def get_url_schedule(self, year, curricula=''):
        if not self.supported:
            raise NotSupportedError(self.course_id, self.not_supported_reason)
        schedule_part = SCHEDULE_URL[self.parser].format(year, curricula)
        return f"{self.url}/{SCHEDULE_SUBDIR_URL[self.lang]}/{schedule_part}"

    def get_url_exams(self):
        return f"{self.url}/{EXAMS_SUBDIR_URL[self.lang]}"


class CourseRepo:
    def __init__(self, courses):
        self.courses = courses

    def get(self, course_id):
        match = next((c for c in self.courses if c.course_id == course_id), None)
        if not match:
            raise CourseNotFoundError(course_id)
        return match

    def search(self, query):
        query = ''.join(c if c not in string.punctuation else ' ' for c in query)
        query = ''.join(c for c in query if c in QUERY_ALLOWED_CHARS)
        query = ' '.join(query.split())
        if len(query) < QUERY_MIN_LENGTH:
            raise QueryTooShortError(query)
        query = query.replace(' ', '.*')
        regx = re.compile(query, flags=re.IGNORECASE)
        return [c for c in self.courses if regx.search(c.search_name)]


@cache_for(minutes=30)
def get_courses():
    try:
        with open('assets/courses.json', 'r') as fp:
            courses = [course_factory(c) for c in json.load(fp)]
            return CourseRepo(courses)
    except Exception as e:
        logging.exception(e)
        sys.exit(1)


@cache_for(minutes=60)
def get_curricula(course, year):
    return fetch(course.get_url_curricula(year)).json()


def course_factory(course):
    out = Course(course['id'], course['title'], course['lang'],
                 course['campus'], course['url'])
    if 'supported' in course:
        out.supported = course['supported']
        out.not_supported_reason = course['not_supported_reason']
    if 'url_lastminute' in course:
        out.url_lastminute = course['url_lastminute']
    if 'parser' in course:
        out.parser = course['parser']
    return out
