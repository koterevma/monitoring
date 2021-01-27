from datetime import datetime
from pathlib import Path
import json
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.header import Header
from email import encoders
import smtplib

addr_to   = ["zedix.ru@gmail.com", "mr.lux1@yandex.ru"]
addr_from = "makoterev@gmail.com"

# Хранение пароля от почты в открытом доступе - плохая идея
# По этому пароль будет храниться в локальном файле на компьютере
with open("private_data.json") as json_file:
    private_info = json.load(json_file)

password = private_info["email_pd"]
print(password)

today_date = datetime.today().strftime("%d-%m-%y-")
path_to_xl_file = Path(f"reports/{today_date}report.xlsx")
filename_xl = f"{today_date}report.xlsx"
path_to_csv_file = Path(f"data/{today_date}info.csv")
filename_csv = f"{today_date}info.csv"

msg = MIMEMultipart()
msg['From']    = addr_from
msg['To']      = ', '.join(addr_to)
msg['Subject'] = Header(f'Отчет практика {today_date[:-1]}', 'utf-8')

body = f"Отчет за {today_date[:-1]} число\nОтчет сформирован автоматически, пожалуйста, не отвечайте на него."
msg.attach(MIMEText(body, 'plain', 'utf-8'))

part = MIMEBase('application', "octet-stream")
part.set_payload(open(path_to_xl_file, "rb").read(), 'utf-8')
encoders.encode_base64(part)
part.add_header('Content-Disposition', f'attachment; filename="{filename_xl}"')
msg.attach(part)

part = MIMEBase('application', "octet-stream")
part.set_payload(open(path_to_csv_file, "rb").read(), 'utf-8')
encoders.encode_base64(part)
part.add_header('Content-Disposition', f'attachment; filename="{filename_csv}"')
msg.attach(part)

server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
server.set_debuglevel(False)  
server.login(addr_from, password)
server.send_message(msg)
server.quit()
# UyP2EOtjuo7
