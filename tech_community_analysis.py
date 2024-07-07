import time
from tech_community_input_parser import parse_input_data
from driver import *
from tech_community_parser import run_search
from tech_community_post_analysis import run_TechCommunityAnalysis
from excel_func import make_excel
from tqdm import tqdm

def run_tech_community_analysis(args):
    print("[Info] Run Tech Community Analysis")
    input_keywords, community_list, period_date_start, period_date_end, output_path = parse_input_data(args.input_txt)
    tech_community_analysis(input_keywords, community_list, period_date_start, period_date_end, output_path)

def tech_community_analysis(input_keywords, community_list, period_date_start, period_date_end, output_path):
    df_output_data = []
    for community in tqdm(community_list):
        print("[Info] search community : " + community)
        print("[Info] search for " + time.strftime('%Y-%m-%d', period_date_start) + " ~ " + time.strftime('%Y-%m-%d', period_date_end))
        for keyword in tqdm(input_keywords):
            print("[Info] keyword : " + keyword)

            url_data_list = run_search(driver, keyword, period_date_start, community)
            df_data = run_TechCommunityAnalysis(driver, keyword, url_data_list, community)
            df_output_data += df_data
    try:
        make_excel(df_output_data, output_path)
    except Exception as exception:
        print("[Err] making excel: " + str(exception))

    print("[Info] Done")
    driver.quit()
    driver_video.quit()
