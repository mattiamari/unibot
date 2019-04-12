import logging
from datetime import datetime
from bs4 import BeautifulSoup

from unibot.urlfetch import fetch
from unibot.cache import cache_for
from unibot.unibo.courses import get_courses
from unibot.unibo.constants import DAY_NAMES, MONTHNAME_NUM_DICT


EXAM_DATE_HEADING_DICT = {
    'data e ora:': 'date',
    'lista iscrizioni:': 'signup_dates',
    'tipo prova:': 'exam_type',
    'luogo:': 'location',
    'note:': 'notes'
}


class Exam:
    DATE_FORMAT = '%d/%m/%Y %H:%M'

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
        out += "= {} {} =\n<b>Iscrizione:</b> {}\n<b>Tipo prova:</b> {}\n<b>Luogo:</b> {}" \
               .format(DAY_NAMES[self.date.weekday()],
                       self.date.strftime(self.DATE_FORMAT),
                       self.signup_dates, self.exam_type, self.location)
        if self.notes:
            out += "\n<b>Note:</b> {}".format(self.notes)
        return out


class ExamList:
    def __init__(self, items):
        self.items = items

    def __str__(self):
        return self.tostring()

    def subjects(self):
        # returns tuples like (subject_id, heading)
        ids = {e.subject_id for e in self.items}
        return [(sub_id, next(e.heading() for e in self.items if e.subject_id == sub_id))
                for sub_id in ids]

    def having_subject(self, subject_id):
        return [e for e in self.items if e.subject_id == subject_id]

    def tostring(self, limit_per_subject=None):
        out = ''
        for subject_id, heading in self.subjects():
            out += "<b>{}</b>\n".format(heading)
            out += "\n\n".join(e.tostring(with_heading=False)
                               for e in self.having_subject(subject_id)[:limit_per_subject])
            out += "\n\n"
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
        return {e.subject_id for e in self.exams}

    def of_subject(self, subject_id, exclude_finished=False):
        return self.of_subjects([subject_id], exclude_finished)

    def of_subjects(self, subject_id_list, exclude_finished=False):
        now = datetime.now()
        exams = [e for e in self.exams
                 if e.subject_id in subject_id_list
                 and (not exclude_finished or e.date > now)]
        exams.sort(key=lambda e: e.subject_id)  # sort() is stable so the date ordering will be kept
        return ExamList(exams)


@cache_for(minutes=60)
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
                        ' '.join(date_info['location'].split()),
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
                    month=MONTHNAME_NUM_DICT[month.lower()],
                    year=int(year),
                    hour=int(hour),
                    minute=int(minute))
