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


def RequestChannelInfo(cID, dev_key):
    CHANNEL_SEARCH_URL = f"https://www.googleapis.com/youtube/v3/channels?id={cID}&key={dev_key}&part=snippet,statistics"
    response = requests.get(CHANNEL_SEARCH_URL).json()
    return response



def RequestVideoInfo(vID, dev_key):
    VIDEO_SEARCH_URL = "https://www.googleapis.com/youtube/v3/videos?id=" + vID + "&key=" + dev_key + "&part=snippet,statistics&fields=items(id,snippet(channelId, publishedAt, title, thumbnails.high),statistics)"
    response = requests.get(VIDEO_SEARCH_URL).json()
    return response

def get_channel_data(input_json, cID):
    ret = {
        'Channel' : "",
        'Subscriber' : 0,
        'Location' : "",
        'Channel URL' : "",
        "Channel Thumbnail" : "",
    }
    items = input_json.get("items")
    if items:
        channel = items[0]
        ret['Channel'] = channel["snippet"]["title"]
        ret['Subscriber'] = channel["statistics"]["subscriberCount"]
        ret['Location'] = channel["snippet"].get("country", "")
        ret['Channel URL'] = f"https://www.youtube.com/channel/{cID}"
        ret['Channel Thumbnail'] = channel["snippet"]["thumbnails"]["default"]["url"]
    return ret


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
        'ChannelID' : "",
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
    date_str = snippet.get('publishedAt', "")
    if len(date_str) > 0:
        # 2023-05-12T05:01:32Z
        time_tuple = time.strptime(date_str, '%Y-%m-%dT%H:%M:%SZ')
        ret['Date'] = time.strftime("%Y-%m-%d", time_tuple)

    statistics = item.get('statistics', {})
    ret['View'] = statistics.get('viewCount', 0)
    ret['Like'] = statistics.get('likeCount', 0)
    ret['Comment'] = statistics.get('commentCount', 0)
    nComment = float(ret['Comment'])
    nLike = float(ret['Like'])
    nView = float(ret['View'])
    nER = ((nComment + nLike) / nView * 100) if nView != 0 else 0
    ret['ER(%)'] = str(nER) + "%"

    ret['Thumbnail'] = "https://img.youtube.com/vi/" + vID + "/maxresdefault.jpg"
    ret['ChannelID'] = snippet.get('channelId', "")

    return ret


def run_VideoAnalysis(keyword, dev_key, period_date_start, period_date_end, thumbnails):
    print("[Info] Running Youtube Video Analysis")
    df_data = []
    for thumbnail in reversed(thumbnails):
        #video
        href = thumbnail.attrs["href"]
        vID = get_id_from_href(href)
        if vID == None:
            print("[Warning] video id is None for : " + href)
            continue
        video_json = RequestVideoInfo(vID, dev_key)
        video_data = get_video_data(keyword, vID, href, video_json)
        if len(video_data['Date']) > 0:
            date_video = time.strptime(video_data['Date'], '%Y-%m-%d')
            if period_date_start > date_video:
                continue
            if period_date_end < date_video:
                break

        cID = video_data['ChannelID']
        if cID == None:
            print("[Warning] channel id is None for : " + href)
            continue
        channel_json = RequestChannelInfo(cID, dev_key)
        channel_data = get_channel_data(channel_json, cID)

        video_channel_data = {**video_data, **channel_data}
        df_data.append(video_channel_data)
    return df_data
