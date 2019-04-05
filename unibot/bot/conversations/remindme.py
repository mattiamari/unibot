import logging
import datetime
import re

from telegram.ext import ConversationHandler, CommandHandler, MessageHandler, Filters
from telegram import ParseMode

import unibot.bot.messages as messages
from unibot.bot.users import UserSettingsRepo, ChatNotFoundError


STEP_TIME_SELECT, STEP_TIME_INVALID = range(0, 2)

TIME_FORMAT = '%H:%M'

REGEX_TIME = re.compile(r'^(\d?\d)[.,:]*(\d?\d?)$')


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
    if not UserSettingsRepo().has(update.effective_chat.id):
        send(update, context, messages.NEED_SETUP)
        return ConversationHandler.END
    send(update, context, messages.REMINDME_START)
    return STEP_TIME_SELECT


def step_time_select(update, context):
    parts = update.message.text.split()
    if len(parts) > 2:
        send(update, context, messages.REMINDME_TIME_INVALID)
        return STEP_TIME_SELECT
    if len(parts) == 1:
        time_str = parts[0]
        remind_type = RemindType.TODAY
    else:
        remind_type_str, time_str = parts
        if remind_type_str not in REMIND_TYPE_DICT:
            send(update, context, messages.REMINDME_TIME_INVALID)
            return STEP_TIME_SELECT
        remind_type = REMIND_TYPE_DICT[remind_type_str]

    match = REGEX_TIME.match(time_str)
    time = time_from_match(match)
    if time is None:
        send(update, context, messages.REMINDME_TIME_INVALID)
        return STEP_TIME_SELECT

    settings = UserSettingsRepo()
    setting = settings.get(update.effective_chat.id)
    if remind_type == RemindType.TODAY:
        setting.do_remind_today = True
        setting.remind_time_today = time
    elif remind_type == RemindType.TOMORROW:
        setting.do_remind_tomorrow = True
        setting.remind_time_tomorrow = time
    settings.update(setting)
    send(update, context, messages.REMINDME_END.format(time.strftime(TIME_FORMAT)))
    return ConversationHandler.END


def step_time_invalid(update, context):
    send(update, context, messages.REMINDME_TIME_INVALID)
    return STEP_TIME_SELECT


def step_cancel(update, context):
    send(update, context, messages.CANCELED)
    return ConversationHandler.END


def time_from_match(match):
    if not match:
        return None
    hour, minute = match.groups()
    try:
        hour = int(hour)
        minute = int(minute) if minute is not None and minute != '' else 0
    except Exception as e:
        logging.exception(e)
        return None
    if hour not in range(0, 24) or minute not in range(0, 60):
        return None
    return datetime.time(hour, minute)


def send(update, context, text):
    context.bot.send_message(chat_id=update.message.chat_id, parse_mode=ParseMode.HTML, text=text)
