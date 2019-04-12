import logging
import datetime
import re

from telegram.ext import ConversationHandler, CommandHandler, MessageHandler, Filters
from telegram import ParseMode

from unibot.bot.conversations.common import step_cancel, send
import unibot.bot.messages as messages
from unibot.bot.users import UserSettingsRepo, ChatNotFoundError


STEP_TIME_SELECT, STEP_TIME_INVALID = range(0, 2)

TIME_FORMAT = '%H:%M'

REGEX_TIME = re.compile(r'((?:oggi){0,1}|domani)\s*(\d{1,2})[.,: ]*(\d{0,2})', flags=re.IGNORECASE)


class RemindType:
    TODAY = 1
    TOMORROW = 2


REMIND_TYPE_DICT = {'oggi': RemindType.TODAY, 'domani': RemindType.TOMORROW}


def get_handler():
    return ConversationHandler(
        entry_points=[CommandHandler('ricordami', step_start)],
        states={
            STEP_TIME_SELECT: [MessageHandler(Filters.text, step_time_select)],
            STEP_TIME_INVALID: [MessageHandler(Filters.text, step_time_invalid)]
        },
        fallbacks=[CommandHandler('annulla', step_cancel)]
    )


def step_start(update, context):
    settingsrepo = UserSettingsRepo()
    if not settingsrepo.has(update.effective_chat.id):
        send(update, context, messages.NEED_SETUP)
        settingsrepo.close()
        return ConversationHandler.END
    send(update, context, messages.REMINDME_START)
    settingsrepo.close()
    return STEP_TIME_SELECT


def step_time_select(update, context):
    match = REGEX_TIME.search(update.message.text)
    if not match:
        send(update, context, messages.REMINDME_TIME_INVALID)
        return STEP_TIME_SELECT
    remind_type_str, hour, minute = match.groups()
    remind_type_str = remind_type_str.lower()

    if remind_type_str == '':
        remind_type = RemindType.TODAY
    else:
        if remind_type_str not in REMIND_TYPE_DICT:
            send(update, context, messages.REMINDME_TIME_INVALID)
            return STEP_TIME_SELECT
        remind_type = REMIND_TYPE_DICT[remind_type_str]

    time = time_from_string(hour, minute)
    if time is None:
        send(update, context, messages.REMINDME_TIME_INVALID)
        return STEP_TIME_SELECT

    settingsrepo = UserSettingsRepo()
    setting = settingsrepo.get(update.effective_chat.id)
    if remind_type == RemindType.TODAY:
        setting.do_remind_today = True
        setting.remind_time_today = time
        term_day = messages.TERM_TODAY
    elif remind_type == RemindType.TOMORROW:
        setting.do_remind_tomorrow = True
        setting.remind_time_tomorrow = time
        term_day = messages.TERM_TOMORROW
    settingsrepo.update(setting)
    settingsrepo.close()
    send(update, context, messages.REMINDME_END.format(term_day, time.strftime(TIME_FORMAT)))
    return ConversationHandler.END


def step_time_invalid(update, context):
    send(update, context, messages.REMINDME_TIME_INVALID)
    return STEP_TIME_SELECT


def time_from_string(hour, minute):
    try:
        hour = int(hour)
        minute = int(minute) if minute is not None and minute != '' else 0
        return datetime.time(hour, minute)
    except ValueError:
        return None
