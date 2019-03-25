from datetime import datetime, date, timedelta
import logging
import pprint

from unibot.urlfetch import fetch
from unibot.cache import cache_for

DAY_NAMES = ['Lunedì', 'Martedì', 'Mercoledì', 'Giovedì', 'Venerdì', 'Sabato', 'Domenica']
STR_TODAY = 'Oggi'
STR_TOMORROW = 'Domani'
STR_NO_LESSONS = 'Nessuna lezione'

REPLACEMENTS = {
    'LABORATORIO ': 'LAB ',
}

LESSON_DAYS = range(0,5)

def get_today(url):
    today = date.today()
    return "<b>{}</b>\n{}".format(STR_TODAY, get_schedule(today, url))

def get_tomorrow(url):
    tomorrow = date.today() + timedelta(days=1)
    return "<b>{}</b>\n{}".format(STR_TOMORROW, get_schedule(tomorrow, url))

def get_next_lesson_day(url):
    tomorrow = date.today() + timedelta(days=1)
    day_name = STR_TOMORROW

    if tomorrow.weekday not in lesson_days(url):
        tomorrow = tomorrow + timedelta(days=7-tomorrow.weekday())
        day_name = DAY_NAMES[tomorrow.weekday()]

    return "<b>{}</b>\n{}".format(day_name, get_schedule(tomorrow, url))

def get_schedule(date, url):
    upstream = events_from_source(url)
    events = [e for e in upstream if e['start'].date() == date]

    if len(events) == 0:
        return STR_NO_LESSONS

    events.sort(key=lambda e: e['start'])
    return schedule_tostring(events)

def abbrev_name(name):
    if not isinstance(name, str):
        return name
    for (old,new) in REPLACEMENTS.items():
        name = name.replace(old, new)
    return name

def schedule_tostring(events):
    return '\n'.join('{}  {}  ({})\n'.format(
        e['time'],
        e['title'],
        e['room']
    ) for e in events)



'''
    fetching and cleaning
'''
def parse_date(date):
    return datetime.strptime(date, '%Y-%m-%dT%H:%M:%S')

def clean_events(data):
    if not data['events']:
        return []
    return [clean_event(e) for e in data['events']]

def shift_weekdays(days):
    return [6 if d == 0 else d-1 for d in days]

def clean_event(event):
    e = {
        'time': '???' if 'time' not in event else event['time'],
        'title': '???' if 'title' not in event else event['title'],
        'room': '',
        'start': parse_date(event['start'])
    }

    try:
        e['room'] = event['aule'][0]['des_risorsa']
    except:
        pass

    return e

@cache_for(minutes=60)
def lesson_days(url):
    res = fetch(url).json()
    if 'daystohide' not in res:
        return set(range(0,6))
    hide = set(shift_weekdays(res['daystohide']))
    return set(range(0,7)) - hide

@cache_for(minutes=60)
def events_from_source(url):
    res = fetch(url)
    return clean_events(res.json())

@cache_for(minutes=60)
def curricula_from_source(url):
    res = fetch(url)
    return res.json()
