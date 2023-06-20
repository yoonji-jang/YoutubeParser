# youtube_video_analysis
from tqdm import trange
import requests
import json
from urllib.parse import urlparse, parse_qs
import time

def make_enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    return type('Enum', (), enums)

cIndex = make_enum('TITLE', 'URL', 'SUBSCRIBER', 'LOCATION', 'PROFILE_IMG')


RETURN_ERR = -1

def get_id_from_href(href):
    """Returns Video_ID extracting from the given href of Youtube

    Examples of URLs:
      Valid:
        '/shorts/R98H7jKJIPA'
        '/watch?v=VWhZHi0ml4M&pp=ygUG7J247YWU'
    """
    video_id = None

    # extract string after "/shorts/"
    shorts_index = href.find("/shorts/")
    if shorts_index != -1:
        video_id = href[shorts_index + len("/shorts/"):]

    # extract string after "v="
    if not video_id:
        v_index = href.find("v=")
        if v_index != -1:
            video_id = href[v_index + len("v="):]

    # remove additional parameter (string after &)
    if video_id:
        param_index = video_id.find("&")
        if param_index != -1:
            video_id = video_id[:param_index]

    return video_id


def RequestVideoInfo(vID, dev_key):
    VIDEO_SEARCH_URL = "https://www.googleapis.com/youtube/v3/videos?id=" + vID + "&key=" + dev_key + "&part=snippet,statistics&fields=items(id,snippet(channelId, publishedAt, title, thumbnails.high),statistics)"
    response = requests.get(VIDEO_SEARCH_URL).json()
    return response

def get_video_data(keyword, vID, href, input_json):
    ret = {
        'Keyword' : keyword,
        'Title' : "",
        'URL' : "https://www.youtube.com" + href,
        'View' : 0,
        'Like' : 0,
        'Comment' : 0,
        'ER(%)' : 0,
        'Date' : "",
        'Thumbnail' : "",
        'Channel ID' : "",
    }
    arr = json.dumps(input_json)
    jsonObject = json.loads(arr)
    if ((jsonObject.get('error')) or ('items' not in jsonObject)):
        print("[Warning] response error! : " + vID)
        print(jsonObject['error'])
        return ret
    items = jsonObject['items']
    if len(items) <= 0:
        print("[Warning] no items for Video Data: " + vID)
        return ret
    item = jsonObject['items'][0]

    snippet = item.get('snippet', {})
    ret['Title'] = snippet.get('title', "")
    ret['Date'] = snippet.get('publishedAt', "")
    ret['Channel ID'] = snippet.get('channelId', "")

    statistics = item.get('statistics', {})
    ret['View'] = statistics.get('viewCount', 0)
    ret['Like'] = statistics.get('likeCount', 0)
    ret['Comment'] = statistics.get('commentCount', 0)
    nComment = float(ret['Comment'])
    nLike = float(ret['Like'])
    nView = float(ret['View'])
    ret['ER(%)'] = ((nComment + nLike) / nView * 100) if nView != 0 else 0

    ret['Thumbnail'] = "https://img.youtube.com/vi/" + vID + "/maxresdefault.jpg"

    return ret


def run_VideoAnalysis(keyword, dev_key, period_date_start, period_date_end, thumbnails):
    print("[Info] Running Youtube Video Analysis")
    df_data = []
    for thumbnail in reversed(thumbnails):
        href = thumbnail.attrs["href"]
        # shorts
        vID = get_id_from_href(href)
        if vID == None:
            continue
        res_json = RequestVideoInfo(vID, dev_key)
        video_data = get_video_data(keyword, vID, href, res_json)
        # 2023-05-12T05:01:32Z
        if len(video_data['Date']) > 0:
            date_video = time.strptime(video_data['Date'], '%Y-%m-%dT%H:%M:%SZ')
            if period_date_start > date_video:
                continue
            if period_date_end < date_video:
                break
        df_data.append(video_data)
    return df_data
