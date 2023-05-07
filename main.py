import pandas as pd
import argparse
import os
from input_parser import parse_input_data
from driver import *
from youtube_parser import run_search, get_video_data

# parse argument
parser = argparse.ArgumentParser()
parser.add_argument('-input', type=str, dest="input_txt", action='store', default="input.txt", help='input text file')
args = parser.parse_args()

# version info
VERSION = 3.0
print("[Info] YoutubeParser V" + str(VERSION))

#input
input_text = args.input_txt
input_file = open(input_text, "r", encoding="UTF8")
input_data=input_file.readlines()
input_file.close()
input_keywords, period_date_start, period_date_end, output_path = parse_input_data(input_data)
print("[Info] Done reading input.txt")


def make_excel(df_datas, output_path):
    df_just_video = pd.DataFrame(df_datas)
    ext = os.path.splitext(output_path)[1]
    if ext == ".csv":
        df_just_video.to_csv(output_path, encoding='utf-8-sig', index=False)
    else:
        df_just_video.to_excel(output_path, encoding='utf-8-sig', index=False)

#start
df_output_data = []
for keyword in input_keywords:
    # print("[Info] search for " + period_date_start + "~" + period_date_end)
    thumbnails = run_search(driver, driver_video, keyword, period_date_start)
    df_data = get_video_data(driver, keyword, period_date_start, period_date_end, thumbnails)
    df_output_data += df_data
make_excel(df_output_data, output_path)

driver.quit()
driver_video.quit()

