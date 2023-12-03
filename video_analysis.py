import time
import pandas as pd
import os
from video_input_parser import parse_input_data
from driver import *
from youtube_parser import run_search, get_video_data
from youtube_video_analysis import run_VideoAnalysis
from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.styles import Font
import re

def run_video_analysis(args):
    print("[Info] Run Video Analysis")
    input_keywords, period_date_start, period_date_end, output_path, dev_keys = read_input(args.input_txt)
    video_analysis(input_keywords, period_date_start, period_date_end, output_path, dev_keys)

def video_analysis(input_keywords, period_date_start, period_date_end, output_path, dev_keys):
    df_output_data = []
    for keyword in input_keywords:
        print("[Info] search for " + keyword)
        print("[Info] search for " + time.strftime('%Y-%m-%d', period_date_start) + " ~ " + time.strftime('%Y-%m-%d', period_date_end))

        thumbnails = run_search(driver, driver_video, keyword, period_date_start)
        # df_data = get_video_data(driver, keyword, period_date_start, period_date_end, thumbnails)
        df_data = run_VideoAnalysis(keyword, dev_keys, period_date_start, period_date_end, thumbnails)
        df_output_data += df_data
    try:
        make_excel(df_output_data, output_path)
    except Exception as exception:
        print("[Err] making excel: " + str(exception))

    print("[Info] Done")
    driver.quit()
    driver_video.quit()

# read input
def read_input(input_text):
    input_file = open(input_text, "r", encoding="UTF8")
    input_data=input_file.readlines()
    input_file.close()
    print("[Info] Done reading : " + input_text)
    return parse_input_data(input_data)

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
