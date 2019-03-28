import logging
from os import environ
from datetime import datetime, date, time, timedelta
import time as os_time

from telegram.ext import Updater, CommandHandler
from telegram import ParseMode
import telegram.error

from . import conversations, users as bot_users, announcements
from unibot.schedule import courses, schedule as class_schedule

class Bot:
    def __init__(self):
        self.users = bot_users.UserRepo
        self.user_settings = bot_users.UserSettingsRepo
        self.updater = Updater(token=environ['BOT_TOKEN'], use_context=True)
        self.dispatcher = self.updater.dispatcher
        self.handlers = [
            CommandHandler('start', self.cmd_start),
            CommandHandler('help', self.cmd_command_list),
            CommandHandler('orario', self.cmd_schedule_today),
            CommandHandler('oggi', self.cmd_schedule_today),
            CommandHandler('domani', self.cmd_schedule_tomorrow),
            CommandHandler('settimana', self.cmd_schedule_week),
            CommandHandler('prossimasettimana', self.cmd_schedule_next_week),
            CommandHandler('nonricordarmi', self.cmd_remindme_off),
            conversations.setup.get_handler(),
            conversations.remindme.get_handler()
        ]
        self.daily_schedule_repeat_every = timedelta(minutes=3)
        self.daily_schedule_last_run = datetime.now()

    def run(self):
        self.register_handlers()
        self.dispatcher.job_queue.run_repeating(self.daily_schedule, self.daily_schedule_repeat_every)
        self.dispatcher.job_queue.run_once(self.send_announcements, 5)
        # self.dispatcher.job_queue.run_once(self.daily_schedule, 3)
        self.dispatcher.job_queue.start()
        self.updater.start_polling(poll_interval=1.0)
        self.updater.idle()

    def register_handlers(self):
        for h in self.handlers:
            self.dispatcher.add_handler(h)

    def cmd_start(self, update, context):
        if (environ['TESTING'] == '1'):
            self.send(update, context, ("Io non sono il vero UniBot ma solo un'istanza di test.\n"
                                        "Usa @unibo_orari_bot"))
            return
        self.send(update, context, messages.CMD_START)

    def cmd_command_list(self, update, context):
        self.send(update, context, messages.COMMAND_LIST.format(environ['BOT_VERSION']))

    def cmd_schedule_today(self, update, context):
        self.send_schedule(update, context, 'today')

    def cmd_schedule_tomorrow(self, update, context):
        self.send_schedule(update, context, 'tomorrow')
                                            # 'toyota'

    def cmd_schedule_week(self, update, context):
        self.send_schedule(update, context, 'week')

    def cmd_schedule_next_week(self, update, context):
        self.send_schedule(update, context, 'next_week')

    def send_schedule(self, update, context, type):
        settings = self.user_settings().get(update.effective_chat.id)
        if settings is None:
            self.send(update, context, messages.NEED_SETUP)
            return
        logging.info("REQUEST {} chat_id={} course_id={} year={} curricula={}".format(
            type, update.effective_chat.id, settings.course_id, settings.year, settings.curricula))
        try:
            schedule = class_schedule.get_schedule(settings.course_id, settings.year, settings.curricula)
        except Exception as e:
            logging.exception(e)
            self.send(update, context, messages.SCHEDULE_FETCH_ERROR)
            return
        schedule = getattr(schedule, type)()
        if not schedule.has_events():
            self.send(update, context, messages.NO_LESSONS)
            return
        self.send(update, context, schedule.tostring(with_date=True))

    def cmd_remindme_off(self, update, context):
        settings = self.user_settings()
        setting = settings.get(update.effective_chat.id)
        if setting is None:
            self.send(update, context, messages.NEED_SETUP)
            return
        setting.do_remind = False
        settings.update(setting)
        self.send(update, context, messages.REMINDME_OFF)

    def daily_schedule(self, context):
        settings_repo = self.user_settings()
        now = datetime.now()
        users = settings_repo.get_to_remind()
        users = [u for u in users if isinstance(u.remind_time, time)]
        users = [u for u in users if self.daily_schedule_last_run < u.next_remind_time() <= now]
        if len(users) == 0:
            return

        logging.info('Sending todays schedule to {} users'.format(len(users)))
        for user in users:
            try:
                schedule = class_schedule.get_schedule(user.course_id, user.year, user.curricula)
                if not schedule.week_has_lessons():
                    continue
                context.bot.send_message(chat_id=user.chat_id, parse_mode=ParseMode.HTML, text=schedule.today().tostring(with_date=True))
                os_time.sleep(0.1)
            except telegram.error.Unauthorized as e:
                logging.warning(e)
                settings_repo.delete(user)
            except telegram.error.ChatMigrated as e:
                old = user.chat_id
                user.chat_id = e.new_chat_id
                settings_repo.update(user)
                logging.info("Updated chat_id {} to {}".format(old, user.chat_id))
            except Exception as e:
                logging.exception(e)

        self.daily_schedule_last_run = now
        logging.info("Done sending daily schedule")


    def send_announcements(self, context):
        anns = announcements.get_announcements()
        if len(anns) == 0:
            return
        settings_repo = self.user_settings()
        chats = settings_repo.get_all()
        logging.info('Sending announcements to {} chats'.format(len(chats)))
        for ann in anns:
            for chat in chats:
                try:
                    context.bot.send_message(chat_id=chat.chat_id, parse_mode=ParseMode.HTML, text=ann['msg'])
                    os_time.sleep(0.1)
                except telegram.error.Unauthorized as e:
                    logging.warning(e)
                    settings_repo.delete(chat)
                except telegram.error.ChatMigrated as e:
                    old = chat.chat_id
                    chat.chat_id = e.new_chat_id
                    settings_repo.update(chat)
                    logging.info("Updated chat_id {} to {}".format(old, chat.chat_id))
                except Exception as e:
                    logging.exception(e)
            announcements.set_sent(ann)
        announcements.save_sent()

    def send(self, update, context, text):
        try:
            context.bot.send_message(chat_id=update.message.chat_id, parse_mode=ParseMode.HTML, text=text)
        except Exception as e:
            logging.exception(e)
