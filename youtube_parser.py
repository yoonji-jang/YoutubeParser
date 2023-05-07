from bs4 import BeautifulSoup
import time
import re

SCROLL_PAUSE_SEC = 1
# define environment
latest = "&sp=CAI%253D"
platform = "https://www.youtube.com"

# search keyword in youtube in input period
def run_search(driver, driver_video, keyword, period_date_start):
    print("[Info] Start to parse youtube information")

    url = "https://www.youtube.com/results?search_query=" + keyword.replace(" ", "+") + latest
    print("[Info] search : " + url)
    driver.get(url)

    scroll_cnt = 0

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

def get_video_data(driver, keyword, period_date_start, period_date_end, thumbnails):
    df_data = []
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

        if date == None or len(date) <= 0:
            print("[Warning] Date information is not parsed!!")
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
            '채널명' : channel.get_text() if channel else "",
            'url' : link,
            '조회수' : view.get_text() if view else "",
            '영상등록날짜' : time.strftime('%Y.%m.%d', date_video),
            '구독자 수' : subscriber.get_text() if subscriber else "",
            '키워드' : keyword
        }
        df_data.append(new_data)

    return df_data