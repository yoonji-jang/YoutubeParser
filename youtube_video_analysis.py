# youtube_video_analysis
from googleapiclient.discovery import build
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
# youtube api
YOUTUBE_API_SERVICE_NAME="youtube"
YOUTUBE_API_VERSION="v3"

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

def GetDevKeyAvailable(dev_keys):
    key_len = len(dev_keys)
    if GetDevKeyAvailable.key_ind >= key_len:
        print("[Error] No more developer keys available")
        return RETURN_ERR
    return dev_keys[GetDevKeyAvailable.key_ind]
GetDevKeyAvailable.key_ind = 0

def UseNextDevKey():
    GetDevKeyAvailable.key_ind += 1
    print("[Info] Use Next dev key. key_ind = " + str(GetDevKeyAvailable.key_ind))


def RequestYoutubeAPI(request_url_prefix, dev_keys):
    while True:
        dev_key = GetDevKeyAvailable(dev_keys)
        if dev_key == RETURN_ERR:
            print("[Error] No more developer keys available")
            return RETURN_ERR
        request_url = f"{request_url_prefix}&key={dev_key}"
        response = requests.get(request_url).json()
        if "quotaExceeded" in str(response):
            print("[Info] Quota exceeded : " + dev_key + ". Retry with next key")
            UseNextDevKey()
            continue
        if "API_KEY_INVALID" in str(response):
            print("[Info] Invalid key : " + dev_key + ". Retry with next key")
            UseNextDevKey()
            continue
        break
    return response

def RequestChannelInfo(cID, dev_keys):
    channel_request_prefix = f"https://www.googleapis.com/youtube/v3/channels?id={cID}&part=snippet,statistics"
    return RequestYoutubeAPI(channel_request_prefix, dev_keys)



def RequestVideoInfo(vID, dev_keys):
    VIDEO_SEARCH_URL = f"https://www.googleapis.com/youtube/v3/videos?id={vID}&part=snippet,statistics"
    return RequestYoutubeAPI(VIDEO_SEARCH_URL, dev_keys)

def RequestChannelContentsInfo(dev_keys, cID, max_result):
    while True:
        dev_key = GetDevKeyAvailable(dev_keys)
        if dev_key == RETURN_ERR:
            print("[Error] No more developer keys available")
            return RETURN_ERR
        try:
            youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=dev_key)
            response = youtube.search().list(
                channelId = cID,
                type = "video",
                order = "date",
                part = "id",
                fields = "items(id)",
                maxResults = max_result
            ).execute()
        except Exception as exception:
            print("[Warning]" + str(exception))
            print("dev_key=" + dev_key + ", cID=" + cID)
            return RETURN_ERR
        if "quotaExceeded" in str(response):
            print("[Info] Quota exceeded : " + dev_key + ". Retry with next key")
            UseNextDevKey()
            continue
        if "API_KEY_INVALID" in str(response):
            print("[Info] Invalid key : " + dev_key + ". Retry with next key")
            UseNextDevKey()
            continue
        break
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
        'Category' : "",
        'View' : 0,
        'Like' : 0,
        'Comment' : 0,
        'ER(%)' : 0,
        'Date' : "",
        'Thumbnail' : "",
        'ChannelID' : "",
    }
    if 'shorts' in href:
        ret['Category'] = 'Shorts'
    else:
        ret['Category'] = 'Video'
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


vIDs = []
def run_VideoAnalysis(keyword, dev_keys, period_date_start, period_date_end, thumbnails):
    df_data = []
    print("[Info] Running Youtube Video Analysis")
    for thumbnail in reversed(thumbnails):
        #video
        href = thumbnail.attrs["href"]
        vID = get_id_from_href(href)
        if vID == None:
            print("[Warning] video id is None for : " + href)
            continue
        if vID in vIDs:
            print("[Info] Skip duplicated video id: " + vID)
            continue
        vIDs.append(vID)

        ret = RequestVideoInfo(vID, dev_keys)
        if ret == RETURN_ERR:
            print("[Info] Stop crawling due to Quota Exceeded errer for all developer keys")
            return df_data

        video_json = ret
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
        ret = RequestChannelInfo(cID, dev_keys)
        if ret == RETURN_ERR:
            print("[Info] Stop crawling due to Quota Exceeded errer for all developer keys")
            return df_data

        channel_json = ret
        channel_data = get_channel_data(channel_json, cID)

        video_channel_data = {**video_data, **channel_data}
        df_data.append(video_channel_data)
    return df_data