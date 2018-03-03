#!/usr/bin/env python
# -*- coding: utf-8 -*-
import telebot
import sqlite3
from base import MessageTemlates


bot_token = ""
bot = telebot.TeleBot(bot_token)


def show_table(user):
    try:
        con = sqlite3.connect('Base.bd')
        cur = con.cursor()
        cur.execute("SELECT * FROM {USER}".format(USER=user))
        answer = ""
        for row in cur.fetchall():
            answer += "{NAME} {MONEY}\n".format(NAME=row[1], MONEY=str(row[2]))
        if answer == "":
            answer = MessageTemlates.EMPTY_BASE
        con.close()
        return answer
    except sqlite3.OperationalError:
        return MessageTemlates.SQL_SMTG_WRONG


def clear_name(user, name):
    con = sqlite3.connect('Base.bd')
    cur = con.cursor()
    cur.execute("DELETE FROM {USER} WHERE FULL_NAME = \"{NAME}\"".format(USER=user, NAME=name))
    con.commit()
    con.close()


def check_table(user):
    con = sqlite3.connect('Base.bd')
    cur = con.cursor()
    try:
        cur.execute("SELECT * FROM {USER}".format(USER=user))
    except sqlite3.OperationalError:
        cur.execute("CREATE TABLE {USER}"
                    "(id INTEGER PRIMARY KEY, FULL_NAME VARCHAR(100), CREDIT INTEGER)".format(USER=user))
        con.commit()
    con.close()


def add_entry_in_table(user, name, money):
    con = sqlite3.connect('Base.bd')
    cur = con.cursor()
    try:
        cur.execute("SELECT * FROM {USER} WHERE FULL_NAME =\"{NAME}\"".format(USER=user, NAME=name))
        if len(cur.fetchall()) == 0:
            cur.execute("INSERT INTO {USER} (FULL_NAME, CREDIT) VALUES( \"{NAME}\" , {MONEY})".format(USER=user,
                                                                                                      NAME=name,
                                                                                                      MONEY=money))
            con.commit()
        else:
            cur.execute("UPDATE {USER} SET CREDIT = CREDIT + {MONEY} WHERE FULL_NAME = \"{NAME}\"".format(USER=user,
                                                                                                          NAME=name,
                                                                                                          MONEY=money))
            con.commit()
        return MessageTemlates.ALRIGHT
    except sqlite3.OperationalError:
        return MessageTemlates.SQL_SMTG_WRONG
    finally:
        con.close()


@bot.message_handler(commands=['clear'])
def handle_clear(message):
    # TODO Чекать имя в базе
    buffer = message.text.split()
    try:
        clear_name(user=message.chat.username, name=buffer[1])
        bot.send_message(message.chat.id, MessageTemlates.CLEAR)
    except IndexError:
        bot.send_message(message.chat.id, MessageTemlates.ERROR_ELEMENT_COUNT)


@bot.message_handler(commands=['add'])
def handle_add(message):
    buffer = message.text.split()
    check_table(user=message.chat.username)
    try:
        bot.send_message(message.chat.id, add_entry_in_table(user=message.chat.username,
                                                             name=buffer[1],
                                                             money=str(buffer[2])))
    except IndexError:
        bot.send_message(message.chat.id, MessageTemlates.ERROR_ELEMENT_COUNT)


@bot.message_handler(commands=['help'])
def help_handle(message):
    bot.send_message(message.chat.id, MessageTemlates.HELP)


@bot.message_handler(commands=['show'])
def handle_text(message):
    bot.send_message(message.chat.id, show_table(user=message.chat.username))


bot.polling(none_stop=True, interval=0)
