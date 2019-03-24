import logging
import sys
from os import environ as env
from datetime import date, time

from telegram.ext import Updater, CommandHandler, MessageHandler, ConversationHandler, Filters, BaseFilter
from telegram import ParseMode

import create_db
import messages
import users as mod_users
import courses
import uni_schedule

import pprint


# class CaseInsensitiveRegexFilter(BaseFilter):
#     def __init__(self, pattern):
#         self.pattern = re.compile(pattern, flags=re.IGNORECASE)
#     def filter(self, message):
#         return False if self.pattern.search(message.text) is None else True


class Bot:
    SETUP_SEARCH, SETUP_SEARCH_SELECT, SETUP_YEAR, SETUP_CURRICULA_SELECT = range(0,4)

    def __init__(self):
        self.users = mod_users.UserRepo
        self.user_settings = mod_users.UserSettingsRepo
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
            ConversationHandler(
                entry_points=[CommandHandler('setup', self.setup_step_start)],
                states={
                    self.SETUP_SEARCH: [MessageHandler(Filters.text, self.setup_step_search)],
                    self.SETUP_SEARCH_SELECT: [
                        MessageHandler(Filters.regex('^\d+$'), self.setup_step_search_select),
                        CommandHandler('cerca', self.setup_search_again)
                    ],
                    self.SETUP_YEAR: [
                        MessageHandler(Filters.regex('^\d+$'), self.setup_step_year),
                        MessageHandler(Filters.text, self.setup_step_year_invalid)
                    ],
                    self.SETUP_CURRICULA_SELECT: [
                        MessageHandler(Filters.regex('^\d+$'), self.setup_step_curricula_select),
                        CommandHandler('cerca', self.setup_search_again)
                    ],
                },
                fallbacks=[CommandHandler('stop', self.setup_step_stop)]
            )
        ]
        self.context = {}

    def run(self):
        self.register_handlers()
        self.dispatcher.job_queue.run_daily(self.daily_schedule, time(hour=7, minute=0), days=tuple(range(0,6)))
        # self.dispatcher.job_queue.run_once(self.daily_schedule, 3)
        self.updater.start_polling(poll_interval=1.0)
        self.updater.idle()

    def register_handlers(self):
        for h in self.handlers:
            self.dispatcher.add_handler(h)

    def cmd_start(self, update, context):
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

    def setup_step_start(self, update, context):
        self._send(update, context, messages.SETUP_STEP_START)
        self._send(update, context, messages.SETUP_STEP_SEARCH)

        users = self.users()
        user = users.get(update.effective_user.id, update.effective_chat.id)
        if user is None:
            user = mod_users.User(
                update.effective_user.id,
                update.effective_chat.id,
                update.effective_user.first_name,
                update.effective_user.last_name,
                update.effective_user.username
            )
        settings = mod_users.UserSettings(
            update.effective_user.id,
            update.effective_chat.id,
            course_id='',
            year=1,
            curricula=''
        )
        self.context[update.effective_chat.id] = {'user': user, 'settings': settings}

        return self.SETUP_SEARCH

    def setup_step_search(self, update, context):
        if len(update.message.text) < 4:
            self._send(update, context, messages.QUERY_TOO_SMALL)
            return self.SETUP_SEARCH

        matches = courses.search(update.message.text)
        if len(matches) == 0:
            self._send(update, context, messages.COURSE_SEARCH_NO_RESULT)
            return self.SETUP_SEARCH

        matches = dict(enumerate(matches, start=1))
        self.context[update.effective_chat.id]['search_matches'] = matches
        matches_list = ''.join(
            messages.COURSE_SEARCH_RESULT_ITEM.format(n, c['title']) for (n,c) in matches.items())

        self._send(update, context,
            '{}\n\n{}\n{}'.format(messages.COURSE_SEARCH_RESULTS, matches_list, messages.COURSE_SEARCH_CHOOSE_RESULT))

        return self.SETUP_SEARCH_SELECT

    def setup_search_again(self, update, context):
        return self.SETUP_SEARCH

    def setup_step_search_select(self, update, context):
        search_matches = self.context[update.effective_chat.id]['search_matches']
        selected_num = int(update.message.text)
        if selected_num < 1 or selected_num > len(search_matches):
            self._send(update, context, messages.INVALID_SELECTION)
            return self.SETUP_SEARCH_SELECT

        selected_course = search_matches[selected_num]
        self.context[update.effective_chat.id]['settings'].course_id = selected_course['id']
        self._send(update, context, messages.SELECT_YEAR)
        return self.SETUP_YEAR

    def setup_step_year(self, update, context):
        self.context[update.effective_chat.id]['settings'].year = int(update.message.text)

        curricula_url = courses.get_url_curricula(
            self.context[update.effective_chat.id]['settings'].course_id,
            self.context[update.effective_chat.id]['settings'].year)

        curricula = uni_schedule.curricula_from_source(curricula_url)
        if len(curricula) == 0:
            self._send(update, context, messages.NO_CURRICULA_FOUND)
            return self.SETUP_YEAR

        curricula = dict(enumerate(curricula, start=1))
        curricula_list = ''.join(messages.CURRICULA_RESULT_ITEM.format(n, c['label']) for (n,c) in curricula.items())
        self.context[update.effective_chat.id]['curricula'] = curricula

        self._send(update, context, '{}\n\n{}\n{}'.format(
            messages.CURRICULA_RESULTS,
            curricula_list,
            messages.COURSE_SEARCH_CHOOSE_RESULT))
        return self.SETUP_CURRICULA_SELECT

    def setup_step_year_invalid(self, update, context):
        self._send(update, context, messages.YEAR_NOT_VALID)
        return self.SETUP_YEAR

    def setup_step_curricula_select(self, update, context):
        curricula = self.context[update.effective_chat.id]['curricula']
        selected_num = int(update.message.text)
        if selected_num < 1 or selected_num > len(curricula):
            self._send(update, context, messages.INVALID_SELECTION)
            return self.SETUP_CURRICULA_SELECT

        selected_curricula = curricula[selected_num]
        self.context[update.effective_chat.id]['settings'].curricula = selected_curricula['value']

        self.users().update(self.context[update.effective_chat.id]['user'])
        self.user_settings().update(self.context[update.effective_chat.id]['settings'])

        self._send(update, context, messages.SETUP_DONE)
        del self.context[update.effective_chat.id]
        return ConversationHandler.END

    def setup_step_stop(self, update, context):
        self._send(update, context, messages.SETUP_STOPPED)
        return ConversationHandler.END

    def daily_schedule(self, context):
        users = self.user_settings().get_to_remind()
        weekday = date.today().weekday()
        for user in users:
            url = self._get_schedule_url_for_user(user.user_id, user.chat_id)
            if url is None:
                continue
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


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO,
                        stream=sys.stdout)
    create_db.create()
    bot = Bot()
    bot.run()
