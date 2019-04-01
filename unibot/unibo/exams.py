import logging
from bs4 import BeautifulSoup

from unibot.urlfetch import fetch
from unibot.cache import cache_for
from unibot.unibo.courses import get_courses

EXAM_DATE_HEADING_DICT = {
    'date e ora:': 'date',
    'lista iscrizioni:': 'signup_dates',
    'tipo prova:': 'exam_type',
    'luogo:': 'location',
    'note:': 'notes'
}

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
        return "{} - {} ({})".format(self.subject_id, self.subject, self.prof)

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
        return '\n'.join(e.tostring(with_heading=False) for e in self.items)

    def has_exams(self):
        return len(self.items) > 0


class Exams:
    def __init__(self, exams):
        self.exams = exams

    def get_all(self):
        return ExamList(self.exams)


def get_exams(course_id):
    courses = get_courses()
    course = courses.get(course_id)
    src = fetch(course.get_url_exams)
    soup = BeautifulSoup(fix_html(src.text), 'html.parser')
    title_list = soup.select('#u-content-core > div:nth-child(2) > div > div.dropdown-component > h3')
    content_list = soup.select('#u-content-core > div:nth-child(2) > div > div.dropdown-component > div.items-container')
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
        date_info = date_info_from_row(d.select('tr'))
        out.append(Exam(subject_id,
                        subject,
                        course_id,
                        prof,
                        date_info['date'],
                        date_info['signup_dates'],
                        date_info['exam_type'],
                        date_info['location'],
                        date_info['notes']))


def date_info_from_rows(rows):
    info = dict.fromkeys(EXAM_DATE_HEADING_DICT.values())
    for row in rows:
        heading = row.th.text.lower()
        if heading in EXAM_DATE_HEADING_DICT:
            info[EXAM_DATE_HEADING_DICT[heading]] = row.td.text
    return info
