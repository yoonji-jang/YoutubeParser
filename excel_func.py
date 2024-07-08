import pandas as pd
import os
from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.styles import Font

# make output
def make_excel(df_datas, output_path):
    wb = Workbook()
    ws = wb.active
    df_just_video = pd.DataFrame(df_datas)
    ext = os.path.splitext(output_path)[1]
    if ext == ".csv":
        df_just_video.to_csv(output_path, encoding='utf-8-sig', index=False)
        df_xl = pd.read_csv(output_path)
    else:
        df_just_video.to_excel(output_path, encoding='utf-8-sig', index=False)
        df_xl = pd.read_excel(output_path)

    for row in dataframe_to_rows(df_xl, index=False, header=True):
        ws.append(row)
    for row in ws.iter_rows(min_row=2, max_col=len(df_xl.columns), max_row=len(df_xl) + 1):
        for cell in row:
            if "http" in str(cell.value):
                cell.font = Font(underline="single", color="0563C1")
                cell.hyperlink = cell.value
    wb.save(output_path)
    print("[Info] Saved Output Excel : " + output_path)
