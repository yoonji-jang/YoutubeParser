# youtube_video_analysis
from tqdm import trange
import requests
import json
from urllib.parse import urlparse, parse_qs
import time

def make_enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    return type('Enum', (), enums)

vIndex = make_enum('KEYWORD', 'TITLE', 'URL', 'VIEW', 'LIKE', 'COMMENTS', 'ER', 'DATE', 'THUMBNAIL', 'CHANNEL_ID')
cIndex = make_enum('TITLE', 'URL', 'SUBSCRIBER', 'LOCATION', 'PROFILE_IMG')


RETURN_ERR = -1

def get_id_from_url(url):
    """Returns Video_ID extracting from the given url of Youtube

    Examples of URLs:
      Valid:
        'http://youtu.be/_lOT2p_FCvA',
        'www.youtube.com/watch?v=_lOT2p_FCvA&feature=feedu',
        'http://www.youtube.com/embed/_lOT2p_FCvA',
        'http://www.youtube.com/v/_lOT2p_FCvA?version=3&amp;hl=en_US',
        'https://www.youtube.com/watch?v=rTHlyTphWP0&index=6&list=PLjeDyYvG6-40qawYNR4juzvSOg-ezZ2a6',
        'youtube.com/watch?v=_lOT2p_FCvA',
        'https://www.youtube.com/channel/UCUbOogiD-4PKDqaJfSOTC0g'
      Invalid:
        'youtu.be/watch?v=_lOT2p_FCvA',
    """
    if url.startswith(('youtu', 'www')):
        url = 'http://' + url
    elif url.startswith(('insta', 'www')):
        url = 'http://' + url

    query = urlparse(url)

    if 'youtube' in query.hostname:
        if (query.path == '/watch') or (query.path == '//watch'):
            return parse_qs(query.query)['v'][0]
        elif query.path.startswith(('/embed/', '/v/', '/channel/')):
            return query.path.split('/')[2]
    elif 'youtu.be' in query.hostname:
        return query.path[1:]
    elif 'instagram' in query.hostname:
        if query.path.startswith('/p/'):
            return query.path.split('/')[2]
        else:
            return query.path.split('/')[1]
    else:
        return RETURN_ERR


def RequestVideoInfo(vID, dev_key):
    VIDEO_SEARCH_URL = "https://www.googleapis.com/youtube/v3/videos?id=" + vID + "&key=" + dev_key + "&part=snippet,statistics&fields=items(id,snippet(channelId, publishedAt, title, thumbnails.high),statistics)"
    response = requests.get(VIDEO_SEARCH_URL).json()
    return response

def get_video_data(keyword, vID, input_json, period_date_start, period_date_end):
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
    ret[vIndex.TITLE] = snippet.get('title', "")
    ret[vIndex.DATE] = snippet.get('publishedAt', "")
    ret[vIndex.CHANNEL_ID] = snippet.get('channelId', "")

    statistics = item.get('statistics', {})
    ret[vIndex.VIEW] = statistics.get('viewCount', 0)
    ret[vIndex.LIKE] = statistics.get('likeCount', 0)
    ret[vIndex.COMMENTS] = statistics.get('commentCount', 0)
    nComment = float(ret[vIndex.COMMENTS])
    nLike = float(ret[vIndex.LIKE])
    nView = float(ret[vIndex.VIEW])
    ret[vIndex.ER] = (nComment + nLike) / nView if nView != 0 else 0

    ret[vIndex.THUMBNAIL] = "https://img.youtube.com/vi/" + vID + "/maxresdefault.jpg"

    return ret


def run_VideoAnalysis(keyword, dev_key, period_date_start, period_date_end, thumbnails):
    print("[Info] Running Youtube Video Analysis")
    df_data = []
    for thumbnail in reversed(thumbnails):
        link = "https://www.youtube.com" + thumbnail.attrs["href"]
        vID = get_id_from_url(link)
        if vID == None:
            continue
        res_json = RequestVideoInfo(vID, dev_key)
        video_data = get_video_data(keyword, vID, res_json, period_date_start, period_date_end)
        # 2023-05-12T05:01:32Z
        if len(video_data[vIndex.DATE]) > 0:
            date_video = time.strptime(video_data[vIndex.DATE], '%Y-%m-%dT%H:%M:%SZ')
            if period_date_start > date_video:
                continue
            if period_date_end < date_video:
                break
        df_data.append(video_data)
    return df_data
