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

import telegram
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler,
                          ConversationHandler)
from enum import Enum

from main import db_fill_form, create_user_dir, delete_user_dir
from utils import make_dir, get_json_data

import yaml
import os

config = yaml.load(open("config.yaml"))
TOKEN = config["TOKEN"]
AZURE_KEY = config["AZURE_KEY"]

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


class Global:
    USER_DIR = None

    CONV = get_json_data("conv.json")

    LANG = "DE"

    BOT = None


class States(Enum):
    start = "start"

    ask_lang_state = "ask_lang_state"
    process_lang_state = "process_lang_state"

    ask_service_state = "ask_service_state"

    ask_train_state = "ask_train_state"
    process_train_state = "process_train_state"

    request_delayed_train_ticket_photo = "request_delayed_train_ticket_photo"
    request_cancelled_train_ticket_photo = "request_cancelled_train_ticket_photo"

    ask_replacement_train = "ask_replacement_train"
    process_replacement_train = "process_replacement_train"
    request_replacement_train_ticket_photo = "request_replacement_train_ticket_photo"

    ask_payment_state = "ask_payment_state"

    send_pdf = "send_pdf"


def start(update, context):
    # reply_keyboard = [['delayed', 'cancelled']]

    return States.ask_train_state


def ask_lang_state(update, context):
    reply_keyboard = [['DE', 'EN']]
    update.message.reply_text(Global.CONV['LANG'],
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

    # Create user directory
    Global.USER_DIR = create_user_dir(update.message.chat_id)

    return States.ask_service_state


def process_lang_state(update, context):
    if update.message.text == "DE":
        Global.LANG = "DE"
    elif update.message.text == "EN":
        Global.LANG = "EN"

    return States.ask_service_state


def ask_service_state(update, context):
    reply_keyboard = [['Deutsche Bahn', 'FlixBus']]
    update.message.reply_text(Global.CONV[Global.LANG]['ask_service_state'],
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

    # Create user directory
    # Global.USER_DIR = create_user_dir(update.message.chat_id)

    return States.ask_train_state


def ask_train_state(update, context):
    reply_keyboard = [['verspätet', 'storniert']]
    update.message.reply_text(Global.CONV[Global.LANG]['ask_train_state'],
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

    # Create user directory
    # Global.USER_DIR = create_user_dir(update.message.chat_id)

    return States.process_train_state


def process_train_state(update, context):
    if update.message.text == "verspätet":
        # txt = "So your train was delayed. Please send me a screenshot of your mobile ticket."
        update.message.reply_text(Global.CONV[Global.LANG]['process_train_state']['verspätet'], reply_markup=ReplyKeyboardRemove())
        return States.request_delayed_train_ticket_photo
    elif update.message.text == "storniert":
        # txt = "So your train was cancelled. Please send me a screenshot of your mobile ticket."
        update.message.reply_text(Global.CONV[Global.LANG]['process_train_state']['storniert'], reply_markup=ReplyKeyboardRemove())
        return States.request_cancelled_train_ticket_photo
    else:
        pass


def train_state_delayed(update, context):
    user = update.message.from_user
    update.message.reply_text("{}".format(update.message.text), reply_markup=ReplyKeyboardRemove())
    if update.message.text == "verspätet":
        return States.request_delayed_train_ticket_photo
    elif update.message.text == "storniert":
        return States.train_state_cancelled
    else:
        pass


def ask_payment_state(update, context):
    reply_keyboard = [['PayPal', 'Bank Überweisung']]
    update.message.reply_text(Global.CONV[Global.LANG]['ask_payment_state'],
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

    update.message.reply_text(Global.CONV[Global.LANG]['send_pdf']['success'])

    return States.ask_train_state


def send_pdf(update, context, data):

    pdf = db_fill_form(Global.USER_DIR, data)

    if pdf:
        update.message.reply_text('Super! Deine Daten wurde übermittelt.')
        Global.BOT.send_document(chat_id=update.message.chat_id, document=open(pdf, 'rb'))
    else:
        update.message.reply_text('Entschuldigung, es ist leider ein Fehler aufgetreten mit der Datei.')


def cancel(update, context):
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text(Global.CONV[Global.LANG]['cancel'],
                              reply_markup=ReplyKeyboardRemove())

    delete_user_dir(update.message.chat_id)

    return ConversationHandler.END


def request_delayed_train_ticket_photo(update, context):
    user = update.message.from_user
    photo_file = update.message.photo[-1].get_file()
    ticket_path = os.path.join(Global.USER_DIR, "ticket.jpg")
    photo_file.download(ticket_path)
    logger.info("Photo of %s: %s", user.first_name, ticket_path)

    from src.src import extract_data_from_image, re_list
    # Get ocr data in JSON
    form_data = extract_data_from_image(ticket_path, re_list, AZURE_KEY)
    import json
    ticket_ocr_path = os.path.join(Global.USER_DIR, "ticket_ocr.json")
    with open(ticket_ocr_path, "w") as f:
        json.dump(form_data, f)

    update.message.reply_text(Global.CONV[Global.LANG]['processing_photo'])

    send_pdf(update, context, form_data)
    return States.ask_train_state


def request_cancelled_train_ticket_photo(update, context):
    user = update.message.from_user
    photo_file = update.message.photo[-1].get_file()
    ticket_path = os.path.join(Global.USER_DIR, "ticket.jpg")
    photo_file.download(ticket_path)
    logger.info("Photo of %s: %s", user.first_name, ticket_path)

    reply_keyboard = [['Ich habe einen anderen Zug genommen', 'Ich habe meine Reise storniert']]
    update.message.reply_text(Global.CONV[Global.LANG]['trip_question_1'],
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return States.process_replacement_train


def process_replacement_train(update, context):
    if update.message.text == "Ich habe einen anderen Zug genommen":
        txt = "Please send me a screenshot of your mobile ticket."
        update.message.reply_text("{}".format(txt), reply_markup=ReplyKeyboardRemove())
        return States.request_delayed_train_ticket_photo
    elif update.message.text == "Ich habe meine Reise storniert":
        txt = "Ok. Ich sende dir das aufgefüllte Formular."
        update.message.reply_text("{}".format(txt), reply_markup=ReplyKeyboardRemove())

        form_data = "" # TODO
        send_pdf(update, context, form_data)
        return States.ask_train_state
    else:
        pass


def request_replacement_train_ticket_photo(update, context):
    user = update.message.from_user
    photo_file = update.message.photo[-1].get_file()
    ticket_path = os.path.join(Global.USER_DIR, "ticket.jpg")
    photo_file.download(ticket_path)
    logger.info("Photo of %s: %s", user.first_name, ticket_path)
    update.message.reply_text(Global.CONV[Global.LANG]['processing_photo'])

    form_data = ""  # TODO
    send_pdf(update, context, form_data)

    return States.ask_train_state


def clean_data_dir():
    data_dir = os.path.join(os.getcwd(), os.pardir, "data")
    users_dir = os.path.join(data_dir, "users")

    if os.path.isdir(users_dir):
        user_dirs = [os.path.join(users_dir, d) for d in os.listdir(users_dir)]

        for d in user_dirs:
            delete_user_dir(d)

    make_dir(data_dir)
    make_dir(users_dir)


def main():
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    Global.BOT = telegram.Bot(token=TOKEN)

    updater = Updater(TOKEN, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    conv_handler = ConversationHandler(
        entry_points=[RegexHandler("^([Hh]i|[Hh]allo)|start", ask_lang_state)],
        states={
            States.ask_lang_state : [MessageHandler(Filters.text, ask_lang_state)],
            # States.process_lang_state : [MessageHandler(Filters.text, process_lang_state)],
            States.ask_service_state : [MessageHandler(Filters.text, ask_service_state)],
            States.ask_train_state : [MessageHandler(Filters.text, ask_train_state)],
            States.process_train_state: [RegexHandler('^(verspätet|storniert)$', process_train_state)],
            States.request_delayed_train_ticket_photo :  [MessageHandler(Filters.photo, request_delayed_train_ticket_photo)],
            States.request_cancelled_train_ticket_photo : [MessageHandler(Filters.photo, request_cancelled_train_ticket_photo)],
            States.process_replacement_train : [RegexHandler('^(Ich habe einen anderen Zug genommen|Ich habe meine Reise storniert)$', process_replacement_train)],
            States.request_replacement_train_ticket_photo : [MessageHandler(Filters.photo, request_replacement_train_ticket_photo)]
            # States.ask_payment_state : [MessageHandler(Filters.text, ask_payment_state)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    dp.add_handler(conv_handler)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    # clean_data_dir()
    main()
