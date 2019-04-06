# import telegram
# from telegram.ext import Updater
# from telegram.ext import CommandHandler
# from telegram.ext import MessageHandler, Filters
# from telegram.ext import InlineQueryHandler
# from telegram import InlineQueryResultArticle, InputTextMessageContent

import logging
import telegram
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler,
                          ConversationHandler)

from main import db_fill_form, create_user_dir


TOKEN = '898252052:AAFJiIhd9WQ9M7VLfSwAaqVg4KqkpLiXH5Q'

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                    level=logging.INFO)

logger = logging.getLogger(__name__)

LANG, PHOTO, ALT = range(3)


def start(update, context):
    reply_keyboard = [['DE', 'EN']]

    update.message.reply_text(
        'Hallo! Ich bin dein Payout-Bot. Bitte wähl eine Sprache.',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

    # create_user_dir(update.message.chat_id)

    return LANG


def language(update, context):
    # print("This is your context", context)

    user = update.message.from_user
    update.message.reply_text("{}".format(update.message.text), reply_markup=ReplyKeyboardRemove())
    if update.message.text == "DE":
        print("Going back to start")
        return ALT
    else:
        print("Going to photo")
        return PHOTO
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
    photo_file.download('user_photo.jpg')
    logger.info("Photo of %s: %s", user.first_name, 'user_photo.jpg')
    update.message.reply_text('Danke! Ich beantrage deine Erstattung.')


def unknown(update, context):
    print(update.message.chat_id)
    context.bot.send_message(chat_id=update.message.chat_id, text="Sorry, I didn't understand that command.")


def cancel(update, context):
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text('Bye! I hope we can talk again some day.',
                              reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


def _start(update, context):
    print("hi")
    return PHOTO


def main():

    bot = telegram.Bot(token=TOKEN)

    updater = Updater(token=TOKEN, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Add conversation handler with the states
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            LANG: [RegexHandler('^(DE|EN)$', language)],
            PHOTO: [MessageHandler(Filters.photo, photo)],
            ALT: [MessageHandler(Filters.text, _start)]
        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dp.add_handler(conv_handler)

    updater.start_polling()

    updater.idle()

    #
    # start_handler = CommandHandler('start', start)
    # dispatcher.add_handler(start_handler)
    #
    # # Should be added last
    # unknown_handler = MessageHandler(Filters.command, unknown)
    # dispatcher.add_handler(unknown_handler)
    # #
    # updater.start_polling()


if __name__ == '__main__':
    main()
