import logging
from os import environ
from datetime import datetime, time, timedelta
import time as os_time

from telegram.ext import Updater, CommandHandler
from telegram import ParseMode
import telegram.error

from unibot.bot import conversations, announcements, messages
from unibot.bot.users import UserRepo, UserSettingsRepo, ChatNotFoundError
from unibot.unibo import lastminute
from unibot.unibo.schedule import get_schedule
from unibot.unibo.courses import get_courses, NotSupportedError
from unibot.unibo.exams import get_exams


class Bot:
    def __init__(self):
        self.users = UserRepo
        self.user_settings = UserSettingsRepo
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
            CommandHandler('lastminute', self.cmd_lastminute),
            CommandHandler('esami', self.cmd_exams),
            conversations.setup.get_handler(),
            conversations.remindme.get_handler(),
            conversations.noremindme.get_handler()
        ]
        self.daily_schedule_repeat_every = timedelta(minutes=3)
        self.daily_schedule_today_last_run = datetime.now()
        self.daily_schedule_tomorrow_last_run = datetime.now()

    def run(self):
        self.register_handlers()
        if environ['TESTING'] == '0':
            self.dispatcher.job_queue.run_repeating(self.daily_schedule_today, self.daily_schedule_repeat_every)
            self.dispatcher.job_queue.run_repeating(self.daily_schedule_tomorrow, self.daily_schedule_repeat_every)
            self.dispatcher.job_queue.run_once(self.send_announcements, 5)
            # self.dispatcher.job_queue.run_once(self.daily_schedule, 3)
        self.dispatcher.job_queue.start()
        self.updater.start_polling(poll_interval=1.0)
        self.updater.idle()

    def register_handlers(self):
        for h in self.handlers:
            self.dispatcher.add_handler(h)

    def cmd_start(self, update, context):
        if environ['TESTING'] == '1':
            self.send(update, context,
                      ("Io non sono il vero UniBot ma solo un'istanza di test.\n"
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

    def send_schedule(self, update, context, schedule_type):
        try:
            settings = self.user_settings().get(update.effective_chat.id)
        except ChatNotFoundError:
            self.send(update, context, messages.NEED_SETUP)
            return
        logging.info("REQUEST %s chat_id=%d course_id=%s year=%d curricula=%s",
                     schedule_type, update.effective_chat.id, settings.course_id,
                     settings.year, settings.curricula)
        try:
            schedule = get_schedule(
                settings.course_id, settings.year, settings.curricula)
        except NotSupportedError as ex:
            self.send(update, context, messages.COURSE_NOT_SUPPORTED.format(ex.reason))
            return
        except Exception as ex:
            logging.exception(ex)
            self.send(update, context, messages.SCHEDULE_FETCH_ERROR)
            return
        schedule = getattr(schedule, schedule_type)()
        if not schedule.has_events():
            self.send(update, context, messages.NO_LESSONS)
            return
        self.send(update, context, schedule.tostring(with_date=True))

    def cmd_remindme_off(self, update, context):
        settings = self.user_settings()
        try:
            setting = settings.get(update.effective_chat.id)
        except ChatNotFoundError:
            self.send(update, context, messages.NEED_SETUP)
            return
        setting.do_remind = False
        settings.update(setting)
        self.send(update, context, messages.REMINDME_OFF)

    def cmd_lastminute(self, update, context):
        settings = self.user_settings()
        try:
            setting = settings.get(update.effective_chat.id)
        except ChatNotFoundError:
            self.send(update, context, messages.NEED_SETUP)
            return
        logging.info("REQUEST lastminute chat_id=%d course_id=%s year=%d curricula=%s",
                     update.effective_chat.id, setting.course_id,
                     setting.year, setting.curricula)
        course = get_courses().get(setting.course_id)
        if not course.has_lastminute():
            self.send(update, context, messages.NOT_SUPPORTED_LASTMINUTE)
            return
        try:
            news = lastminute.get_news(course.url_lastminute)
        except Exception as ex:
            logging.exception(ex)
            self.send(update, context, messages.FETCH_ERROR)
            return
        if not news:
            self.send(update, context, messages.NO_NEWS)
            return
        msg = '\n\n'.join(str(n) for n in news)
        self.send(update, context, msg)

    def cmd_exams(self, update, context):
        settings = self.user_settings()
        try:
            setting = settings.get(update.effective_chat.id)
        except ChatNotFoundError:
            self.send(update, context, messages.NEED_SETUP)
            return
        logging.info("REQUEST exams chat_id=%d course_id=%s year=%d curricula=%s",
                     update.effective_chat.id, setting.course_id,
                     setting.year, setting.curricula)
        try:
            subjects = get_schedule(setting.course_id, setting.year, setting.curricula).subjects()
            exams = get_exams(setting.course_id).of_subjects(subjects, exclude_finished=True)
        except NotSupportedError as ex:
            self.send(update, context, messages.COURSE_NOT_SUPPORTED.format(ex.reason))
            return
        except Exception as ex:
            logging.exception(ex)
            self.send(update, context, messages.FETCH_ERROR)
            return
        self.send(update, context, exams.tostring(limit_per_subject=3))

    def daily_schedule_today(self, context):
        now = datetime.now()
        if now.weekday() in [5, 6]:
            # don't send reminders on the weekend
            self.daily_schedule_today_last_run = now
            return
        settings_repo = self.user_settings()
        users = settings_repo.get_to_remind_today()
        users = [u for u in users if isinstance(u.remind_time_today, time)]
        users = [u for u in users if self.daily_schedule_today_last_run < u.next_remind_time_today() <= now]
        if not users:
            return

        logging.info('Sending todays schedule to %d users', len(users))
        for user in users:
            try:
                schedule = get_schedule(user.course_id,
                                        user.year,
                                        user.curricula)
                if not schedule.week_has_lessons():
                    if now.weekday() == 0:
                        msg = "{}\n\n{}".format(messages.NO_LESSONS_WEEK, messages.NO_REMIND_THIS_WEEK)
                        context.bot.send_message(chat_id=user.chat_id, parse_mode=ParseMode.HTML, text=msg)
                    continue
                schedule = schedule.today()
                msg = "<b>{}</b>\n\n{{}}".format(messages.YOUR_LESSONS_TODAY)
                if not schedule.has_events():
                    msg = msg.format(messages.NO_LESSONS)
                    context.bot.send_message(chat_id=user.chat_id, parse_mode=ParseMode.HTML, text=msg)
                    continue
                msg = msg.format(schedule.tostring(with_date=True))
                context.bot.send_message(chat_id=user.chat_id, parse_mode=ParseMode.HTML, text=msg)
                os_time.sleep(0.1)
            except NotSupportedError as ex:
                context.bot.send_message(chat_id=user.chat_id,
                                         parse_mode=ParseMode.HTML,
                                         text=messages.COURSE_NOT_SUPPORTED.format(ex.reason))
            except telegram.error.Unauthorized as e:
                logging.warning(e)
                settings_repo.delete(user)
            except telegram.error.ChatMigrated as e:
                old = user.chat_id
                user.chat_id = e.new_chat_id
                settings_repo.update(user)
                logging.info("Updated chat_id %d to %d", old, user.chat_id)
            except Exception as e:
                logging.exception(e)

        self.daily_schedule_today_last_run = now
        logging.info("Done sending today's schedule")

    def daily_schedule_tomorrow(self, context):
        now = datetime.now()
        if now.weekday() == 5:
            # don't send reminders on the weekend
            self.daily_schedule_tomorrow_last_run = now
            return
        settings_repo = self.user_settings()
        users = settings_repo.get_to_remind_tomorrow()
        users = [u for u in users if isinstance(u.remind_time_tomorrow, time)]
        users = [u for u in users if self.daily_schedule_tomorrow_last_run < u.next_remind_time_tomorrow() <= now]
        if not users:
            return

        logging.info('Sending tomorrows schedule to %d users', len(users))
        for user in users:
            try:
                schedule = get_schedule(user.course_id,
                                        user.year,
                                        user.curricula)
                if now.weekday() == 6 and not schedule.next_week_has_lessons():
                    msg = "{}\n\n{}".format(messages.NO_LESSONS_WEEK, messages.NO_REMIND_THIS_WEEK)
                    context.bot.send_message(chat_id=user.chat_id, parse_mode=ParseMode.HTML, text=msg)
                    continue
                if now.weekday() != 6 and not schedule.week_has_lessons():
                    continue
                schedule = schedule.tomorrow()
                msg = "<b>{}</b>\n\n{{}}".format(messages.YOUR_LESSONS_TOMORROW)
                if not schedule.has_events():
                    msg = msg.format(messages.NO_LESSONS)
                    context.bot.send_message(chat_id=user.chat_id, parse_mode=ParseMode.HTML, text=msg)
                    continue
                msg = msg.format(schedule.tostring(with_date=True))
                context.bot.send_message(chat_id=user.chat_id, parse_mode=ParseMode.HTML, text=msg)
                os_time.sleep(0.1)
            except NotSupportedError as ex:
                context.bot.send_message(chat_id=user.chat_id,
                                         parse_mode=ParseMode.HTML,
                                         text=messages.COURSE_NOT_SUPPORTED.format(ex.reason))
            except telegram.error.Unauthorized as e:
                logging.warning(e)
                settings_repo.delete(user)
            except telegram.error.ChatMigrated as e:
                old = user.chat_id
                user.chat_id = e.new_chat_id
                settings_repo.update(user)
                logging.info("Updated chat_id %d to %d", old, user.chat_id)
            except Exception as e:
                logging.exception(e)

        self.daily_schedule_tomorrow_last_run = now
        logging.info("Done sending tomorrow's schedule")

    def send_announcements(self, context):
        anns = announcements.get_announcements()
        if not anns:
            return
        settings_repo = self.user_settings()
        chats = settings_repo.get_all()
        logging.info('Sending announcements to %d chats', len(chats))
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
                    logging.info("Updated chat_id %d to %d", old, chat.chat_id)
                except Exception as e:
                    logging.exception(e)
            announcements.set_sent(ann)
        announcements.save_sent()

    def send(self, update, context, text):
        for msg in split_message(text):
            try:
                context.bot.send_message(chat_id=update.message.chat_id, parse_mode=ParseMode.HTML, text=msg)
                os_time.sleep(0.05)
            except Exception as e:
                logging.exception(e)


def split_message(msg):
    out = []
    rows = msg.split('\n')
    end_row = len(rows)
    while sum(len(r) for r in rows[:end_row]) > 2048:
        end_row -= 1
    out.append('\n'.join(rows[:end_row]))
    if end_row < len(rows):
        out += split_message('\n'.join(rows[end_row:]))
    return out
