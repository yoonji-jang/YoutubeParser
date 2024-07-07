# youtube_video_analysis
from googleapiclient.discovery import build
from bs4 import BeautifulSoup
from tqdm import trange
import requests
import json
from urllib.parse import urlparse, parse_qs
import time
from tqdm import tqdm
import pandas as pd


def get_post_data(driver, keyword, url_data):
    ret = []
    row = {
        'Keyword' : keyword,
        'Date' : url_data['date'],
        'Title' : url_data['title'],
        'Comment' : [],
        'URL' : url_data['url'],
        'Reply' : "",
        'View' : "",
        'Like' : ""
    }
    ret.append(row)

    driver.get(url_data['url'])
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(1)

    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")
    row['Reply'] = soup.find('em', class_="reply").text if soup.find('em', class_="reply") else ""
    row['View'] = soup.find('em', class_="view").text if soup.find('em', class_="view") else ""
    row['Like'] = soup.find('em', class_="like").text if soup.find('em', class_="like") else ""

    # comments = comment_elem.select('div', class_="mid-text-area")
    
    comment_elem = soup.find('div', class_="reply-list")
    if (comment_elem == None):
        return ret

    comments = comment_elem.find_all('div', class_='note-editor content-view-ok')

    for comment in comments:
        new_row = row.copy()
        str_comment = comment.text
        new_row['Comment'] = str_comment
        ret.append(new_row)
    
    
    return ret


def run_TechCommunityAnalysis(driver, keyword, list_url_data):
    df_data = pd.DataFrame()
    print("[Info] Running Tech Community Analysis")
    print("[Info] list size = " +  str(len(list_url_data)))
    for url_data in tqdm(reversed(list_url_data)):
        post_data = get_post_data(driver, keyword, url_data)
        df_data = pd.concat([pd.DataFrame([data]) for data in post_data], ignore_index=True)
    ret = df_data.to_dict(orient='records')
    return ret