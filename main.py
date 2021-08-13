from selenium import webdriver as wd
import pandas as pd
from bs4 import BeautifulSoup
import time

# define
latest = "&sp=CAI%253D"
platform = "https://www.youtube.com"

# filter
start_date = 0
end_date = 0
exclude_channel = []
output_path = "./data/df_just_video.csv"


def get_input():
    keyword = input("keyword : ")
    url = "https://www.youtube.com/results?search_query=" + keyword.replace(" ", "+") + latest
    print("search : " + url)

    webdriver_options = wd.ChromeOptions()
    webdriver_options.add_argument("headless")
    driver = wd.Chrome(executable_path=".\\chromedriver_win32\\chromedriver.exe", options=webdriver_options)
    driver.get(url)
    html = driver.page_source

    soup = BeautifulSoup(html, "html.parser")
    thumbnails = soup.select("a#video-title")

    df_title = []
    df_link = []
    df_channel = []
    df_view = []
    df_date = []
    df_subscriber = []

    for thumbnail in thumbnails:
        link = "https://www.youtube.com/" + thumbnail.attrs["href"]
        title = thumbnail.attrs["title"]
        print(title + ": " + link)

        driver.get(link)
        time.sleep(5)
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        channel = soup.select_one("#text > a")
        view = soup.select_one(
            "#count > ytd-video-view-count-renderer > span.short-view-count.style-scope.ytd-video-view-count-renderer")
        date = soup.select_one("#info-strings > yt-formatted-string")
        subscriber = soup.select_one("#owner-sub-count")

        if len(channel) <= 0 or len(view) <= 0 or len(date) <= 0 or len(subscriber) <= 0:
            print("some information is not parsed!!")
            continue

        print(channel.get_text())
        print(view.get_text())
        print(date.get_text())
        print(subscriber.get_text())

        df_title.append(title)
        df_link.append(link)
        df_channel.append(channel.get_text())
        df_view.append(view.get_text())
        df_date.append(date.get_text())
        df_subscriber.append(subscriber.get_text())

    df_just_video = pd.DataFrame(columns=['영상제목', '채널명', '영상url', '조회수', '영상등록날짜', '구독자 수'])

    df_just_video['영상제목'] = df_title
    df_just_video['채널명'] = df_channel
    df_just_video['영상url'] = df_link
    df_just_video['조회수'] = df_view
    df_just_video['영상등록날짜'] = df_date
    df_just_video['구독자 수'] = df_subscriber

    df_just_video.to_csv(output_path, encoding='utf-8-sig', index=False)
    driver.quit()


print("Start")
get_input()
