import time
from bulk_input_parser import parse_input_data
from driver import *
from youtube_parser import run_search_bulk
from youtube_video_analysis import run_BulkAnalysis
from excel_func import make_excel
from tqdm import tqdm

def run_channel_bulk(args):
    print("[Info] Run Bulk Analysis")
    period_date_start, period_date_end, output_path, dev_keys, channel_list = read_input(args.input_txt)
    bulk_analysis(period_date_start, period_date_end, output_path, dev_keys, channel_list)

def bulk_analysis(period_date_start, period_date_end, output_path, dev_keys, channel_list):
    df_output_data = []
    for channel in tqdm(channel_list):
        print("[Info] search bulk for " + channel)
        print("[Info] search for " + time.strftime('%Y-%m-%d', period_date_start) + " ~ " + time.strftime('%Y-%m-%d', period_date_end))

        thumbnails = run_search_bulk(driver, driver_video, channel, period_date_start)
        df_data = run_BulkAnalysis(dev_keys, period_date_start, period_date_end, thumbnails)
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
