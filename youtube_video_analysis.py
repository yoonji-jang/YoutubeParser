# youtube_video_analysis
from tqdm import trange
import requests
import json

def make_enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    return type('Enum', (), enums)

vIndex = make_enum('KEYWORD', 'TITLE', 'URL', 'VIEW', 'LIKE', 'COMMENTS', 'ER', 'DATE', 'THUMBNAIL', 'CHANNEL_ID')
cIndex = make_enum('TITLE', 'URL', 'SUBSCRIBER', 'LOCATION', 'PROFILE_IMG')


RETURN_ERR = -1

def RequestVideoInfo(vID, dev_key):
    VIDEO_SEARCH_URL = "https://www.googleapis.com/youtube/v3/videos?id=" + vID + "&key=" + dev_key + "&part=snippet,statistics&fields=items(id,snippet(channelId, title, thumbnails.high),statistics)"
    response = requests.get(VIDEO_SEARCH_URL).json()
    return response

def get_video_data(keyword, vID, input_json, dev_key):
    arr = json.dumps(input_json)
    jsonObject = json.loads(arr)
    if ((jsonObject.get('error')) or ('items' not in jsonObject)):
        print("[Warning] response error! : " + vID)
        print(jsonObject['error'])
        return RETURN_ERR
    items = jsonObject['items']
    if len(items) <= 0:
        print("[Warning] no items for Video Data: " + vID)
        return RETURN_ERR
    item = jsonObject['items'][0]
    ret = {}
    ret[vIndex.KEYWORD] = keyword
    ret[vIndex.TITLE] = ""
    ret[vIndex.URL] = "https://www.youtube.com/watch?v=" + vID
    ret[vIndex.VIEW] = 0
    ret[vIndex.LIKE] = 0
    ret[vIndex.COMMENTS] = 0
    ret[vIndex.ER] = 0
    ret[vIndex.DATE] = ""
    ret[vIndex.THUMBNAIL] = ""
    ret[vIndex.CHANNEL_ID] = ""

    snippet = item.get('snippet', {})
    ret[vIndex.TITLE] = snippet.get('title', "")
    ret[vIndex.DATE] = snippet.get('publishedAt', "")
    ret[vIndex.CHANNEL_ID] = snippet.get('channelId', "")

    statistics = item.get('statistics', {})
    ret[vIndex.VIEW] = statistics.get('viewCount', 0)
    ret[vIndex.LIKE] = statistics.get('likeCount', 0)
    ret[vIndex.COMMENTS] = statistics.get('commentCount', 0)
    ret[vIndex.ER] = (ret[vIndex.COMMENTS] + ret[vIndex.LIKE]) / ret[vIndex.VIEW] if ret[vIndex.VIEW] != 0 else 0

    ret[vIndex.THUMBNAIL] = "https://img.youtube.com/vi/" + vID + "/maxresdefault.jpg"

    return ret


def run_VideoAnalysis(keyword, vID, dev_key):
    print("[Info] Running Youtube Video Analysis")
    res_json = RequestVideoInfo(vID, dev_key)
    df_just_video = get_video_data(keyword, vID, res_json, dev_key)
    return df_just_video
