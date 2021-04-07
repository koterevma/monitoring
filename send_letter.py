from datetime import datetime
from pathlib import Path
import json
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.header import Header
from email import encoders
import smtplib

addr_from = "makoterev@gmail.com"

# Хранение пароля от почты в открытом доступе - плохая идея
# По этому пароль будет храниться в локальном файле на компьютере

working_directory = Path(__file__).parent

with open(working_directory / "private_data.json") as json_file:
    private_info = json.load(json_file)

password = private_info["email_pd"]


def send_letter(msg):
    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.set_debuglevel(False)
    server.login(addr_from, password)
    server.send_message(msg)
    server.quit()


def form_message(to, subject, text):
    msg = MIMEMultipart()
    msg['From'] = addr_from
    msg['To'] = ', '.join(to)
    msg['Subject'] = Header(subject, 'utf-8')

    body = text
    msg.attach(MIMEText(body, 'plain', 'utf-8'))
    return msg


def main():
    addr_to = ["zedix.ru@gmail.com", "mr.lux1@yandex.ru", "JLoGuk@mail.ru"]

    today_date = datetime.today().strftime("%d-%m-%y-")
    path_to_xl_file = working_directory / f"reports/{today_date}report.docx"
    filename_docx = f"{today_date}report.docx"
    path_to_csv_file = working_directory / f"data/{today_date}info.csv"
    filename_csv = f"{today_date}info.csv"

    msg = form_message(
        addr_to,
        f'Отчет практика {today_date[:-1]}',
        f"Отчет за {today_date[:-1]} число\nОтчет сформирован автоматически, пожалуйста, не отвечайте на него."
    )

    part = MIMEBase('application', "octet-stream")
    part.set_payload(open(path_to_xl_file, "rb").read(), 'utf-8')
    encoders.encode_base64(part)
    part.add_header('Content-Disposition',
                    f'attachment; filename="{filename_docx}"')
    msg.attach(part)

    part = MIMEBase('application', "octet-stream")
    part.set_payload(open(path_to_csv_file, "rb").read(), 'utf-8')
    encoders.encode_base64(part)
    part.add_header('Content-Disposition',
                    f'attachment; filename="{filename_csv}"')
    msg.attach(part)

    send_letter(msg)


if __name__ == '__main__':
    main()
