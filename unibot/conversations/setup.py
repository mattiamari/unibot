from telegram.ext import ConversationHandler, CommandHandler, MessageHandler, Filters
from telegram import ParseMode

import unibot.messages as messages
import unibot.users
import unibot.courses as courses
import unibot.uni_schedule as uni_schedule

SETUP_SEARCH, SETUP_SEARCH_SELECT, SETUP_YEAR, SETUP_CURRICULA_SELECT = range(0,4)
conv_context = {}
users = unibot.users.UserRepo
user_settings = unibot.users.UserSettingsRepo

def get_handler():
    return ConversationHandler(
        entry_points=[CommandHandler('setup', setup_step_start)],
        states={
            SETUP_SEARCH: [MessageHandler(Filters.text, setup_step_search)],
            SETUP_SEARCH_SELECT: [
                MessageHandler(Filters.regex('^\d+$'), setup_step_search_select),
                CommandHandler('cerca', setup_search_again)
            ],
            SETUP_YEAR: [
                MessageHandler(Filters.regex('^\d+$'), setup_step_year),
                MessageHandler(Filters.text, setup_step_year_invalid)
            ],
            SETUP_CURRICULA_SELECT: [
                MessageHandler(Filters.regex('^\d+$'), setup_step_curricula_select),
                CommandHandler('cerca', setup_search_again)
            ],
        },
        fallbacks=[CommandHandler('annulla', setup_step_cancel)]
    )

def setup_step_start(update, context):
    send(update, context, messages.SETUP_STEP_START)
    send(update, context, messages.SETUP_STEP_SEARCH)

    user = users().get(update.effective_user.id, update.effective_chat.id)
    if user is None:
        user = unibot.users.User(
            update.effective_user.id,
            update.effective_chat.id,
            update.effective_user.first_name,
            update.effective_user.last_name,
            update.effective_user.username
        )
    settings = unibot.users.UserSettings(
        update.effective_user.id,
        update.effective_chat.id,
        course_id='',
        year=1,
        curricula=''
    )
    conv_context[update.effective_chat.id] = {'user': user, 'settings': settings}

    return SETUP_SEARCH

def setup_step_search(update, context):
    if len(update.message.text) < 4:
        send(update, context, messages.QUERY_TOO_SMALL)
        return SETUP_SEARCH

    matches = courses.search(update.message.text)
    if len(matches) == 0:
        send(update, context, messages.COURSE_SEARCH_NO_RESULT)
        return SETUP_SEARCH

    matches = dict(enumerate(matches, start=1))
    conv_context[update.effective_chat.id]['search_matches'] = matches
    matches_list = ''.join(
        messages.COURSE_SEARCH_RESULT_ITEM.format(n, c['title']) for (n,c) in matches.items())

    send(update, context,
        '{}\n\n{}\n{}'.format(messages.COURSE_SEARCH_RESULTS, matches_list, messages.COURSE_SEARCH_CHOOSE_RESULT))

    return SETUP_SEARCH_SELECT

def setup_search_again(update, context):
    return SETUP_SEARCH

def setup_step_search_select(update, context):
    search_matches = conv_context[update.effective_chat.id]['search_matches']
    selected_num = int(update.message.text)
    if selected_num < 1 or selected_num > len(search_matches):
        send(update, context, messages.INVALID_SELECTION)
        return SETUP_SEARCH_SELECT

    selected_course = search_matches[selected_num]
    conv_context[update.effective_chat.id]['settings'].course_id = selected_course['id']
    send(update, context, messages.SELECT_YEAR)
    return SETUP_YEAR

def setup_step_year(update, context):
    conv_context[update.effective_chat.id]['settings'].year = int(update.message.text)

    curricula_url = courses.get_url_curricula(
        conv_context[update.effective_chat.id]['settings'].course_id,
        conv_context[update.effective_chat.id]['settings'].year)

    curricula = uni_schedule.curricula_from_source(curricula_url)
    if len(curricula) == 0:
        send(update, context, messages.NO_CURRICULA_FOUND)
        return SETUP_YEAR

    curricula = dict(enumerate(curricula, start=1))
    curricula_list = ''.join(messages.CURRICULA_RESULT_ITEM.format(n, c['label']) for (n,c) in curricula.items())
    conv_context[update.effective_chat.id]['curricula'] = curricula

    send(update, context, '{}\n\n{}\n{}'.format(
        messages.CURRICULA_RESULTS,
        curricula_list,
        messages.COURSE_SEARCH_CHOOSE_RESULT))
    return SETUP_CURRICULA_SELECT

def setup_step_year_invalid(update, context):
    send(update, context, messages.YEAR_NOT_VALID)
    return SETUP_YEAR

def setup_step_curricula_select(update, context):
    curricula = conv_context[update.effective_chat.id]['curricula']
    selected_num = int(update.message.text)
    if selected_num < 1 or selected_num > len(curricula):
        send(update, context, messages.INVALID_SELECTION)
        return SETUP_CURRICULA_SELECT

    selected_curricula = curricula[selected_num]
    conv_context[update.effective_chat.id]['settings'].curricula = selected_curricula['value']

    users().update(conv_context[update.effective_chat.id]['user'])
    user_settings().update(conv_context[update.effective_chat.id]['settings'])

    send(update, context, messages.SETUP_DONE)
    del conv_context[update.effective_chat.id]
    return ConversationHandler.END

def setup_step_cancel(update, context):
    send(update, context, messages.SETUP_STOPPED)
    return ConversationHandler.END

def send(update, context, text):
    context.bot.send_message(chat_id=update.message.chat_id, parse_mode=ParseMode.HTML, text=text)
