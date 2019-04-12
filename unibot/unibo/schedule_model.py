from datetime import date, timedelta

from unibot.unibo.constants import DAY_NAMES


class Event:
    TIME_FORMAT = '%H:%M'

    def __init__(self, subject_id, title, date_start, date_end, room):
        self.subject_id = subject_id
        self.title = title
        self.date_start = date_start
        self.date_end = date_end
        self.room = room

    def __str__(self):
        return "<b>{} - {}</b>  {}  ({})".format(
            self.date_start.time().strftime(self.TIME_FORMAT),
            self.date_end.time().strftime(self.TIME_FORMAT),
            self.title,
            self.room
        )

    def __hash__(self):
        return hash((self.title,
                     self.date_start.timestamp(),
                     self.date_end.timestamp(),
                     self.room))

    def __eq__(self, other):
        return hash(self) == hash(other)


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
        for event in self.items:
            if (with_date and last_day != event.date_start.date()):
                # write date for each day
                if last_day is not None:
                    out += '\n'
                out += '<b>= {} {} =</b>\n\n'.format(
                    DAY_NAMES[event.date_start.date().weekday()],
                    event.date_start.date().strftime(self.DATE_FORMAT)
                )
                last_day = event.date_start.date()
            out += str(event) + '\n\n'
        return out


class Schedule:
    def __init__(self, events):
        self.events = events
        self.events.sort(key=lambda e: e.date_start)

    def subjects(self):
        return set(e.subject_id for e in self.events)

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
        if next_date is None:
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
        return len(self.week()) > 0

    def next_week_has_lessons(self):
        return len(self.next_week()) > 0
