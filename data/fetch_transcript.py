from youtube_transcript_api import YouTubeTranscriptApi

# TODO: test if no transcript available


def fetch_transcript(youtube_link):
    video_id = youtube_link.split("v=")[-1]
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
