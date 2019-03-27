import sqlite3
from os import environ as env
from datetime import datetime
import logging

class Repo:
    def __init__(self):
        self.db = sqlite3.connect(env['DB_PATH'])

    def shutdown(self):
        self.db.commit()
        self.db.close()

    def __del__(self):
        self.db.commit()
        self.db.close()

class UserRepo(Repo):
    def __init__(self):
        super().__init__()
        self.db.row_factory = sqlite3.Row

    def has(self, user_id, chat_id):
        res = self.db.execute("select count(*) from user where user_id=? and chat_id=?", (user_id, chat_id)).fetchone()[0]
        return True if res > 0 else False

    def get(self, user_id, chat_id):
        res = self.db.execute("select * from user where user_id=? and chat_id=?", (user_id, chat_id)).fetchone()
        if isinstance(res, sqlite3.Row):
            return _user_factory(res)
        return None

    def update(self, user):
        self.db.execute("insert or replace into user (user_id, chat_id, first_name, last_name, username) "
            "values (:user_id, :chat_id, :first_name, :last_name, :username)", user.__dict__)
        self.db.commit()
        logging.info('New or updated user: @{}'.format(user.username))

class User:
    def __init__(
        self,
        user_id,
        chat_id,
        first_name,
        last_name,
        username
    ):
        self.user_id = user_id
        self.chat_id = chat_id
        self.first_name = first_name
        self.last_name = last_name
        self.username = username

class UserSettingsRepo(Repo):
    def __init__(self):
        super().__init__()
        self.db.row_factory = sqlite3.Row

    def has(self, chat_id):
        res = self.db.execute("select count(*) from user_settings where chat_id=? and deleted != 1", (chat_id,)).fetchone()[0]
        return True if res > 0 else False

    def get(self, chat_id):
        res = self.db.execute("select * from user_settings where chat_id=? and deleted != 1", (chat_id,)).fetchone()
        if isinstance(res, sqlite3.Row):
            return _usersettings_factory(res)
        return None

    def update(self, settings):
        self.db.execute("insert or replace into user_settings (user_id, chat_id, course_id, year, curricula, do_remind, remind_time) "
            "values (:user_id, :chat_id, :course_id, :year, :curricula, :do_remind, :remind_time)", _usersettings_dict(settings))
        self.db.commit()

    def delete(self, settings):
        self.db.execute("update user_settings set deleted=1 where chat_id=:chat_id", _usersettings_dict(settings))
        self.db.commit()
        logging.info("Deleted user chat '{}'".format(settings.chat_id))

    def get_to_remind(self):
        res = self.db.execute("select * from user_settings where do_remind=1 and deleted != 1")
        return [_usersettings_factory(x) for x in res]

    def get_all_chat_id(self):
        res = self.db.execute("select chat_id from user_settings where deleted != 1")
        return [row['chat_id'] for row in res]

class UserSettings:
    TIME_FORMAT = '%H:%M'

    def __init__(self, user_id, chat_id, course_id, year, curricula, do_remind=False, remind_time=None):
        self.user_id = user_id
        self.chat_id = chat_id
        self.course_id = course_id
        self.year = year
        self.curricula = curricula
        self.do_remind = do_remind
        self.remind_time = remind_time


def _user_factory(row):
    return User(
        row['user_id'],
        row['chat_id'],
        row['first_name'],
        row['last_name'],
        row['username'])

def _usersettings_factory(row):
    do_remind = False
    remind_time = None
    try:
        remind_time = _parse_remind_time(row['remind_time'])
        do_remind = row['do_remind']
    except Exception:
        pass

    return UserSettings(
        row['user_id'],
        row['chat_id'],
        row['course_id'],
        row['year'],
        row['curricula'],
        do_remind,
        remind_time
    )

def _usersettings_dict(settings):
    d = settings.__dict__.copy()
    d['remind_time'] = None
    if settings.remind_time is not None:
        d['remind_time'] = settings.remind_time.strftime(UserSettings.TIME_FORMAT)
    return d

def _parse_remind_time(time_str):
    return datetime.strptime(time_str, UserSettings.TIME_FORMAT).time()
