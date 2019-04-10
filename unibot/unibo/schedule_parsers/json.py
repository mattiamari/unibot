import logging
from datetime import datetime
from unibot.unibo.schedule_model import Event
from unibot.unibo.schedule_parsers.errors import ParseError


class JsonParser:
    def __init__(self):
        pass

    def parse(self, response):
        source = response.json()
        if 'events' not in source:
            logging.error("'events' key not found for url '%s'", response.url)
            raise ParseError(response.url)
        try:
            events = [self._event_factory(e) for e in source['events']]
        except Exception as e:
            logging.exception(e)
            raise ParseError(response.url)
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
