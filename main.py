from selenium import webdriver as wd
from selenium.webdriver.chrome.service import Service
import pandas as pd
from bs4 import BeautifulSoup
import time
from datetime import datetime
import sys
from webdriver_manager.chrome import ChromeDriverManager
import re


# version info
VERSION = 2.1
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
input_file = open(".\input.txt", "r", encoding="UTF8")
input_data=input_file.readlines()
input_file.close()
print("[Info] Done reading input.txt")

dict = {}
for line in input_data:
    key_value = line.strip().split('=')
    if len(key_value)==2:
        dict[key_value[0]] = key_value[1]

keyword = dict["KEYWORD"]
period_string = dict["PERIOD_STRING"]
period_date = time.strptime(dict["PERIOD_DATE"], "%Y.%m.%d")
output_path = dict["OUTPUT"]
exclude_channel = []

#start
print("[Info] Start to parse youtube information")
print("[Info] search for " + period_string)

url = "https://www.youtube.com/results?search_query=" + keyword.replace(" ", "+") + latest
print("[Info] search : " + url)
driver.get(url)

scroll_cnt=0

date_video = period_date
while True:
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")
    end = soup.select("#message")
    dates = soup.select("#metadata-line > span:nth-child(4)")
    #print(dates)

    if period_string in "%s"%dates:
        print("[Info] find!!!" + period_string)
        break
    if period_date > date_video:
        print("[Info] Meet the date. stop scroll!!! : ")
        break
    if scroll_cnt%10==0:
        last_video_url = "https://www.youtube.com" + soup.select("a#video-title")[-1].attrs["href"]
        driver_video.get(last_video_url)
        time.sleep(3)
        html_video = driver_video.page_source
        soup_video = BeautifulSoup(html_video, "html.parser")
        date_video_str = soup_video.select_one("#info-strings > yt-formatted-string")
        print("[Info] scroll")
        if date_video_str != None and len(date_video_str) > 0:
            date_video = time.strptime(date_video_str.get_text(), "%Y. %m. %d.")
            print("[Info] current date : " + date_video_str.get_text())
    driver.execute_script("window.scrollTo(0, document.getElementById('content').scrollHeight);")
    time.sleep(SCROLL_PAUSE_SEC)
    scroll_cnt+=1


thumbnails = soup.select("a#video-title")

df_title = []
df_link = []
df_channel = []
df_view = []
df_date = []
df_subscriber = []

for thumbnail in thumbnails:
    link = "https://www.youtube.com" + thumbnail.attrs["href"]
    title = thumbnail.attrs["title"]
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

#    print(channel.get_text())
#    print(view.get_text())
#    print(date.get_text())
#    print(subscriber.get_text())

    df_title.append(title)
    df_link.append(link)
    df_channel.append(channel.get_text())
    df_view.append(view.get_text())
    df_date.append(date.get_text())
    df_subscriber.append(subscriber.get_text())

df_just_video = pd.DataFrame(columns=['영상제목', '채널명', 'url', '조회수', '영상등록날짜', '구독자 수'])

df_just_video['영상제목'] = df_title
df_just_video['채널명'] = df_channel
df_just_video['url'] = df_link
df_just_video['조회수'] = df_view
df_just_video['영상등록날짜'] = df_date
df_just_video['구독자 수'] = df_subscriber

df_just_video.to_csv(output_path, encoding='utf-8-sig', index=False)

driver.quit()
driver_video.quit()

