from datetime import datetime, date, timedelta
import logging

from unibot.urlfetch import fetch
from unibot.cache import cache_for
from unibot.courses import get_url_schedule

DAY_NAMES = ['Lunedì', 'Martedì', 'Mercoledì', 'Giovedì', 'Venerdì', 'Sabato', 'Domenica']

class InvalidSourceDataError(Exception):
    def __init__(self, url):
        super().__init__("Invalid input data for url '{}'".format(url))

class Event:
    TIME_FORMAT='%H:%M'

    def __init__(self, title, date_start, date_end, room):
        self.title = title
        self.date_start = date_start
        self.date_end = date_end
        self.room = room

    def __str__(self):
        return "{} - {}  {}  ({})".format(
            self.date_start.time().strftime(self.TIME_FORMAT),
            self.date_end.time().strftime(self.TIME_FORMAT),
            self.title,
            self.room
        )

class EventList:
    DATE_FORMAT = '%d/%m/%Y'

    def __init__(self, events):
        self.items = events

    def __str__(self):
        return self.tostring()

    def __iter__(self):
        return iter(self.items)

    def __getitem__(self, key):
        return self.items[key]

    def __len__(self):
        return len(self.items)

    def has_events(self):
        return len(self.items) > 0

    def tostring(self, with_date=False):
        out = ''
        last_day = None
        for e in self.items:
            if with_date and (last_day is None or last_day != e.date_start.date()):
                out += '<b>{} {}</b>\n'.format(
                    DAY_NAMES[e.date_start.date().weekday()],
                    e.date_start.date().strftime(self.DATE_FORMAT)
                )
                last_day = e.date_start.date()
            out += str(e) + '\n\n'
        return out

class Schedule:
    def __init__(self, events):
        self.events = events
        self.events.sort(key=lambda e: e.date_start)

    def today(self):
        return self.of_day(date.today())

    def tomorrow(self):
        tomorrow = date.today() + timedelta(days=1)
        return self.of_day(tomorrow)

    def week(self):
        start = date.today() - timedelta(days=date.today().weekday())
        end = start + timedelta(days=6)
        return self.between(start, end)

    def next_week(self):
        start = date.today() + timedelta(days=7-date.today().weekday())
        end = start + timedelta(days=6)
        return self.between(start, end)

    def next_class_day(self):
        next_date = self.next_lesson_date()
        if next_date == None:
            return None
        return self.of_day(next_date)

    def of_day(self, date):
        return EventList([e for e in self.events if e.date_start.date() == date])

    def between(self, date_start, date_end):
        return EventList([e for e in self.events if date_start <= e.date_start.date() <= date_end])

    def next_lesson_date(self):
        tomorrow = date.today() + timedelta(days=1)
        events = (e for e in self.events if e.date_start.date() >= tomorrow)
        try:
            next_event = next(events)
        except Exception:
            return None
        return next_event.date_start

    def week_has_lessons(self):
        return True if len(self.week()) > 0 else False

def get_schedule(course_id, year, curricula=''):
    src_url = get_url_schedule(course_id, year, curricula)
    src_data = fetch(src_url).json()
    if 'events' not in src_data:
        logging.error("'events' key not found for url '{}'".format(src_url))
        raise InvalidSourceDataError(src_url)
    try:
        events = [event_factory(e) for e in src_data['events']]
    except Exception as e:
        logging.error(e)
        raise InvalidSourceDataError(src_url)
    return Schedule(events)


#
# private stuff
#

def event_factory(e):
    event = Event(
        title=e['title'],
        date_start=parse_date(e['start']),
        date_end=parse_date(e['end']),
        room=''
    )
    try:
        event.room = e['aule'][0]['des_risorsa']
    except Exception:
        pass
    return event

def parse_date(date):
    return datetime.strptime(date, '%Y-%m-%dT%H:%M:%S')
