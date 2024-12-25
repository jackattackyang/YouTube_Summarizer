import re
import os
from typing import Dict, List, Optional, TypedDict, Union
from dotenv import load_dotenv

import requests
from bs4 import BeautifulSoup
from youtube_transcript_api import YouTubeTranscriptApi
from googleapiclient.discovery import build

from dataclasses import dataclass

from utils.helpers import timestamp_to_date

class Transcript(TypedDict):
    """Type definition for transcript API response."""
    transcript: List[Dict[str, Union[str, float]]]
    is_auto_generated: bool

@dataclass
class Chapter:
    """Data class representing a video chapter."""
    timestamp: str
    title: str

    def __str__(self) -> str:
        return f"{self.timestamp} {self.title}"

@dataclass
class MetaData:
    title: str
    channel_name: str
    publish_date: str
    chapter: Chapter
    transcript: Transcript

# TODO: test if no transcript available
def load_api_key():
    load_dotenv(override=True)
    api_key = os.getenv("YOUTUBE_API_TOKEN")
    if not api_key:
        raise ValueError("YOUTUBE_API_TOKEN is not set in the environment.")
    return api_key
API_KEY = load_api_key()

def get_transcript(video_id):
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

def extract_chapters(description):
    chapter_pattern = r"(\d{1,2}:\d{2}(?::\d{2})?)\s+(.*)"
    matches = re.findall(chapter_pattern, description)

    chapters = []
    for match in matches:
        chapters.append(' '.join(match))
    return chapters

def get_description_bs4(video_url):
    response = requests.get(video_url, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(response.content, features="lxml")
    pattern = re.compile('(?<=shortDescription":").*(?=","isCrawlable)')
    description = pattern.findall(str(soup))[0].replace('\\n','\n')
    return description

def get_meta_data(video_url, api_key):
    video_id = extract_video_id(video_url)

    transcript = get_transcript(video_id)

    youtube = build("youtube", "v3", developerKey=api_key)
    request = youtube.videos().list(
        part="snippet",
        id=video_id
    )
    response = request.execute()
    meta = response['items'][0]['snippet']

    return MetaData(
        title=meta['title'],
        channel_name=meta['channelTitle'],
        publish_date=timestamp_to_date(meta['publishedAt']),
        chapter=extract_chapters(meta['description']),
        transcript=transcript
    )


def extract_video_id(url):
    pattern = r"(?:v=|\/)([0-9A-Za-z_-]{11}).*"
    match = re.search(pattern, url)
    if match:
        return match.group(1)
    else:
        return None