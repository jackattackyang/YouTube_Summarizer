import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Tuple

from utils.helpers import time_to_seconds


def clean_transcript(transcript: list[dict[str, str]]) -> list[str]:
    cleaned = []
    for segment in transcript:
        segment = f"{segment['start']} - {segment['text']}"
        segment = clean_text(segment)
        cleaned.append(segment)
    return cleaned


def clean_text(text):
    text = re.sub(r"\[.*?\]", "", text)  # Remove annotations [Music]
    text = re.sub(r"\s+|\n", " ", text).strip()  # White space or newline
    return text


@dataclass
class ChapterTranscript:
    chapter: str
    timestamp: str
    transcript: List[str] = field(default_factory=list)

    @staticmethod
    def parse_chapters(chapters: List[str]) -> List[Tuple[int, "ChapterTranscript"]]:
        pattern = r"(\d{1,2}:\d{1,2})\s*[-]?\s*(.*)"
        output = []
        try:
            for chapter in chapters:
                timestamp, text = re.match(pattern, chapter).groups()
                output.append(
                    (
                        time_to_seconds(timestamp),
                        ChapterTranscript(
                            chapter=text,
                            timestamp=timestamp,
                        ),
                    )
                )
            return [
                (
                    time_to_seconds(re.match(pattern, chapter).groups()[0]),
                    ChapterTranscript(
                        chapter=re.match(pattern, chapter).groups()[1],
                        timestamp=re.match(pattern, chapter).groups()[0],
                    ),
                )
                for chapter in chapters
            ]
        except Exception as e:
            raise ValueError(f"Failed to parse chapters: {e}")

    @staticmethod
    def assign_transcripts_to_chapters(
        chapter_data: List[Tuple[int, "ChapterTranscript"]],
        transcript_data: List[Tuple[float, str]],
    ) -> List["ChapterTranscript"]:
        """Assign transcript entries to the appropriate chapters."""
        try:
            current_chapter_index = 0
            for transcript_time, transcript_text in transcript_data:
                # Move to the next chapter if the transcript time exceeds the current chapter time
                while (
                    current_chapter_index + 1 < len(chapter_data)
                    and transcript_time >= chapter_data[current_chapter_index + 1][0]
                ):
                    current_chapter_index += 1

                # Add the transcript to the current chapter
                chapter_data[current_chapter_index][1].transcript.append(
                    transcript_text
                )

            # Return only the ChapterTranscript objects
            return [chapter for _, chapter in chapter_data]
        except Exception as e:
            raise ValueError(f"Failed to assign transcripts to chapters: {e}")


def merge_chapter_transcript(meta_data):
    transcript = meta_data.transcript["transcript"]
    cleaned = clean_transcript(transcript)

    chapters = meta_data.chapters

    if not chapters:
        transcript_data = [t.split("-", maxsplit=1)[1].strip() for t in cleaned]
        return [
            ChapterTranscript(chapter=None, timestamp=None, transcript=transcript_data)
        ]

    transcript_data = [
        (
            float(t.split("-", maxsplit=1)[0].strip()),
            t.split("-", maxsplit=1)[1].strip(),
        )
        for t in cleaned
    ]

    chapter_data = ChapterTranscript.parse_chapters(chapters)
    # Assign transcripts to chapters
    merged_chapters = ChapterTranscript.assign_transcripts_to_chapters(
        chapter_data, transcript_data
    )
    return merged_chapters


def get_prompt(meta_data, chapter_transcript):
    if meta_data.chapters:
        return get_chapter_prompt(meta_data, chapter_transcript)

    return get_no_chapter_prompt(meta_data, chapter_transcript)


def get_no_chapter_prompt(meta_data, chapter_transcript):
    prompt = [
        """
Instructions:
* Provide video title
* Provide high level overall summary.
* Summarize into major chapters, for each chapter create an informative summary in **bullet-point format**
* Provide additional context where appropriate.

Can refer to this example structure:
```
Title:
    High level summary
Chapter 1: Example Title
    - Summary

Chapter 2: Example Title
    - Summary
```

Inputs:"""
    ]
    prompt.append(f"Title: {meta_data.title}")
    prompt.append(f"Channel Name: {meta_data.channel_name}")
    prompt.append(
        f"Transcript is auto-generated: {meta_data.transcript['is_auto_generated']}"
    )
    prompt.append("")

    prompt.append("Transcript:")
    for chapter in chapter_transcript:
        transcript = []
        for line in chapter.transcript:
            transcript.append(f"{line}")
        prompt.append(" ".join(transcript))
        prompt.append("")

    return "\n".join(prompt)


def get_chapter_prompt(meta_data, chapter_transcript):
    prompt = [
        """
Instructions:
* Provide video title
* Provide high level overall summary.
* For each chapter create an informative summary in **bullet-point format**, provide additional context where appropriate.
* Include the chapter's timestamp, infer start and end duration.

Can refer to this example structure:
```
Title:
    High level summary
Chapter 1: Example Title (00:00 - 02:00)
    - Summary

Chapter 2: Example Title (02:00 - 04:00)
    - Summary
```

Inputs:"""
    ]
    prompt.append(f"Title: {meta_data.title}")
    prompt.append(f"Channel Name: {meta_data.channel_name}")
    prompt.append(
        f"Transcript is auto-generated: {meta_data.transcript['is_auto_generated']}"
    )
    prompt.append("")

    for chapter in chapter_transcript:
        prompt.append(f"(Timestamp: {chapter.timestamp}) {chapter.chapter}")
        prompt.append("Transcript:")
        transcript = []
        for line in chapter.transcript:
            transcript.append(f"{line}")
        prompt.append(" ".join(transcript))
        prompt.append("")

    return "\n".join(prompt)


def get_video_info(meta_data, chapter_transcript):
    prompt = []
    prompt.append(f"Title: {meta_data.title}")
    prompt.append(f"Channel Name: {meta_data.channel_name}")
    prompt.append(
        f"Transcript is auto-generated: {meta_data.transcript['is_auto_generated']}"
    )
    prompt.append("")

    for chapter in chapter_transcript:
        prompt.append(f"(Timestamp: {chapter.timestamp}) {chapter.chapter}")
        prompt.append("Transcript:")
        transcript = []
        for line in chapter.transcript:
            transcript.append(f"{line}")
        prompt.append(" ".join(transcript))
        prompt.append("")

    return "\n".join(prompt)
