import pandas as pd
import datetime
import docx.enum.text
from pathlib import Path
from docx import Document
from docx.shared import RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

from docx.oxml.ns import nsdecls
from docx.oxml import parse_xml


def main():
    today_date = datetime.date.today().strftime("%d-%m-%y-")
    path_file_in = Path(f"csv.csv")
    path_file_out = Path(f"data.docx")

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
    tables = list()
    shade_row = list()
    shade_col = list()

    tablecount = (len(dates)-1)/5
    if tablecount%1!=0: tablecount = int(tablecount)+1

    columns = 6
    if len(dates)<=5: columns=len(dates)

    for i in range(int(tablecount)):
        tables.append(doc.add_table(df.shape[1] + 1, columns))
        tables[i].cell(0,0).paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        trun = tables[i].cell(0,0).paragraphs[0].add_run('Дата')
        trun.font.bold=True
        brun = doc.add_paragraph().add_run()
        brun.add_break(docx.enum.text.WD_BREAK.PAGE)

    k = 0
    m = 0
    for i in range(len(tables)):
        for j in range(df.shape[1]):
            for l in range(int(tablecount)):shade_col.append(parse_xml(r'<w:shd {} w:fill="E6E6E6"/>'.format(nsdecls('w'))))
            tables[i].cell(j+1,0)._tc.get_or_add_tcPr().append(shade_col[m])
            paragraph = tables[i].cell(j + 1, 0).paragraphs[0]
            paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
            paragraph.add_run(df.columns[j]).font.bold = True
            m=m+1

        for j in range(columns-1):
            if(k+1>len(dates)-1):break
            for l in range(int(tablecount)):shade_row.append(parse_xml(r'<w:shd {} w:fill="E6E6E6"/>'.format(nsdecls('w'))))
            tables[i].cell(0,j+1)._tc.get_or_add_tcPr().append(shade_row[k])
            paragraph = tables[i].cell(0, j + 1).paragraphs[0]
            paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
            paragraph.add_run(dates[k].strftime("%H:%M:%S - ") + dates[k+1].strftime("%H:%M:%S")).font.bold = True
            k=k+1
    
    k = 0
    for i, list_of_vals in enumerate(values):
        k=int(i/(columns-1))
        for j, val in enumerate(list_of_vals):
            if val == 0:
                paragraph = tables[k].cell(j+1, (i%(columns-1)) + 1).paragraphs[0]
                paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
                run = paragraph.add_run('✖')
                run.font.color.rgb = RGBColor(255, 0, 0)
                run.font.bold = True

            elif val==1:
                paragraph = tables[k].cell(j+1, (i%(columns-1)) + 1).paragraphs[0]
                paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
                run = paragraph.add_run('✔')
                run.font.color.rgb = RGBColor(0, 200, 0)
                run.font.bold = True

    doc.save(path_file_out)

if __name__ == '__main__':
    main()
