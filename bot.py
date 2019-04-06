import os
import logging
import telegram
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler,
                          ConversationHandler)

from main import db_fill_form, create_user_dir, delete_user_dir
from utils import load_telegram_token
from enum import Enum


TOKEN = load_telegram_token()

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                    level=logging.INFO)

logger = logging.getLogger(__name__)


class Global:
    USER_DIR = None


class States(Enum):
    LANG = 1
    LANG_DEC = 2
    LANG_DEC_EN = 3
    PHOTO = 4
    PHOTO_DEC = 5


def start(update, context):
    reply_keyboard = [['DE', 'EN']]

    update.message.reply_text(
        'Hallo! Ich bin dein Payout-Bot. Bitte wähl eine Sprache.',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

    print(Global.USER_DIR)
    print(update.message.chat_id)
    Global.USER_DIR = create_user_dir(update.message.chat_id)
    print(Global.USER_DIR)

    return States.LANG


def request_photo(update, context):
    if update.message.text == "DE":
        update.message.reply_text("Please update a photo.")
        return States.PHOTO
    elif update.message.text == "EN":
        print("English")
        return States.PHOTO
    else:
        update.message.reply_text("Sorry, I don't support that language.")


def language(update, context):

    # reply_keyboard = [['DE', 'EN']]
    #
    # update.message.reply_text(
    #     'Hallo! Ich bin dein Payout-Bot. Bitte wähl eine Sprache.',
    #     reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    # print("This is your context", context)

    user = update.message.from_user
    update.message.reply_text("{}".format(update.message.text), reply_markup=ReplyKeyboardRemove())

    return States.PHOTO
    # logger.info("Language of %s: %s", user.first_name, update.message.text)
    # update.message.reply_text('Super! Bitte lad ein Screenshot von deinem Ticket hoch'
    #                           'damit ich deine Erstattung beantragen kann.',
    #                           reply_markup=ReplyKeyboardRemove())
    #
    # print(update.message.text)
    # print(type(update.message.text))


def photo(update, context):
    user = update.message.from_user
    photo_file = update.message.photo[-1].get_file()
    print(Global.USER_DIR)
    ticket_path = os.path.join(Global.USER_DIR, "ticket.jpg")
    photo_file.download(ticket_path)
    logger.info("Photo of %s: %s", user.first_name, '{}'.format(str(ticket_path)))
    update.message.reply_text('Danke! Ich beantrage deine Erstattung.')


def unknown(update, context):
    print(update.message.chat_id)
    context.bot.send_message(chat_id=update.message.chat_id, text="Sorry, I didn't understand that command.")


def cancel(update, context):
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text('Bye! I hope we can talk again some day.',
                              reply_markup=ReplyKeyboardRemove())

    delete_user_dir(update.message.chat_id)

    return ConversationHandler.END


def _start(update, context):
    print("hi")
    return States.PHOTO


def main():

    # bot = telegram.Bot(token=TOKEN)

    updater = Updater(token=TOKEN, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Add conversation handler with the states
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            States.LANG: [RegexHandler('^(DE|EN)$', request_photo)],
            States.PHOTO: [MessageHandler(Filters.photo, photo)],
            States.PHOTO_DEC: [MessageHandler(Filters.text, _start)]
        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dp.add_handler(conv_handler)

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
