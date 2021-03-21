import pandas as pd
import datetime
from pathlib import Path
import openpyxl
from openpyxl.utils import get_column_letter
from openpyxl.styles import PatternFill

today_date = datetime.date.today().strftime("%d-%m-%y-")
path_file_in = Path(f"data/{today_date}info.csv")
path_file_out = Path(f"reports/{today_date}report.xlsx")

with open(path_file_in, 'r') as file:
    df = pd.read_csv(file, delimiter=';')

df = df.set_index('Date')
df.index = pd.to_datetime(df.index)
# print(df.index)
# print(df)

df.to_excel(path_file_out)

wb = openpyxl.load_workbook(path_file_out)

sheet = wb["Sheet1"]
# sheet["A1"].number_format = 'h:mm:ss'
for i in range(len(df.index)):
    sheet["A{}".format(i + 2)].number_format = "hh:mm:ss"

for i in range(len(df.keys())):
    sheet.column_dimensions[get_column_letter(i + 2)].width = len(str(sheet[get_column_letter(i + 2) + '1'].value)) + 2

redFill = PatternFill(start_color='FFFF0000',
                      end_color='FFFF0000',
                      fill_type='solid')
for row in sheet.rows:
    for cell in row:
        if cell.value == 0:
            cell.fill = redFill

wb.save(path_file_out)
wb.close()
