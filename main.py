from selenium import webdriver as wd
from selenium.webdriver.chrome.service import Service
import pandas as pd
from bs4 import BeautifulSoup
import time
from datetime import datetime
import sys
from webdriver_manager.chrome import ChromeDriverManager
import re
import argparse
import os

# parse argument
parser = argparse.ArgumentParser()
parser.add_argument('-input', type=str, dest="input_txt", action='store', default="input.txt", help='input text file')
args = parser.parse_args()

# version info
VERSION = 2.3
print("[Info] YoutubeParser V" + str(VERSION))

# define environment
latest = "&sp=CAI%253D"
platform = "https://www.youtube.com"
webdriver_options = wd.ChromeOptions()
webdriver_options.add_argument("headless")
webdriver_options.add_argument("lang=ko")
driver = wd.Chrome(service=Service(ChromeDriverManager().install()), options=webdriver_options)
driver_video = wd.Chrome(service=Service(ChromeDriverManager().install()), options=webdriver_options)

SCROLL_PAUSE_SEC = 1

#input
input_text = args.input_txt
input_file = open(input_text, "r", encoding="UTF8")
input_data=input_file.readlines()
input_file.close()
print("[Info] Done reading input.txt")

dict = {}
for line in input_data:
    key_value = line.strip().split('=')
    if len(key_value)==2:
        dict[key_value[0]] = key_value[1]

input_keywords = list(dict["KEYWORD"].split(','))
period_date_start = time.strptime(dict["PERIOD_DATE_START"], "%Y.%m.%d")
period_date_end = time.strptime(dict["PERIOD_DATE_END"], "%Y.%m.%d")
output_path = dict["OUTPUT"]
exclude_channel = []


def run_search(keyword):
    print("[Info] Start to parse youtube information")
    print("[Info] search for " + dict["PERIOD_DATE_START"] + "~" + dict["PERIOD_DATE_END"])

    url = "https://www.youtube.com/results?search_query=" + keyword.replace(" ", "+") + latest
    print("[Info] search : " + url)
    driver.get(url)

    scroll_cnt=0

    date_video = period_date_start
    while True:
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        end = soup.select("#message")
        dates = soup.select("#metadata-line > span:nth-child(4)")
        #print(dates)

        if period_date_start > date_video:
            print("[Info] Meet the date. stop scroll!!! : ")
            break
        if scroll_cnt%5 == 0:
            try:
                last_video_url = "https://www.youtube.com" + soup.select("a#video-title")[-1].attrs["href"]
                driver_video.get(last_video_url)
                time.sleep(3)
                html_video = driver_video.page_source
                soup_video = BeautifulSoup(html_video, "html.parser")
                date_video_str = soup_video.select_one("#info-strings > yt-formatted-string")
                print("[Info] scroll")
                if date_video_str != None and len(date_video_str) > 0:
                    date_video_list = re.findall("\d+. \d+. \d+", date_video_str.get_text())
                    if len(date_video_list) > 0:
                        date_str = date_video_list[0]
                        date_video = time.strptime(date_str, "%Y. %m. %d")
                        print("[Info] current scroll date : " + date_str)
            except Exception as exception:
                print("[Warning] " + str(exception))
                continue
        driver.execute_script("window.scrollTo(0, document.getElementById('content').scrollHeight);")
        time.sleep(SCROLL_PAUSE_SEC)
        scroll_cnt+=1
    thumbnails = soup.select("a#video-title")
    return thumbnails

def get_video_data(keyword, thumbnails):
    df_data = [
        {
        '영상제목' :  "",
        '채널명' : "",
        'url' : "",
        '조회수' : "",
        '영상등록날짜' : "",
        '구독자 수' : "",
        '키워드' : ""
        }
    ]
    for thumbnail in reversed(thumbnails):
        link = "https://www.youtube.com" + thumbnail.attrs["href"]
        title = thumbnail.attrs["title"]
        date_str = ""
        print(title + ": " + link)

        driver.get(link)
        time.sleep(5)
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        date = soup.select_one("#info-strings > yt-formatted-string")

        channel = soup.select_one("#text > a")
        view = soup.select_one(
            "#count > ytd-video-view-count-renderer > span.short-view-count.style-scope.ytd-video-view-count-renderer")
        subscriber = soup.select_one("#owner-sub-count")

        if channel == None or view == None or date == None or subscriber == None or len(channel) <= 0 or len(view) <= 0 or len(date) <= 0 or len(subscriber) <= 0:
            print("[Warning] Some information is not parsed!!")
            continue

        date_video_list = re.findall("\d+. \d+. \d+", date.get_text())
        if len(date_video_list) > 0:
            date_str = date_video_list[0]
            date_video = time.strptime(date_str, "%Y. %m. %d")
            if period_date_start > date_video:
                continue
            if period_date_end < date_video:
                break

        new_data = {
            '영상제목' :  title,
            '채널명' : channel.get_text(),
            'url' : link,
            '조회수' : view.get_text(),
            '영상등록날짜' : date_str,
            '구독자 수' : subscriber.get_text(),
            '키워드' : keyword
        }
        df_data.append(new_data)

    return df_data

def make_excel(df_datas, output_path):
    df_just_video = pd.DataFrame(df_datas)
    ext = os.path.splitext(output_path)[1]
    if ext == ".csv":
        df_just_video.to_csv(output_path, encoding='utf-8-sig', index=False)
    else:
        df_just_video.to_excel(output_path, encoding='utf-8-sig', index=False)

#start
df_output_data = [
    {
        '영상제목' :  "",
        '채널명' : "",
        'url' : "",
        '조회수' : "",
        '영상등록날짜' : "",
        '구독자 수' : "",
        '키워드' : ""
    }
]
for keyword in input_keywords:
    thumbnails = run_search(keyword)
    df_data = get_video_data(keyword, thumbnails)
    df_output_data.extend(df_data)
make_excel(df_output_data, output_path)

driver.quit()
driver_video.quit()

