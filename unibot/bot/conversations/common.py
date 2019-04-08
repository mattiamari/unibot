from telegram.ext import ConversationHandler
from telegram import ParseMode
from unibot.bot import messages


def step_cancel(update, context):
    send(update, context, messages.CANCELED)
    return ConversationHandler.END


def send(update, context, text):
    context.bot.send_message(chat_id=update.message.chat_id,
                             parse_mode=ParseMode.HTML, text=text)
