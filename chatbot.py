#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This program is dedicated to the public domain under the CC0 license.
#
# THIS EXAMPLE HAS BEEN UPDATED TO WORK WITH THE BETA VERSION 12 OF PYTHON-TELEGRAM-BOT.
# If you're still using version 11.1.0, please see the examples at
# https://github.com/python-telegram-bot/python-telegram-bot/tree/v11.1.0/examples

"""
First, a few callback functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Example of a bot-user conversation using ConversationHandler.
Send /start to initiate the conversation.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging

from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler,
                          ConversationHandler)
from enum import Enum

import yaml

config = yaml.load(open("config.yaml"))
TOKEN = config["TOKEN"]
AZURE_KEY = config["AZURE_KEY"]

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

# GENDER, PHOTO, LOCATION, BIO = range(4)

class States(Enum):
    start = "start"
    ask_train_state = "ask_train_state"
    process_train_state = "process_train_state"

    request_delayed_train_ticket_photo = "request_delayed_train_ticket_photo"
    request_cancelled_train_ticket_photo = "request_cancelled_train_ticket_photo"

    ask_replacement_train = "ask_replacement_train"
    process_replacement_train = "process_replacement_train"
    request_replacement_train_ticket_photo = "request_replacement_train_ticket_photo"

    send_pdf = "send_pdf"




def start(update, context):
    # reply_keyboard = [['delayed', 'cancelled']]
    return States.ask_train_state


def ask_train_state(update, context):
    reply_keyboard = [['delayed', 'cancelled']]
    update.message.reply_text(
        'Hi! My name is delay bot and I will assist you with claiming your refund. '
        'Send cancel to stop talking to me.\n\n'
        'Did your train get delayed or was completely canceled?',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return States.process_train_state


def process_train_state(update, context):
    if update.message.text == "delayed":
        txt = "So your train was delayed. Please send me a screenshot of your mobile ticket."
        update.message.reply_text("{}".format(txt), reply_markup=ReplyKeyboardRemove())
        return States.request_delayed_train_ticket_photo
    elif update.message.text == "cancelled":
        txt = "So your train was cancelled. Please send me a screenshot of your mobile ticket."
        update.message.reply_text("{}".format(txt), reply_markup=ReplyKeyboardRemove())
        return States.request_cancelled_train_ticket_photo
    else:
        pass


def train_state_delayed(update, context):
    user = update.message.from_user
    update.message.reply_text("{}".format(update.message.text), reply_markup=ReplyKeyboardRemove())
    if update.message.text == "delayed":
        return States.request_delayed_train_ticket_photo
    elif update.message.text == "cancelled":
        return States.train_state_cancelled
    else:
        pass


def send_pdf(update, context):
    print("TODO: send pdf")
    pass

def cancel(update, context):
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text('Bye! I hope we can talk again some day.',
                              reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END

def request_delayed_train_ticket_photo(update, context):
    user = update.message.from_user
    photo_file = update.message.photo[-1].get_file()
    photo_file.download('user_photo.jpg')
    logger.info("Photo of %s: %s", user.first_name, 'user_photo.jpg')

    from src.src import extract_data_from_image, re_list
    form_data = extract_data_from_image("user_photo.jpg", re_list, AZURE_KEY)
    import json
    with open("user_data.json", "w") as f:
        json.dump(form_data, f)

    update.message.reply_text('Danke! Ich beantrage deine Erstattung.')

    send_pdf(update, context)
    return States.ask_train_state

def request_cancelled_train_ticket_photo(update, context):
    user = update.message.from_user
    photo_file = update.message.photo[-1].get_file()
    photo_file.download('user_photo.jpg')
    logger.info("Photo of %s: %s", user.first_name, 'user_photo.jpg')

    reply_keyboard = [['took different train', 'I cancelled my trip']]
    update.message.reply_text(
        'Did you take a different train instead of cancel your trip?',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return States.process_replacement_train

def process_replacement_train(update, context):
    if update.message.text == "took different train":
        txt = "Please send me a screenshot of your mobile ticket."
        update.message.reply_text("{}".format(txt), reply_markup=ReplyKeyboardRemove())
        return States.request_delayed_train_ticket_photo
    elif update.message.text == "I cancelled my trip":
        txt = "Ok. Ich sende dir das das aufgefüllte Formular."
        update.message.reply_text("{}".format(txt), reply_markup=ReplyKeyboardRemove())

        send_pdf(update, context)
        return States.ask_train_state
    else:
        pass

def request_replacement_train_ticket_photo(update, context):
    user = update.message.from_user
    photo_file = update.message.photo[-1].get_file()
    photo_file.download('user_photo.jpg')
    logger.info("Photo of %s: %s", user.first_name, 'user_photo.jpg')
    update.message.reply_text('Danke! Ich beantrage deine Erstattung.')

    send_pdf(update, context)

    return States.ask_train_state

def main():
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(TOKEN, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    conv_handler = ConversationHandler(
        entry_points=[RegexHandler("^(hi|hallo)", ask_train_state)],
        states={
            States.ask_train_state : [MessageHandler(Filters.text, ask_train_state)],
            States.process_train_state: [RegexHandler('^(delayed|cancelled)$', process_train_state)],
            States.request_delayed_train_ticket_photo :  [MessageHandler(Filters.photo, request_delayed_train_ticket_photo)],
            States.request_cancelled_train_ticket_photo : [MessageHandler(Filters.photo, request_cancelled_train_ticket_photo)],
            States.process_replacement_train : [RegexHandler('^(took different train|I cancelled my trip)$', process_replacement_train)],
            States.request_replacement_train_ticket_photo : [MessageHandler(Filters.photo, request_replacement_train_ticket_photo)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    dp.add_handler(conv_handler)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()