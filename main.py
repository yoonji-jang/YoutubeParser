import argparse
from video_analysis import run_video_analysis
from influencer_analysis import run_influencer_analysis

# 1. print version info
VERSION = 5.0
print("[Info] YoutubeParser V" + str(VERSION))

# 2. parse argument
parser = argparse.ArgumentParser()
# common
parser.add_argument('--va', action='store_true', help='video analysis')
parser.add_argument('--ia', action='store_true', help='influencer analysis')
parser.add_argument('-input', type=str, dest="input_txt", action='store', default="input_video.txt", help='input text file')
# influencer analysis
parser.add_argument('--yc', action='store_true', help='youtube channel')
parser.add_argument('--yv', action='store_true', help='youtube video')
parser.add_argument('--ic', action='store_true', help='instagram channel')
parser.add_argument('--ip', action='store_true', help='instagram post')

args = parser.parse_args()

# 3. run YoutubeAnalysis
if (args.va == True):
    run_video_analysis(args)
else:
    run_influencer_analysis(args)