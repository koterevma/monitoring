import requests
import datetime
from pathlib import Path
from progress.bar import IncrementalBar
import json
from telebot import TeleBot
from telebot import types


# Храниться токен бота будет в файле на компьютере (по соображениям безопасности)
with open("private_data.json") as json_file:
    private_info = json.load(json_file)

token = private_info["bot_token"]
bot = TeleBot(token)

today_date = datetime.date.today().strftime("%d-%m-%y-")

chat_ids = Path("chat_ids.txt")
errors_path = Path(f"err_msg/{today_date}msg.txt")

# Лучше все константы вынести в отдельный файл
urls = {
    "webrobo": "http://webrobo.mgul.ac.ru:3000/",
    "dbrobo": "http://dbrobo.mgul.ac.ru/",
    "dokuwiki": "http://dokuwiki.mgul.ac.ru/dokuwiki/doku.php"
}

devices = [
    "01 РОСА%20К-2",
    "01 Роса-К-1",
    "schHome Тест%20Студии",
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
    "03 КЛОП_МН"
]

# Для терминала bash, можно будет потом избавиться от цветовых оформлений
class bcolors:
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def form_names(file):
    names = ["Date"]
    names.extend(list(urls.keys()))
    devnames = [i.replace('%20', ' ') for i in devices]
    names.extend(devnames)
    with open(file, 'w', encoding='utf-8') as outfile:
        print(';'.join(names), file=outfile)
    # print(';'.join(names))


if __name__ == "__main__":
    test_req = requests.get('http://google.com')
    if test_req.status_code != 200:
        print(f"{bcolors.FAIL}Error. No internet connection ({test_req.status_code}){bcolors.ENDC}")
    else:
        error_text = []
        # print(today_date)
        path_file_out = Path(f"data/{today_date}info.csv")
        if not path_file_out.is_file():
            print("Creating file \"info.csv\"")
            form_names(path_file_out)
            print("File created")
        print("Getting information about sites and devices")
        pr_bar = IncrementalBar("In progress", max=len(urls)+1)
        statuses = []
        for name, url in urls.items():
            req = requests.get(url)
            if req.status_code == 200:
                statuses.append('1')
            else:
                statuses.append('0')
                pr_bar.clearln()
                print(f"{bcolors.FAIL}Error with connection to {name}. Code: {req.status_code}{bcolors.ENDC}")
                error_text.append(f"Ошибка на сервере {name}. Код: {req.status_code}")
            pr_bar.next()

        dev_dict = dict([(i, '0') for i in devices])
        url = 'http://webrobo.mgul.ac.ru:3000/db_api_REST/not_calibr/last5min/'
        req = requests.get(url)
        if req.status_code != 200:
            pr_bar.clearln()
            print(f"{bcolors.FAIL}Error with connection to db_api_REST. Code: {req.status_code}{bcolors.ENDC}")
            error_text.append(f"Ошибка подключения к REST api. Код: {req.status_code}")
        else:
            data_in_json = json.loads(req.text)
            for record in data_in_json:
                nase = str(data_in_json[record]['serial']) + ' ' + str(data_in_json[record]['uName']).replace(' ', "%20")
                if nase in dev_dict.keys():
                    dev_dict[nase] = '1'
            pr_bar.next()

        pr_bar.finish()
        for nase, status in dev_dict.items():
            serial, uname = nase.split()
            if status == '0':
                pr_bar.clearln()
                print(f"{bcolors.WARNING}Warning. No data for {uname.replace('%20', ' ')} {serial} has found{bcolors.ENDC}")
        statuses.extend(dev_dict.values())
        
        with open(path_file_out, 'a', encoding='utf-8') as file:
            file.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:00") + ';')
            file.write(';'.join(statuses))
            file.write('\n')
            # print(file)
        
        if error_text != [] and not errors_path.is_file():
            with open(errors_path, 'w', encoding='utf-8') as opened_err_file:
                opened_err_file.writelines([l + '\n' for l in error_text]) # Можно немного доделать - проверять содержимое файла и если оно не совпадает с сообшением об ошибке - отправлять
            with open(chat_ids, 'r') as ids:
                for chat_id in ids:
                    try:
                        bot.send_message(chat_id, "\n".join(error_text))
                    except Exception as aerr:
                        print(aerr)
