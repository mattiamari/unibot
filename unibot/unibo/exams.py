import logging
from datetime import datetime
from bs4 import BeautifulSoup

from unibot.urlfetch import fetch
from unibot.cache import cache_for
from unibot.unibo.courses import get_courses

from pprint import pformat

EXAM_DATE_HEADING_DICT = {
    'data e ora:': 'date',
    'lista iscrizioni:': 'signup_dates',
    'tipo prova:': 'exam_type',
    'luogo:': 'location',
    'note:': 'notes'
}

MONTH_NAMES_DICT = {
    'gennaio': 1,
    'febbraio': 2,
    'marzo': 3,
    'aprile': 4,
    'maggio': 5,
    'giugno': 6,
    'luglio': 7,
    'agosto': 8,
    'settembre': 9,
    'ottobre': 10,
    'novembre': 11,
    'dicembre': 12
}

DATE_FORMAT = ''

class Exam:
    def __init__(self, subject_id, subject, course_id, prof, date, signup_dates, exam_type, location, notes=''):
        self.subject_id = subject_id
        self.subject = subject
        self.course_id = course_id
        self.prof = prof
        self.date = date
        self.signup_dates = signup_dates
        self.exam_type = exam_type
        self.location = location
        self.notes = notes

    def __str__(self):
        return self.tostring()

    def heading(self):
        return "{} ({}) - {}".format(self.subject, self.subject_id, self.prof)

    def tostring(self, with_heading=True):
        out = ""
        if with_heading:
            out += self.heading()
        out += "{}\nIscrizione: {}\nTipo prova: {}\nLuogo: {}\nNote: {}" \
               .format(self.date, self.signup_dates, self.exam_type, self.location, self.notes)
        return out


class ExamList:
    def __init__(self, items):
        self.items = items

    def __str__(self):
        return self.tostring()

    def tostring(self):
        last_heading = ''
        out = ''
        for e in self.items:
            heading = e.heading()
            if last_heading != heading:
                out += '<b>' + heading + '</b>' + '\n'
                last_heading = heading
            out += e.tostring(with_heading=False) + '\n\n'
        return out

    def subject_heading(self, subject_id):
        return next(e.heading() for e in self.items if e.subject_id == subject_id)

    def has_exams(self):
        return len(self.items) > 0


class Exams:
    def __init__(self, exams):
        self.exams = exams
        self.exams.sort(key=lambda e: e.date)

    def get_all(self):
        return ExamList(self.exams)

    def subjects(self):
        return set([e.subject_id for e in self.exams])

    def of_subject(self, subject_id):
        return ExamList([e for e in self.exams if e.subject_id == subject_id])

    def of_subjects(self, subject_id_list):
        exams = [e for e in self.exams if e.subject_id in subject_id_list]
        exams.sort(key=lambda e: e.subject_id)  # sort() is stable so the date ordering will be kept
        return ExamList(exams)


def get_exams(course_id):
    course = get_courses().get(course_id)
    src = fetch(course.get_url_exams())
    soup = BeautifulSoup(src.text, 'html.parser')
    title_list = soup.select('#u-content-core > div:nth-child(2) > div > div.dropdown-component > h3')
    content_list = soup.select('#u-content-core > div:nth-child(2) > div > div.dropdown-component > div.items-container')
    content_list = iter(content_list)
    exams = []
    for title in title_list:
        content = next(content_list)
        exams += exam_factory(title, content, course_id)
    return Exams(exams)


def exam_factory(title, content, course_id):
    subject_id, subject, prof = list(title.stripped_strings)
    subject = subject.title()
    prof = prof.title()
    dates = content.select('table.single-item')
    out = []
    for d in dates:
        date_info = date_info_from_rows(d.select('tr'))
        out.append(Exam(subject_id,
                        subject,
                        course_id,
                        prof,
                        parse_date(date_info['date']),
                        date_info['signup_dates'],
                        date_info['exam_type'],
                        date_info['location'],
                        date_info['notes']))
    return out


def date_info_from_rows(rows):
    info = dict.fromkeys(EXAM_DATE_HEADING_DICT.values())
    for row in rows:
        heading = row.th.text.lower()
        if heading in EXAM_DATE_HEADING_DICT:
            info[EXAM_DATE_HEADING_DICT[heading]] = row.td.text.strip()
    return info


def parse_date(date_str):
    # parse dates like '14 giugno 2019 ore 14:30'
    day, month, year, _, time = date_str.split()
    hour, minute = time.split(':')
    return datetime(day=int(day),
                    month=MONTH_NAMES_DICT[month.lower()],
                    year=int(year),
                    hour=int(hour),
                    minute=int(minute))
