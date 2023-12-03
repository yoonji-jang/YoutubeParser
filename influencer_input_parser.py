import time

from typing import List, Tuple

def parse_input_data(input_data: List[str]) -> Tuple[str, int, int, int, int, int, int, str, List[str]]:
    dict_ = {}
    for line in input_data:
        key_value = line.strip().split("=")
        if len(key_value) == 2:
            dict_[key_value[0]] = key_value[1]

    input_excel = dict_["INPUT_EXCEL"]
    influencer_sheet = int(dict_["INFLUENCER_SHEET"])
    video_sheet = int(dict_["VIDEO_SHEET"])
    start_row = int(dict_["START_ROW"])
    start_col = int(dict_["START_COL"])
    end_row = int(dict_["END_ROW"])
    max_result = int(dict_["MAX_RESULT"])
    output_excel = dict_["OUTPUT_EXCEL"]
    dev_keys = list(dict_["DEV_KEY"].split(","))

    return input_excel, influencer_sheet, video_sheet, start_row, start_col, end_row, max_result, output_excel, dev_keys

