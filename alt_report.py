import pandas as pd
import datetime
from pathlib import Path
from docx import Document
from docx.shared import RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import nsdecls
from docx.oxml import parse_xml


def main():
    today_date = datetime.date.today().strftime("%d-%m-%y-")
    path_file_in = Path(f"data/{today_date}info.csv")
    path_file_out = Path(f"reports/{today_date}report.docx")

    with open(path_file_in, 'r', encoding="utf-8") as file:
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
    table.cell(0,0).paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    trun = table.cell(0,0).paragraphs[0].add_run('Дата')
    trun.font.bold=True
    
    shade_row = list()
    shade_col = list() 

    for i, col in enumerate(df.columns):
        shade_col.append(parse_xml(r'<w:shd {} w:fill="E6E6E6"/>'.format(nsdecls('w'))))
        table.cell(i+1,0)._tc.get_or_add_tcPr().append(shade_col[i])
        paragraph = table.cell(i + 1, 0).paragraphs[0]
        paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
        paragraph.add_run(col).font.bold = True

    for i, date in enumerate(dates[:-1]):
        shade_row.append(parse_xml(r'<w:shd {} w:fill="E6E6E6"/>'.format(nsdecls('w'))))
        table.cell(0,i+1)._tc.get_or_add_tcPr().append(shade_row[i])
        paragraph = table.cell(0, i + 1).paragraphs[0]
        paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
        paragraph.add_run(date.strftime("%H:%M:%S - ") + dates[i + 1].strftime("%H:%M:%S")).font.bold = True
    
    for i, list_of_vals in enumerate(values):
        for j, val in enumerate(list_of_vals):
            if val == 0:
                paragraph = table.cell(j + 1, i + 1).paragraphs[0]
                paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
                run = paragraph.add_run('✖')
                run.font.color.rgb = RGBColor(255, 0, 0)
                run.font.bold = True
            elif val==1:
                paragraph = table.cell(j + 1, i + 1).paragraphs[0]
                paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
                run = paragraph.add_run('✔')
                run.font.color.rgb = RGBColor(0, 200, 0)
                run.font.bold = True

    doc.save(path_file_out)


if __name__ == '__main__':
    main()
