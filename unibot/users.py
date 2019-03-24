import sqlite3
from os import environ as env
import logging

class Repo:
    def __init__(self):
        self.db = sqlite3.connect(env['DB_PATH'])

    def shutdown(self):
        self.db.commit()
        self.db.close()

    def __del__(self):
        self.shutdown()

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
        with self.db as db:
            db.execute("insert or replace into user (user_id, chat_id, first_name, last_name, username) "
                "values (:user_id, :chat_id, :first_name, :last_name, :username)", user.__dict__)
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

    def has(self, user_id, chat_id):
        res = self.db.execute("select count(*) from user_settings where user_id=? and chat_id=?", (user_id, chat_id)).fetchone()[0]
        return True if res > 0 else False

    def get(self, user_id, chat_id):
        res = self.db.execute("select * from user_settings where user_id=? and chat_id=?", (user_id, chat_id)).fetchone()
        if isinstance(res, sqlite3.Row):
            return _usersettings_factory(res)
        return None

    def update(self, settings):
        with self.db as db:
            db.execute("insert or replace into user_settings (user_id, chat_id, course_id, year, curricula, do_remind) "
                "values (:user_id, :chat_id, :course_id, :year, :curricula, :do_remind)", settings.__dict__)

    def get_to_remind(self):
        res = self.db.execute("select * from user_settings where do_remind=1")
        return [_usersettings_factory(x) for x in res]

class UserSettings:
    def __init__(self, user_id, chat_id, course_id, year, curricula, do_remind=False):
        self.user_id = user_id
        self.chat_id = chat_id
        self.course_id = course_id
        self.year = year
        self.curricula = curricula
        self.do_remind = do_remind


def _user_factory(row):
    return User(
        row['user_id'],
        row['chat_id'],
        row['first_name'],
        row['last_name'],
        row['username'])

def _usersettings_factory(row):
    return UserSettings(
        row['user_id'],
        row['chat_id'],
        row['course_id'],
        row['year'],
        row['curricula'],
        row['do_remind'])
