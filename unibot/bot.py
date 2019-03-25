import logging
from os import environ as env
from datetime import date, time

from telegram.ext import Updater, CommandHandler, MessageHandler, ConversationHandler, Filters, BaseFilter
from telegram import ParseMode

import unibot.messages as messages
import unibot.users
import unibot.courses as courses
import unibot.uni_schedule as uni_schedule
import unibot.conversations.setup

import pprint


# class CaseInsensitiveRegexFilter(BaseFilter):
#     def __init__(self, pattern):
#         self.pattern = re.compile(pattern, flags=re.IGNORECASE)
#     def filter(self, message):
#         return False if self.pattern.search(message.text) is None else True


class Bot:
    def __init__(self):
        self.users = unibot.users.UserRepo
        self.user_settings = unibot.users.UserSettingsRepo
        self.updater = Updater(token=env['BOT_TOKEN'], use_context=True)
        self.dispatcher = self.updater.dispatcher
        self.handlers = [
            CommandHandler('start', self.cmd_start),
            CommandHandler('help', self.cmd_command_list),
            CommandHandler('orario', self.cmd_schedule_today),
            CommandHandler('oggi', self.cmd_schedule_today),
            CommandHandler('domani', self.cmd_schedule_tomorrow),
            CommandHandler('ricordami', self.cmd_remindme_on),
            CommandHandler('smetti', self.cmd_remindme_off),
            unibot.conversations.setup.get_handler()
        ]
        self.context = {}

    def run(self):
        self.register_handlers()
        self.dispatcher.job_queue.run_daily(self.daily_schedule, time(hour=7, minute=30))
        # self.dispatcher.job_queue.run_once(self.daily_schedule, 3)
        self.dispatcher.job_queue.start()
        self.updater.start_polling(poll_interval=1.0)
        self.updater.idle()

    def register_handlers(self):
        for h in self.handlers:
            self.dispatcher.add_handler(h)

    def cmd_start(self, update, context):
        if (env['TESTING'] == '1'):
            self._send(update, context, ("Io non sono il vero UniBot ma solo un'istanza di test.\n"
                                        "Usa @unibo_orari_bot"))
            return
        self._send(update, context, messages.CMD_START)

    def cmd_command_list(self, update, context):
        self._send(update, context, messages.COMMAND_LIST)

    def cmd_schedule_today(self, update, context):
        url = self._get_schedule_url_for_user(update.effective_user.id, update.effective_chat.id)
        if url is None:
            self._send(update, context, messages.NEED_SETUP)
            return
        self._send(update, context, uni_schedule.get_today(url))

    def cmd_schedule_tomorrow(self, update, context):
        url = self._get_schedule_url_for_user(update.effective_user.id, update.effective_chat.id)
        if url is None:
            self._send(update, context, messages.NEED_SETUP)
            return
        self._send(update, context, uni_schedule.get_tomorrow(url))

    def cmd_remindme_on(self, update, context):
        settings = self.user_settings()
        setting = settings.get(update.effective_user.id, update.effective_chat.id)
        if setting is None:
            self._send(update, context, messages.NEED_SETUP)
            return
        setting.do_remind = True
        settings.update(setting)
        self._send(update, context, messages.REMINDME_ON)

    def cmd_remindme_off(self, update, context):
        settings = self.user_settings()
        setting = settings.get(update.effective_user.id, update.effective_chat.id)
        if setting is None:
            self._send(update, context, messages.NEED_SETUP)
            return
        setting.do_remind = False
        settings.update(setting)
        self._send(update, context, messages.REMINDME_OFF)

    def daily_schedule(self, context):
        users = self.user_settings().get_to_remind()
        weekday = date.today().weekday()
        logging.info('Sending todays schedule to {} users'.format(len(users)))
        for user in users:
            url = self._get_schedule_url_for_user(user.user_id, user.chat_id)
            if url is None:
                continue
            logging.info(pprint.pformat(weekday))
            logging.info(pprint.pformat(uni_schedule.lesson_days(url)))
            if weekday not in uni_schedule.lesson_days(url):
                continue
            context.bot.send_message(chat_id=user.chat_id, parse_mode=ParseMode.HTML, text=uni_schedule.get_today(url))

    def _send(self, update, context, text):
        context.bot.send_message(chat_id=update.message.chat_id, parse_mode=ParseMode.HTML, text=text)

    def _get_schedule_url_for_user(self, user_id, chat_id):
        settings = self.user_settings().get(user_id, chat_id)
        if settings is None:
            return None
        return courses.get_url_schedule(settings.course_id, settings.year, settings.curricula)
