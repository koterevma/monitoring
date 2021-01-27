import pandas as pd
import datetime
from pathlib import Path


today_date = datetime.date.today().strftime("%d-%m-%y-")
path_file_in = Path(f"data/{today_date}info.csv")
path_file_out = Path(f"reports/{today_date}report.xlsx")

with open(path_file_in, 'r') as file:
    df = pd.read_csv(file, delimiter=';')

df = df.set_index('Date')
df.index = pd.to_datetime(df.index)
# pd.DataFrame().iloc(0).
curr_row = df.iloc[0]
print(df.index[0])
for idx, row in df.iterrows():
    if list(curr_row) != list(row):
        print(idx)
        curr_row = row
        pass
