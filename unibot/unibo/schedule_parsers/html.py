import logging
import re
from datetime import datetime, time, date, timedelta
from bs4 import BeautifulSoup

from unibot.unibo.constants import MONTHNAME_NUM_DICT, DAYNAME_WEEKDAY_DICT
from unibot.unibo.schedule_model import Event
from unibot.unibo.schedule_parsers.errors import ParseError


regex_period = re.compile(r'periodo di lezione:\s+(\d{1,2}) (\w+) (\d{4})\s+-\s+(\d{1,2}) (\w+) (\d{4})',
                          flags=re.MULTILINE | re.IGNORECASE)
regex_time = re.compile(r'(\d{1,2}):(\d{1,2})\s+-\s+(\d{1,2}):(\d{1,2})')


class MissingSubjectsError(Exception):
    pass


class HtmlParser:
    def __init__(self):
        pass

    def parse(self, response):
        source = response.text
        soup = BeautifulSoup(source)
        try:
            subjectiter = SubjectIterator(soup)
            events = list(subjectiter)
            return events
        except Exception as ex:
            logging.exception(ex)
            raise ParseError(response.url)


class SubjectIterator:
    def __init__(self, soup):
        self.subjects = soup.select('div.area-orari > div.flex-tabs > div > div.dropdown-component > h3')
        if len(self.subjects) == 0:
            raise MissingSubjectsError()
        self.periods = iter(soup.select('div.area-orari > div.flex-tabs > div > div.dropdown-component > div.items-container'))

    def __iter__(self):
        for subject in self.subjects:
            subject_id, title = self._parse_subject(subject)
            periods = next(self.periods)
            perioditer = PeriodIterator(periods, subject_id, title)
            for event in perioditer:
                yield event

    def _parse_subject(self, subject_str):
        strings = list(subject_str.stripped_strings)
        return (strings[0], strings[1].capitalize())


class PeriodIterator:
    def __init__(self, soup, subject_id, title):
        self.subject_id = subject_id
        self.title = title
        self.notes = soup.select('p.note')
        self.events = iter(soup.select('table.timetable'))

    def __iter__(self):
        for note in self.notes:
            period_start, period_end = self._parse_period(str(note))
            events = next(self.events)
            eventiter = EventIterator(events, self.subject_id, self.title, period_start, period_end)
            for event in eventiter:
                yield event

    def _parse_period(self, note_str):
        note = regex_period.search(note_str)
        if not note:
            return None
        groups = note.groups()
        period_start = date(day=int(groups[0]),
                            month=MONTHNAME_NUM_DICT[groups[1].lower()],
                            year=int(groups[2]))
        period_end = date(day=int(groups[3]),
                          month=MONTHNAME_NUM_DICT[groups[4].lower()],
                          year=int(groups[5]))
        return (period_start, period_end)


class EventIterator:
    def __init__(self, soup, subject_id, title, period_start, period_end):
        self.subject_id = subject_id
        self.title = title
        self.period_start = period_start
        self.period_end = period_end
        self.events = iter(soup.select('tr'))
        next(self.events)  # skip first row

    def __iter__(self):
        days_num = (self.period_end - self.period_start).days
        for event in self.events:
            td_dayname = next(event.select('td:nth-child(1)')[0].stripped_strings)
            td_time = next(event.select('td:nth-child(2)')[0].stripped_strings)

            weekday = DAYNAME_WEEKDAY_DICT[td_dayname.lower()]
            time_start, time_end = self._parse_time(td_time)
            room = next(event.select('td:nth-child(4)')[0].stripped_strings)

            days = (self.period_start + timedelta(n) for n in range(days_num))
            lesson_days = (d for d in days if d.weekday() == weekday)
            for lesson_date in lesson_days:
                date_start = datetime.combine(lesson_date, time_start)
                date_end = datetime.combine(lesson_date, time_end)
                event = Event(self.subject_id, self.title, date_start,
                              date_end, room)
                yield event

    def _parse_time(self, time_str):
        res = regex_time.search(time_str)
        if not res:
            return None
        groups = res.groups()
        return (time(hour=int(groups[0]), minute=int(groups[1])),
                time(hour=int(groups[2]), minute=int(groups[3])))
