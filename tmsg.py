#!/usr/bin/env python3
from telebot import TeleBot
from telebot import types
import json
from pathlib import Path

working_directory = Path(__file__).parent

with open(working_directory / "private_data.json") as json_file:
    private_info = json.load(json_file)

token = private_info["bot_token"]
bot = TeleBot(token)
# Вывести бы это в базу данных
in_file = working_directory / "chat_ids.txt"

repl = types.InlineKeyboardMarkup()
key_yes = types.InlineKeyboardButton(text='Да', callback_data='yes')
key_no = types.InlineKeyboardButton(text='Нет', callback_data='no')
repl.add(key_yes)
repl.add(key_no)


@bot.message_handler(commands=['start', 'help'])
def handle_start_help(message):
    if message.text == "/help":
        try:
            bot.send_message(
                message.from_user.id, "Простой бот, который напишет, если на сервере произошла ошибка.\nБот работает с 8 утра до 16:00\nНапиши мне что-нибудь, либо пиши /start")
        except Exception:
            pass
    if message.text == "/start":
        try:
            bot.send_message(
                message.from_user.id,
                "Привет! Если что-то не понятно, пиши /help\nХочешь получать уведомления от меня, когда серваки вуза падают?)",
                reply_markup=repl
            )
        except Exception:
            pass


@bot.message_handler(content_types=['text'])
def text_from_user(message):
    try:
        bot.send_message(
            message.from_user.id,
            "Привет! Если что-то не понятно, пиши /help\nХочешь получать уведомления от меня, когда серваки вуза падают?)",
            reply_markup=repl
        )
    except Exception:
        pass


@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    if call.data == "yes":
        alr_ex = False
        with open(in_file, "r+") as file:
            for line in file:
                # print(line[:-1], call.message.chat.id)
                if line[:-1] == str(call.message.chat.id):
                    alr_ex = True
            if alr_ex:
                try:
                    bot.send_message(
                        call.message.chat.id,
                        "Твое имя уже есть в моем списке"
                    )
                except Exception:
                    pass
            else:
                print(call.message.chat.id, file=file)
                try:
                    bot.send_message(
                        call.message.chat.id,
                        "Я записал твое имя в список, но пока только карандашом . . ."
                    )
                except Exception:
                    pass
    elif call.data == "no":
        removed = False
        with open(in_file, "r+") as file:
            lines = file.readlines()
            file.seek(0)
            for line in lines:
                if line[:-1] == str(call.message.chat.id):
                    removed = True
                else:
                    file.write(line)
            file.truncate()
            if removed:
                try:
                    bot.send_message(
                        call.message.chat.id,
                        "Хорошо, я стер твое имя из списка"
                    )
                except Exception:
                    pass
            else:
                try:
                    bot.send_message(
                        call.message.chat.id,
                        "Странно, тебя и так нет в списке . . ."
                    )
                except Exception:
                    pass


if __name__ == "__main__":
    print("Bot started")
    bot.polling(interval=1)
