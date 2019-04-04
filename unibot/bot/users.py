import logging
from os import environ as env
from datetime import datetime, timedelta, time

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Boolean, Time
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool


Base = declarative_base()
engine = create_engine('sqlite:///{}'.format(env['DB_PATH']),
                       echo=False,
                       connect_args={'check_same_thread': False},
                       poolclass=StaticPool)
Session = sessionmaker(bind=engine)


class UserNotFoundError(Exception):
    def __init__(self, user_id):
        super().__init__("User '{}' does not exist".format(user_id))


class ChatNotFoundError(Exception):
    def __init__(self, chat_id):
        super().__init__("Chat '{}' does not exist".format(chat_id))


class Repo:
    def __init__(self):
        self.db = Session()


class UserRepo(Repo):
    def __init__(self):
        super().__init__()

    def has(self, user_id, chat_id):
        try:
            self.get(user_id, chat_id)
        except UserNotFoundError:
            return False
        return True

    def get(self, user_id, chat_id):
        res = self.db.query(User).get((user_id, chat_id))
        if res is None:
            raise UserNotFoundError(user_id)
        return res

    def update(self, user):
        self.db.add(user)
        self.db.commit()
        logging.info('New or updated user: %s', user)


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


class UserSettingsRepo(Repo):
    def __init__(self):
        super().__init__()

    def has(self, chat_id):
        try:
            self.get(chat_id)
        except ChatNotFoundError:
            return False
        return True

    def get(self, chat_id):
        res = self.db.query(UserSettings).get(chat_id)
        if res is None:
            raise ChatNotFoundError(chat_id)
        return res

    def update(self, settings):
        self.db.add(settings)
        self.db.commit()

    def delete(self, settings):
        settings.deleted = True
        self.update(settings)
        logging.info("Deleted user chat '%d'", settings.chat_id)

    def get_all(self):
        return self.db.query(UserSettings).all()

    def get_to_remind(self):
        return self.db.query(UserSettings).filter_by(do_remind=True, deleted=False)

    def get_all_chat_id(self):
        return self.db.query(UserSettings.chat_id).all()


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


# Base.metadata.create_all(engine)
