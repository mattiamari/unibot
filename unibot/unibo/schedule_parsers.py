import logging
from datetime import datetime
from bf4 import BeautifulSoup
from unibot.unibo.schedule import Event


class InvalidSourceDataError(Exception):
    def __init__(self, url):
        super().__init__("Invalid input data for url '{}'".format(url))


class JsonParser:
    def __init__(self):
        pass

    def parse(self, response):
        source = response.json()
        if 'events' not in source:
            logging.error("'events' key not found for url '%s'", response.url)
            raise InvalidSourceDataError(response.url)
        try:
            events = [self._event_factory(e) for e in source['events']]
            events = remove_duplicates(events)
        except Exception as e:
            logging.exception(e)
            raise InvalidSourceDataError(response.url)
        return events

    def _event_factory(self, e):
        event = Event(
            subject_id=e['cod_modulo'],
            title=e['title'].capitalize(),
            date_start=self._parse_date(e['start']),
            date_end=self._parse_date(e['end']),
            room=''
        )
        try:
            event.room = e['aule'][0]['des_risorsa']
        except Exception:
            pass
        return event

    def _parse_date(self, date_str):
        return datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S')


class HtmlParser:
    def __init__(self):
        pass

    def parse(self, response):
        source = response.text
        soup = BeautifulSoup(source)


PARSERS = {'json': JsonParser, 'html': HtmlParser}


def get_parser(parser_type):
    return PARSERS[parser_type]()


def remove_duplicates(events):
    seen = set()
    return [e for e in events if not (e in seen or seen.add(e))]
