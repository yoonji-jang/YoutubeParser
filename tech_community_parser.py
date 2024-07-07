from bs4 import BeautifulSoup
import time
import re
from urllib.parse import urljoin

SCROLL_PAUSE_SEC = 1
# define environment
platform_list = [
    {"name": "quasarzone", "url": "https://quasarzone.com/groupSearches?kind=subject%7C%7Ccontent&keyword=", "page": "&page="},
    {"name": "coolenjoy", "url": "https://coolenjoy.net/bbs/search4.php?ot=&onetable=&sfl=wr_subject%7C%7Cwr_content&sop=and&stx=", "page": "&page="}
]

def get_platform(platform_name):
    for platform in platform_list:
        if platform['name'] == platform_name:
            return platform
    return None

# search keyword in youtube in input period
def run_search(driver, keyword, period_date_start, platform_name):
    print("[Info] Start to parse Tech Community : " + platform_name)
    platform = get_platform(platform_name)
    post_list = []
    if platform == None:
        print("[Warning] Platform not support : " + platform_name)
        return post_list

    if platform_name == "quasarzone":
        return search_quasarzone(platform, driver, keyword, period_date_start)
    elif platform_name == "coolenjoy":
        return search_coolenjoy(platform, driver, keyword, period_date_start)



def search_quasarzone(platform, driver, keyword, period_date_start):
    print("[Info] Run search_quasarzone")
    post_list = []
    date_post = period_date_start
    page_num = 1
    while True:
        url = platform["url"] + keyword.replace(" ", "+") + platform["page"] + str(page_num)
        print("[Info] search : " + url)
        driver.get(url)
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")

        if period_date_start > date_post:
            print("[Info] Meet the date. Stop search!!! : ")
            break

        try:
            posts = soup.find_all('div', class_='cont-wrap')
            if len(posts) == 0:
                break
            for post in posts:
                # date
                date_elem = post.find('p', class_='time')
                if date_elem == None:
                    continue
                date_str = date_elem.text.strip()
                date_post = time.strptime(date_str, "%Y-%m-%d")

                title_elem = post.find('p', class_="title")
                if title_elem == None:
                    continue
                title = title_elem.text.strip()
                link_href = post.find('a')["href"]
                link = urljoin(url, link_href)
                if period_date_start <= date_post:
                    elem = {"url": link, "date": date_str, "title": title}
                    post_list.append(elem)
            page_num += 1
        except Exception as exception:
            print("[Warning] " + str(exception))
            continue

    return post_list



def search_coolenjoy(platform, driver, keyword, period_date_start):
    print("[Info] Run search_coolenjoy")
    post_list = []
    date_post = period_date_start
    page_num = 1
    while True:
        url = platform["url"] + keyword.replace(" ", "+") + platform["page"] + str(page_num)
        print("[Info] search : " + url)
        driver.get(url)
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")

        if period_date_start > date_post:
            print("[Info] Meet the date. Stop search!!! : ")
            break

        try:
            posts = soup.find_all('ul', class_='na-table d-md-table w-100')
            if len(posts) == 0:
                break
            for post in posts:
                # date
                sr_elem = post.find('div', class_='float-left text-muted')
                if sr_elem == None:
                    sr_elem = post.find('div', class_='float-left float-md-none d-md-table-cell nw-6 nw-md-auto f-sm font-weight-normal py-md-2 pr-md-1')
                    if sr_elem == None:
                        continue

                text_contents = [item.strip() for item in sr_elem.contents if isinstance(item, str)]
                date_str = text_contents[2]
                date_post = time.strptime(date_str, "%y.%m.%d")
                date_str = time.strftime("%Y.%m.%d", date_post)

                title_elem = post.find('div', class_="na-item")
                if title_elem == None:
                    continue
                title = title_elem.text.strip()
                link_href = post.find('a')["href"]
                link = urljoin(url, link_href)
                if period_date_start <= date_post:
                    elem = {"url": link, "date": date_str, "title": title}
                    post_list.append(elem)
            page_num += 1
        except Exception as exception:
            print("[Warning] " + str(exception))
            continue

    return post_list

