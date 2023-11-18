import time

from typing import List, Tuple


def parse_input_data(input_data: List[str]) -> Tuple[List[str], time.struct_time, time.struct_time, str, List[str]]:
    dict_ = {}
    for line in input_data:
        key_value = line.strip().split("=")
        if len(key_value) == 2:
            dict_[key_value[0]] = key_value[1]

    input_keywords = list(dict_["KEYWORD"].split(","))
    period_date_start = time.strptime(dict_["PERIOD_DATE_START"], "%Y.%m.%d")
    period_date_end = time.strptime(dict_["PERIOD_DATE_END"], "%Y.%m.%d")
    output_path = dict_["OUTPUT"]
    dev_keys = list(dict_["DEV_KEY"].split(","))

    return input_keywords, period_date_start, period_date_end, output_path, dev_keys
