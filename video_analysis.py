import time
from video_input_parser import parse_input_data
from driver import *
from youtube_parser import run_search, get_video_data
from youtube_video_analysis import run_VideoAnalysis
from excel_func import make_excel
from tqdm import tqdm

def run_video_analysis(args):
    print("[Info] Run Video Analysis")
    input_keywords, period_date_start, period_date_end, output_path, dev_keys = parse_input_data(args.input_txt)
    video_analysis(input_keywords, period_date_start, period_date_end, output_path, dev_keys)

def video_analysis(input_keywords, period_date_start, period_date_end, output_path, dev_keys):
    df_output_data = []
    for keyword in tqdm(input_keywords):
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
