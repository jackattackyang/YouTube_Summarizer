import re

import requests
from bs4 import BeautifulSoup
from youtube_transcript_api import YouTubeTranscriptApi

# TODO: test if no transcript available


def get_transcript(youtube_url):
    video_id = youtube_url.split("v=")[-1]
    transcript = None
    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        for script in transcript_list:
            print(f"Language: {script.language}")
            print(f"Language: {script.language_code}")
            print(f"Generated automatically: {script.is_generated}")
            print(f"Translation available: {script.is_translatable}")
            print("-----")
            if "en" in script.language_code and not script.is_generated:
                transcript = script.fetch()
                return {"transcript": transcript, "is_auto_generated": False}
        transcript = transcript_list.find_transcript(["en"]).fetch()
        return {"transcript": transcript, "is_auto_generated": True}
    except Exception as e:
        print(f"An error occurred: {e}")

def get_chapters(youtube_url):
    soup = BeautifulSoup(requests.get(youtube_url).content, features="lxml")
    pattern = re.compile('(?<=shortDescription":").*(?=","isCrawlable)')
    description = pattern.findall(str(soup))[0].replace('\\n','\n')
    return extract_chapters(description)

def extract_chapters(description):
    chapter_pattern = r"(\d{1,2}:\d{2}(?::\d{2})?)\s+(.*)"
    matches = re.findall(chapter_pattern, description)

    chapters = []
    for match in matches:
        chapters.append(' '.join(match))
    return chapters