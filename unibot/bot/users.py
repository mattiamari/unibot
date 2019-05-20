import logging

from unibot.db import Session
from unibot.bot.users_model import User, UserSettings


class UserNotFoundError(Exception):
    def __init__(self, user_id):
        super().__init__(f"User '{user_id}' does not exist")


class ChatNotFoundError(Exception):
    def __init__(self, chat_id):
        super().__init__(f"Chat '{chat_id}' does not exist")


class Repo:
    def __init__(self):
        self.db = Session()

    def close(self):
        self.db.close()


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

    def get_to_remind_today(self):
        return self.db.query(UserSettings).filter_by(do_remind_today=True, deleted=False)

    def get_to_remind_tomorrow(self):
        return self.db.query(UserSettings).filter_by(do_remind_tomorrow=True, deleted=False)

    def get_all_chat_id(self):
        return self.db.query(UserSettings.chat_id).all()
