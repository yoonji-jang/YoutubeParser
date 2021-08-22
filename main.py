from selenium import webdriver as wd
import pandas as pd
from bs4 import BeautifulSoup
import time
from datetime import datetime
import sys

# define environment
latest = "&sp=CAI%253D"
platform = "https://www.youtube.com"
webdriver_options = wd.ChromeOptions()
webdriver_options.add_argument("headless")
driver = wd.Chrome(executable_path=".\\chromedriver_win32\\chromedriver.exe", options=webdriver_options)
SCROLL_PAUSE_SEC = 1

#input
keyword = input("keyword : ")
start_month = input("start month : ")
end_month = input("end month : ")

exclude_channel = []
output_path = "./df_just_video.csv"
try:
    start_date = datetime.strptime(start_month, "%m")
    end_date = datetime.strptime(end_month, "%m")
except:
    sys.exit("date error!")


#start
period = datetime.now().month - start_date.month + 1
period_string = "%d"%period + "개월 전"
print(period_string)

url = "https://www.youtube.com/results?search_query=" + keyword.replace(" ", "+") + latest
print("search : " + url)
driver.get(url)


while True:
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")
    end = soup.select("#message")

    #TODO : add end condition!! ( no more contents)

    dates = soup.select("#metadata-line > span:nth-child(2)")
    print(dates)

    if period_string in "%s"%dates:
        print("find!!!" + period_string)
        break

    print("scroll")
    driver.execute_script("window.scrollTo(0, document.getElementById('content').scrollHeight);")
    time.sleep(SCROLL_PAUSE_SEC)


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
    date = soup.select_one("#info-strings > yt-formatted-string")

    channel = soup.select_one("#text > a")
    view = soup.select_one(
        "#count > ytd-video-view-count-renderer > span.short-view-count.style-scope.ytd-video-view-count-renderer")
    subscriber = soup.select_one("#owner-sub-count")

    if len(channel) <= 0 or len(view) <= 0 or len(date) <= 0 or len(subscriber) <= 0:
        print("some information is not parsed!!")
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


