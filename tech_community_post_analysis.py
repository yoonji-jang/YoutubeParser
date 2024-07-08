# youtube_video_analysis
from bs4 import BeautifulSoup
import time
from tqdm import tqdm
import pandas as pd



def get_post_data(driver, keyword, url_data, platform):
    if "quasarzone" in platform:
        return get_post_data_quasarzone(driver, keyword, url_data)
    elif "coolenjoy" in platform:
        return get_post_data_coolenjoy(driver, keyword, url_data)


def run_TechCommunityAnalysis(driver, keyword, list_url_data, platform):
    df_data = pd.DataFrame()
    print("[Info] Running Tech Community Analysis")
    print("[Info] list size = " +  str(len(list_url_data)))
    for url_data in tqdm(reversed(list_url_data)):
        post_data = get_post_data(driver, keyword, url_data, platform)
        df_data = pd.concat([df_data, pd.DataFrame(post_data)], ignore_index=True)
    ret = df_data.to_dict(orient='records')
    return ret


def get_post_data_quasarzone(driver, keyword, url_data):
    ret = []
    row = {
        'Keyword' : keyword,
        'Date' : url_data['date'],
        'Title' : url_data['title'],
        'Comment' : "",
        'URL' : url_data['url'],
        'Reply' : "",
        'View' : "",
        'Like' : ""
    }
    try:
        driver.get(url_data['url'])
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        html = driver.page_source
    except Exception as exception:
        print("[Warning] " + str(exception))
        print("[Warning] url: " + url_data['url'])
        ret.append(row)
        return ret

    soup = BeautifulSoup(html, "html.parser")
    row['Reply'] = soup.find('em', class_="reply").text if soup.find('em', class_="reply") else ""
    row['View'] = soup.find('em', class_="view").text if soup.find('em', class_="view") else ""
    row['Like'] = soup.find('em', class_="like").text if soup.find('em', class_="like") else ""

    # comments = comment_elem.select('div', class_="mid-text-area")
    
    comment_elem = soup.find('div', class_="reply-list")
    if (comment_elem == None):
        ret.append(row)
        return ret

    comments = comment_elem.find_all('div', class_='note-editor content-view-ok')
    for comment in comments:
        new_row = row.copy()
        str_comment = comment.text
        new_row['Comment'] = str_comment
        ret.append(new_row)
    
    return ret



def get_post_data_coolenjoy(driver, keyword, url_data):
    ret = []
    row = {
        'Keyword' : keyword,
        'Date' : url_data['date'],
        'Title' : url_data['title'],
        'Comment' : "",
        'URL' : url_data['url'],
        'Reply' : "",
        'View' : "",
        'Like' : ""
    }
    try:
        driver.get(url_data['url'])
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        html = driver.page_source
    except Exception as exception:
        print("[Warning] " + str(exception))
        print("[Warning] url: " + url_data['url'])
        ret.append(row)
        return ret

    soup = BeautifulSoup(html, "html.parser")


    # 결과를 저장할 딕셔너리
    result = {'조회': 0, '댓글': 0, '추천': 0}

    # 모든 <li> 요소 가져오기
    li_elements = soup.find_all('li', class_='pr-3')

    for li in li_elements:
        # <li> 요소의 텍스트 가져오기
        li_text = li.text.strip()

        # 숫자 정보 추출
        number_text = ''.join(filter(str.isdigit, li_text))
        number = int(number_text) if number_text else 0

        # <span class="sr-only"> 태그의 텍스트 확인하여 결과에 추가
        span = li.find('span', class_='sr-only')
        if span:
            span_text = span.text.strip()
            if span_text in result:
                result[span_text] = number

    row['Reply'] = result['댓글']
    row['View'] = result['조회']
    row['Like'] = result['추천']

    comment_elem = soup.find('section', id="bo_vc", class_="na-fadein")
    if (comment_elem == None):
        ret.append(row)
        return ret

    comments = comment_elem.find_all('div', class_='cmt_contents')
    for comment in comments:
        new_row = row.copy()
        str_comment = comment.text.strip()
        new_row['Comment'] = str_comment
        ret.append(new_row)

    return ret
