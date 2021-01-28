import pandas as pd
import datetime
from pathlib import Path
from docx import Document

def main():
    today_date = datetime.date.today().strftime("%d-%m-%y-")
    path_file_in = Path(f"data/{today_date}info.csv")
    path_file_out = Path(f"reports/{today_date}report.docx")

    with open(path_file_in, 'r') as file:
        df = pd.read_csv(file, delimiter=';')

    df = df.set_index('Date')
    df.index = pd.to_datetime(df.index)

    curr_row = df.iloc[0]
    dates = [ df.index[0] ]
    values = [ list(curr_row) ]
    for idx, row in df.iterrows():
        if list(curr_row) != list(row):
            dates.append(idx)
            curr_row = row
            values.append(list(row))
    dates.append(df.index[len(df.index) - 1])

    doc = Document()
    table = doc.add_table(df.shape[1] + 1, len(dates))
    table.cell(0, 0).text = 'Date'

    for i, col in enumerate(df.columns):
        table.cell(i + 1, 0).text = col
    print(dates)
    for i, date in enumerate(dates[:-1]):
        table.cell(0, i + 1).text = date.strftime("%H:%M:%S - ") + dates[i + 1].strftime("%H:%M:%S")
    
    for i, list_of_vals in enumerate(values):
        for j, val in enumerate(list_of_vals):
            table.cell(j + 1, i + 1).text = str(val)

    doc.save(path_file_out)

if __name__ == '__main__':
    main()