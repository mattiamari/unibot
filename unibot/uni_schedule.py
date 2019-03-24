from datetime import datetime, date, timedelta
import requests
import logging
import os
import pprint

USER_AGENT = 'unibo_orari_bot/{}'.format(os.environ['VERSION'])
DAY_NAMES = ['Lunedì', 'Martedì', 'Mercoledì', 'Giovedì', 'Venerdì', 'Sabato', 'Domenica']
STR_TODAY = 'Oggi'
STR_TOMORROW = 'Domani'
STR_NO_LESSONS = 'Nessuna lezione'

REPLACEMENTS = {
    'LABORATORIO ': 'LAB ',
}

LESSON_DAYS = range(0,5)

class FetchError(Exception):
    pass

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

def cached(minutes=60):
    def cached_inner(func):
        cache = {'some_url': {'data': None, 'last_update': None}}
        def decorate(url):
            if url not in cache or cache[url]['last_update'] is None or datetime.now() - cache[url]['last_update'] > timedelta(minutes=minutes):
                cache[url] = {'data': func(url), 'last_update': datetime.now()}
            return cache[url]['data']
        return decorate
    return cached_inner

@cached(minutes=60)
def lesson_days(url):
    res = get_url(url).json()
    if 'daystohide' not in res:
        return set(range(0,6))
    hide = [6 if d == 0 else d-1 for d in res['daystohide']]
    hide = set(hide)
    return set(range(0,7)) - hide

@cached(minutes=60)
def events_from_source(url):
    res = get_url(url)
    return clean_events(res.json())

@cached(minutes=60)
def curricula_from_source(url):
    res = get_url(url)
    return res.json()

@cached(minutes=10)
def get_url(url):
    try:
        logging.info("Getting from upstream: {}".format(url))
        res = requests.get(url, timeout=10, headers={'user-agent': USER_AGENT})
    except requests.Timeout:
        logging.warning("Cannot get '{}'. Request timed out".format(url))
        raise FetchError()

    if res.status_code != requests.codes.ok:
        logging.warning("Cannot get '{}'. Request returned {}".format(url, res.status_code))
        raise FetchError()
    return res
