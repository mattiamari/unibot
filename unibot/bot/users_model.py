from datetime import datetime, timedelta, time
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Boolean, Time


Base = declarative_base()


class User(Base):
    __tablename__ = 'user'
    user_id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, primary_key=True)
    first_name = Column(String)
    last_name = Column(String)
    username = Column(String)

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
    chat_id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    course_id = Column(String)
    year = Column(Integer)
    curricula = Column(String, default='')
    do_remind = Column(Boolean, default=False)
    remind_time = Column(Time, default=None)
    deleted = Column(Boolean, default=False)

    def __init__(self, user_id, chat_id, course_id, year, curricula, do_remind=False, remind_time=None, deleted=False):
        self.user_id = user_id
        self.chat_id = chat_id
        self.course_id = course_id
        self.year = year
        self.curricula = curricula
        self.do_remind = do_remind
        self.remind_time = remind_time
        self.deleted = deleted

    def __repr__(self):
        return "<UserSettings chat_id='{}' user_id='{}'>" \
            .format(self.chat_id, self.user_id)

    def next_remind_time(self):
        if not self.do_remind or not isinstance(self.remind_time, time):
            return None
        now = datetime.now()
        if self.remind_time > now.time():
            next_date = now + timedelta(days=1)
        else:
            next_date = now

        return next_date.replace(
            hour=self.remind_time.hour,
            minute=self.remind_time.minute,
            second=0,
            microsecond=0
        )
