import requests
import datetime
from pathlib import Path
import os
from progress.bar import IncrementalBar
import json
from telebot import TeleBot
from telebot import types

import send_letter

# Right way to work with relative paths
working_directory = Path(__file__).parent

# Храниться токен бота будет в файле на компьютере (по соображениям безопасности)
with open(working_directory / "private_data.json") as json_file:
    private_info = json.load(json_file)

token = private_info["bot_token"]
bot = TeleBot(token)

today_date = datetime.date.today().strftime("%d-%m-%y-")

chat_ids = working_directory / "chat_ids.txt"
path_to_errors = working_directory / "err_msg"

errors_file = path_to_errors / f"{today_date}msg.txt"

# Лучше все константы вынести в отдельный файл
# Можно вынести все в json формат, в том числе сделать
# json с информацией об еденицах измерения всех датчиков
# (для построения графиков)
urls = {
    "webrobo": "http://webrobo.mgul.ac.ru:3000/",
    "dbrobo": "http://dbrobo.mgul.ac.ru/",
    "dokuwiki": "http://dokuwiki.mgul.ac.ru/dokuwiki/doku.php"
}

devices = [
    "01 РОСА%20К-2",
    "01 Роса-К-1",
    "schHome Тест%20Студии",
    "01 Опорный%20барометр",
    "schHome Тест%20воздуха",
    "01 Hydra-L",
    "02 Hydra-L",
    "03 Hydra-L",
    "04 Hydra-L",
    "05 Hydra-L",
    "06 Hydra-L",
    "07 Hydra-L",
    "08 Hydra-L",
    "01 Сервер%20СЕВ",
    "02 Сервер%20СЕВ",
    "03 Сервер%20СЕВ",
    "01 КЛОП_МН",
    "02 КЛОП_МН",
    "03 КЛОП_МН",
    "04 КЛОП_МН"
]


def send_error_message(errors):
    with open(errors_file, 'w', encoding='utf-8') as opened_err_file:
        # Можно немного доделать - проверять содержимое файла и если оно не совпадает с сообшением об ошибке - отправлять
        opened_err_file.writelines([l + '\n' for l in errors])
    print("Activating tg bot")
    with open(chat_ids, 'r', encoding='utf-8') as ids:
        for chat_id in ids:
            try:
                bot.send_message(chat_id, "\n".join(errors))
            except:
                pass
    print("Sending error message with email")
    msg = send_letter.form_message(
        ["zedix.ru@gmail.com", "sch-ru@yandex.ru"],
        f"Ошибки {today_date[:-1]}",
        "Только что, {}, в ходе работы скриптов, следящих за состоянием сайтов и приборов вуза были получены следующие ошибки:\n{}\n\nСообщение было создано и отправлено автоматически".format(datetime.datetime.today().strftime('%d.%m.%y %H:%M'), '\n'.join(errors))
    )
    print(msg)
    send_letter.send_letter(msg)


def form_names(file):
    names = ["Date"]
    names.extend(list(urls.keys()))
    devnames = [i.replace('%20', ' ') for i in devices]
    names.extend(devnames)
    with open(file, 'w', encoding='utf-8') as outfile:
        print(';'.join(names), file=outfile)
    # print(';'.join(names))


def handle_site_err(err_text, statuses, name, err):
    statuses.append('0')
    print(f"Error with connection to {name} ({err})")
    error_text.append(
        f"Ошибка подключения к сайту {name} ({err})")
    

def handle_dev_error(error_text, dev_dict, err):
    print(f"Error with connection to db_api_REST ({req.status_code})")
    error_text.append(
        f"Ошибка подключения к REST api ({req.status_code})")
    

if __name__ == "__main__":
    try:
        test_req = requests.get('http://google.com')
    except requests.exceptions.ConnectionError as e:
        print("Error. No internet connection (" + str(e) + ")")
    else:
        error_text = []
        # print(today_date)
        path_to_data = working_directory / "data"

        path_file_out = path_to_data / f"{today_date}info.csv"
        if not path_file_out.is_file():
            print("Creating file \"info.csv\"")
            form_names(path_file_out)
            print("File created")

        print("Getting information about sites and devices")
        pr_bar = IncrementalBar("In progress", max=len(urls)+1)
        statuses = []

        for name, url in urls.items():
            try:
                req = requests.get(url)
            except requests.exceptions.ConnectionError as e:
                pr_bar.clearln()
                handle_site_err(error_text, statuses, name, str(e))
            if req.status_code == 200:
                statuses.append('1')
            else:
                pr_bar.clearln()
                handle_site_err(error_text, statuses, name, str(req.status_code))
            pr_bar.next()

        dev_dict = dict([(i, '0') for i in devices])
        url = 'http://webrobo.mgul.ac.ru:3000/db_api_REST/not_calibr/last5min/'
        try:
            req = requests.get(url)
        except requests.exceptions.ConnectionError as e:
            handle_dev_error(error_text, dev_dict, str(e))
        if req.status_code != 200:
            pr_bar.clearln()
            handle_dev_error(error_text, dev_dict, str(req.status_code))
        else:
            data_in_json = json.loads(req.text)
            for record in data_in_json:
                nase = str(data_in_json[record]['serial']) + ' ' + \
                    str(data_in_json[record]['uName']).replace(' ', "%20")
                if nase in dev_dict.keys():
                    dev_dict[nase] = '1'

            pr_bar.next()

        pr_bar.finish()
        for nase, status in dev_dict.items():
            serial, uname = nase.split()
            if status == '0':
                pr_bar.clearln()
                print(
                    f"Warning. No data for {uname.replace('%20', ' ')} {serial} has found")
        statuses.extend(dev_dict.values())

        with open(path_file_out, 'a', encoding='utf-8') as file:
            file.write(datetime.datetime.now().strftime(
                "%Y-%m-%d %H:%M:00") + ';')
            file.write(';'.join(statuses))
            file.write('\n')

        # If some errors were spotted during check and if we didn't send
        if error_text != [] and not errors_file.is_file():
            print("Some errors were spotted during monitoring")
            send_error_message(error_text)
