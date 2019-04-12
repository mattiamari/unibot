from datetime import datetime, timedelta, time
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Boolean, Time


Base = declarative_base()


class User(Base):
    __tablename__ = 'user'
    user_id = Column(Integer(64), primary_key=True)
    chat_id = Column(Integer(64), primary_key=True)
    first_name = Column(String(128))
    last_name = Column(String(128))
    username = Column(String(64))

    def __init__(self,
                 user_id,
                 chat_id,
                 first_name,
                 last_name,
                 username):
        self.user_id = user_id
        self.chat_id = chat_id
        self.first_name = first_name
        self.last_name = last_name
        self.username = username

    def __repr__(self):
        return "<User user_id='{}' first_name='{}' last_name='{}' username='{}'>" \
            .format(self.user_id, self.first_name, self.last_name, self.username)


class UserSettings(Base):
    __tablename__ = 'user_settings'
    chat_id = Column(Integer(64), primary_key=True)
    user_id = Column(Integer(64))
    course_id = Column(String(32))
    year = Column(Integer)
    curricula = Column(String(32), default='')
    do_remind_today = Column(Boolean, default=False)
    remind_time_today = Column(Time, default=None)
    do_remind_tomorrow = Column(Boolean, default=False)
    remind_time_tomorrow = Column(Time, default=None)
    deleted = Column(Boolean, default=False)

    def __init__(self, user_id, chat_id, course_id, year, curricula,
                 do_remind_today=False, remind_time_today=None,
                 do_remind_tomorrow=False, remind_time_tomorrow=None, deleted=False):
        self.user_id = user_id
        self.chat_id = chat_id
        self.course_id = course_id
        self.year = year
        self.curricula = curricula
        self.do_remind_today = do_remind_today
        self.remind_time_today = remind_time_today
        self.do_remind_tomorrow = do_remind_tomorrow
        self.remind_time_tomorrow = remind_time_tomorrow
        self.deleted = deleted

    def __repr__(self):
        return "<UserSettings chat_id='{}' user_id='{}'>" \
            .format(self.chat_id, self.user_id)

    def next_remind_time_today(self):
        return self._next_remind_time(self.do_remind_today, self.remind_time_today)

    def next_remind_time_tomorrow(self):
        return self._next_remind_time(self.do_remind_tomorrow, self.remind_time_tomorrow)

    def _next_remind_time(self, do_remind, remind_time):
        if not do_remind or not isinstance(remind_time, time):
            return None
        now = datetime.now()
        if remind_time > now.time():
            next_date = now + timedelta(days=1)
        else:
            next_date = now

        return next_date.replace(
            hour=remind_time.hour,
            minute=remind_time.minute,
            second=0,
            microsecond=0
        )
