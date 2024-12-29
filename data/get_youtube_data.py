import re
import os
import logging
from typing import Dict, List, Optional, TypedDict, Union
from dataclasses import dataclass
from dotenv import load_dotenv
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from youtube_transcript_api import YouTubeTranscriptApi
from googleapiclient.discovery import build


from utils.helpers import timestamp_to_date


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@dataclass
class Transcript:
    transcript: List[Dict[str, Union[str, float]]]
    is_auto_generated: bool


@dataclass
class Chapter:
    """Data class representing a video chapter."""

    timestamp: str
    title: str


@dataclass
class MetaData:
    title: str
    channel_name: str
    publish_date: str
    chapters: str
    transcript: Optional[Transcript]


class YouTubeDataFetcher:
    YOUTUBE_API_VERSION = "v3"
    TRANSCRIPT_LANG_CODE = "en"

    def __init__(self, env_path: Optional[Path] = None):
        self.api_key = self._load_api_key(env_path)
        self.youtube_client = build(
            "youtube", self.YOUTUBE_API_VERSION, developerKey=self.api_key
        )

    @staticmethod
    def _load_api_key(env_path):
        load_dotenv(override=True)
        api_key = os.getenv("YOUTUBE_API_TOKEN")
        if not api_key:
            raise ValueError("YOUTUBE_API_TOKEN is not set in the environment.")
        return api_key

    def get_transcript(self, video_id: str) -> Optional[Transcript]:
        transcript = None
        try:
            environment = os.getenv("ENVIRONMENT", "local")
            print(f"Running in environment: {environment}")
            if environment == "local":
                transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            else:
                proxy_list = os.getenv("PROXY_LIST")
                for proxy_string in proxy_list.split(","):
                    ip_port, username, password = proxy_string.rsplit(":", 2)
                    proxy_url = f"socks5://{username}:{password}@{ip_port}"
                    proxies = {"http": proxy_url, "https": proxy_url}
                    try:
                        transcript_list = YouTubeTranscriptApi.list_transcripts(
                            video_id, proxies=proxies
                        )
                        break
                    except Exception as e:
                        logger.error("Proxy failed")
                        continue

            for transcript in transcript_list:
                logger.info(f"Language: {transcript.language}")
                logger.info(f"Language: {transcript.language_code}")
                logger.info(f"Generated automatically: {transcript.is_generated}")
                logger.info(f"Translation available: {transcript.is_translatable}")
                logger.info("-----")
                if (
                    self.TRANSCRIPT_LANG_CODE in transcript.language_code
                    and not transcript.is_generated
                ):
                    logger.info("Found manual English transcript")
                    return {
                        "transcript": transcript.fetch(),
                        "is_auto_generated": False,
                    }
            logger.info("Using auto-generated English transcript")
            auto_transcript = transcript_list.find_transcript(
                [self.TRANSCRIPT_LANG_CODE]
            )
            return {"transcript": auto_transcript.fetch(), "is_auto_generated": True}
        except Exception as e:
            raise TranscriptError(f"Failed to fetch transcript: {e}")

    @staticmethod
    def extract_chapters(description: str) -> List[Chapter]:
        chapter_pattern = r"(\d{1,2}:\d{2}(?::\d{2})?)\s+(.*)"
        matches = re.findall(chapter_pattern, description)

        chapters = []
        for match in matches:
            try:
                chapters.append(" ".join(match))
            except ValueError as e:
                logger.warning(f"Skipping invalid chapter: {e}")
                continue

        return chapters

    @staticmethod
    def extract_video_id(url: str) -> Optional[str]:
        pattern = r"(?:v=|\/)([0-9A-Za-z_-]{11}).*"
        match = re.search(pattern, url)
        return match.group(1) if match else None

    def get_meta_data(self, video_url: str) -> MetaData:
        video_id = self.extract_video_id(video_url)
        if not video_id:
            raise ValueError(f"Could not extract valid video ID from URL: {video_url}")

        try:
            response = (
                self.youtube_client.videos().list(part="snippet", id=video_id).execute()
            )

            if not response.get("items"):
                raise YouTubeAPIError(f"No video found for ID: {video_id}")

            meta = response["items"][0]["snippet"]
            transcript = self.get_transcript(video_id)
            chapters = self.extract_chapters(meta["description"])

            return MetaData(
                title=meta["title"],
                channel_name=meta["channelTitle"],
                publish_date=timestamp_to_date(meta["publishedAt"]),
                chapters=chapters,
                transcript=transcript,
            )

        except Exception as e:
            raise YouTubeAPIError(f"Failed to fetch video metadata: {str(e)}")


class YouTubeAPIError(Exception):
    pass


class TranscriptError(Exception):
    pass
