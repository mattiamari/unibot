import logging
import datetime
import re

from telegram.ext import ConversationHandler, CommandHandler, MessageHandler, Filters, RegexHandler
from telegram import ParseMode

import unibot.messages as messages
import unibot.users as users

STEP_TIME_SELECT, STEP_TIME_INVALID = range(0,2)
TIME_FORMAT='%H:%M'

regex_time = re.compile(r'^(\d?\d)[.,:]*(\d?\d?)$')

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
    settings = users.UserSettingsRepo()
    setting = settings.get(update.effective_chat.id)
    if setting is None:
        send(update, context, messages.NEED_SETUP)
        return ConversationHandler.END

    send(update, context, messages.REMINDME_START)
    return STEP_TIME_SELECT

def step_time_select(update, context):
    match = regex_time.match(update.message.text)
    time = time_from_match(match)
    if time is None:
        send(update, context, messages.REMINDME_TIME_INVALID)
        return STEP_TIME_SELECT

    settings = users.UserSettingsRepo()
    setting = settings.get(update.effective_chat.id)
    setting.do_remind = True
    setting.remind_time = time
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
