import logging

from telegram.ext import ConversationHandler, CommandHandler, MessageHandler, Filters
from telegram import ParseMode

from unibot.urlfetch import FetchError
import unibot.bot.messages as messages
from unibot.unibo.courses import get_courses, get_curricula, CourseNotFoundError, QueryTooShortError
from unibot.bot.users import UserRepo, UserSettingsRepo, UserNotFoundError
from unibot.bot.users_model import User, UserSettings


SETUP_SEARCH, SETUP_SEARCH_SELECT, SETUP_YEAR, SETUP_CURRICULA_SELECT = range(0, 4)
conv_context = {}


def get_handler():
    return ConversationHandler(
        entry_points=[CommandHandler('setup', setup_step_start)],
        states={
            SETUP_SEARCH: [MessageHandler(Filters.text, setup_step_search)],
            SETUP_SEARCH_SELECT: [
                MessageHandler(Filters.regex(r'^\d+$'), setup_step_search_select),
                CommandHandler('cerca', setup_search_again)
            ],
            SETUP_YEAR: [
                MessageHandler(Filters.regex(r'^\d+$'), setup_step_year),
                MessageHandler(Filters.text, setup_step_year_invalid)
            ],
            SETUP_CURRICULA_SELECT: [
                MessageHandler(Filters.regex(r'^\d+$'), setup_step_curricula_select),
                CommandHandler('cerca', setup_search_again)
            ],
        },
        fallbacks=[CommandHandler('annulla', setup_step_cancel)]
    )


def setup_step_start(update, context):
    send(update, context, messages.SETUP_STEP_START)
    send(update, context, messages.SETUP_STEP_SEARCH)

    conv_context[update.effective_chat.id] = {}
    ctx = conv_context[update.effective_chat.id]

    ctx['user_repo'] = UserRepo()
    ctx['user_settings_repo'] = UserSettingsRepo()

    try:
        user = ctx['user_repo'].get(update.effective_user.id, update.effective_chat.id)
        settings = ctx['user_settings_repo'].get(update.effective_chat.id)
    except UserNotFoundError:
        user = User(
            update.effective_user.id,
            update.effective_chat.id,
            update.effective_user.first_name,
            update.effective_user.last_name,
            update.effective_user.username
        )
        settings = UserSettings(
            update.effective_user.id,
            update.effective_chat.id,
            course_id='',
            year=1,
            curricula=''
        )
    ctx['user'] = user
    ctx['settings'] = settings

    return SETUP_SEARCH


def setup_step_search(update, context):
    ctx = conv_context[update.effective_chat.id]
    courses = get_courses()
    try:
        matches = courses.search(update.message.text)
    except QueryTooShortError:
        send(update, context, messages.QUERY_TOO_SHORT)
        return SETUP_SEARCH

    if not matches:
        send(update, context, messages.COURSE_SEARCH_NO_RESULT)
        return SETUP_SEARCH

    matches = dict(enumerate(matches, start=1))
    ctx['search_matches'] = matches
    matches_list = ''.join(messages.COURSE_SEARCH_RESULT_ITEM.format(n, c.search_name)
                           for (n, c) in matches.items())

    send(update, context, '{}\n\n{}\n{}'.format(messages.COURSE_SEARCH_RESULTS,
                                                matches_list,
                                                messages.COURSE_SEARCH_CHOOSE_RESULT))
    return SETUP_SEARCH_SELECT


def setup_search_again(update, context):
    return SETUP_SEARCH


def setup_step_search_select(update, context):
    ctx = conv_context[update.effective_chat.id]
    selected_num = int(update.message.text)
    if selected_num < 1 or selected_num > len(ctx['search_matches']):
        send(update, context, messages.INVALID_SELECTION)
        return SETUP_SEARCH_SELECT

    selected_course = ctx['search_matches'][selected_num]
    if not selected_course.is_supported():
        send(update, context, messages.COURSE_NOT_SUPPORTED.format(selected_course.not_supported_reason))
        return ConversationHandler.END

    ctx['course'] = selected_course
    ctx['settings'].course_id = selected_course.course_id
    send(update, context, messages.SELECT_YEAR)
    return SETUP_YEAR


def setup_step_year(update, context):
    ctx = conv_context[update.effective_chat.id]
    ctx['settings'].year = int(update.message.text)

    try:
        curricula = get_curricula(ctx['course'], ctx['settings'].year)
    except FetchError:
        send(update, context, messages.NO_CURRICULA_FOUND)
        return SETUP_YEAR
    except Exception as e:
        logging.exception(e)
        send(update, context, messages.FETCH_ERROR)
        return ConversationHandler.END

    if not curricula:
        send(update, context, messages.NO_CURRICULA_FOUND)
        return SETUP_YEAR

    curricula = dict(enumerate(curricula, start=1))
    curricula_list = ''.join(messages.CURRICULA_RESULT_ITEM.format(n, c['label'])
                             for (n, c) in curricula.items())
    ctx['curricula'] = curricula

    send(update, context, '{}\n\n{}\n{}'.format(
        messages.CURRICULA_RESULTS,
        curricula_list,
        messages.COURSE_SEARCH_CHOOSE_RESULT))
    return SETUP_CURRICULA_SELECT


def setup_step_year_invalid(update, context):
    send(update, context, messages.YEAR_NOT_VALID)
    return SETUP_YEAR


def setup_step_curricula_select(update, context):
    ctx = conv_context[update.effective_chat.id]
    selected_num = int(update.message.text)
    if selected_num < 1 or selected_num > len(ctx['curricula']):
        send(update, context, messages.INVALID_SELECTION)
        return SETUP_CURRICULA_SELECT

    selected_curricula = ctx['curricula'][selected_num]
    ctx['settings'].curricula = selected_curricula['value']

    ctx['user_repo'].update(ctx['user'])
    ctx['user_settings_repo'].update(ctx['settings'])

    ctx['user_repo'].close()
    ctx['user_settings_repo'].close()

    send(update, context, messages.SETUP_DONE)
    del conv_context[update.effective_chat.id]
    return ConversationHandler.END


def setup_step_cancel(update, context):
    send(update, context, messages.SETUP_STOPPED)
    return ConversationHandler.END


def send(update, context, text):
    context.bot.send_message(chat_id=update.message.chat_id, parse_mode=ParseMode.HTML, text=text)
