import logging
import re

from telegram.ext import ConversationHandler, CommandHandler, MessageHandler, Filters

from unibot.bot import messages
from unibot.bot.users import UserSettingsRepo
from unibot.bot.conversations.common import step_cancel, send


STEP_DAY_SELECT, STEP_DAY_INVALID = range(0, 2)
REGEX_DAY = re.compile(r'(oggi|domani)', flags=re.IGNORECASE)


def get_handler():
    return ConversationHandler(
        entry_points=[CommandHandler('nonricordarmi', step_start)],
        states={
            STEP_DAY_SELECT: [MessageHandler(Filters.text, step_day_select)],
        },
        fallbacks=[CommandHandler('annulla', step_cancel)]
    )


def step_start(update, context):
    settingsrepo = UserSettingsRepo()
    if not settingsrepo.has(update.effective_chat.id):
        send(update, context, messages.NEED_SETUP)
        settingsrepo.close()
        return ConversationHandler.END
    settings = settingsrepo.get(update.effective_chat.id)

    if settings.do_remind_today and settings.do_remind_tomorrow:
        send(update, context, messages.NOREMINDME_BOTH_ACTIVE)
        settingsrepo.close()
        return STEP_DAY_SELECT

    day = 'oggi' if settings.do_remind_today else 'domani'
    settings.do_remind_today = False
    settings.do_remind_tomorrow = False
    settingsrepo.update(settings)
    settingsrepo.close()

    send(update, context, messages.NOREMINDME_OFF_DAY.format(day))
    return ConversationHandler.END


def step_day_select(update, context):
    match = REGEX_DAY.search(update.message.text)
    if not match:
        send(update, context, messages.NOREMINDME_INVALID_DAY)
        return STEP_DAY_SELECT
    day, = match.groups()
    day = day.lower()

    settingsrepo = UserSettingsRepo()
    settings = settingsrepo.get(update.effective_chat.id)
    if day == 'oggi':
        settings.do_remind_today = False
    if day == 'domani':
        settings.do_remind_tomorrow = False

    settingsrepo.update(settings)
    settingsrepo.close()

    send(update, context, messages.NOREMINDME_OFF_DAY.format(day))
    return ConversationHandler.END
