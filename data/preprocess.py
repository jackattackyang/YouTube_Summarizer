import re


def clean_transcript(transcript: list[dict[str, str]]) -> list[str]:
    cleaned = []
    for segment in transcript:
        segment = f"{segment['start']:.0f}s - {segment['text']}"
        segment = clean_text(segment)
        cleaned.append(segment)
    return cleaned

def clean_text(text):
    text = re.sub(r"\[.*?\]", "", text)     # Remove annotations [Music]
    text = re.sub(r"\s+|\n", " ", text).strip()  # White space or newline
    return text

def chunk_transcript(cleaned_transcript: list[str], chunk_size=50_000) -> list[str]:
    size = 0
    chunk = []
    lst_chunk = []
        
    for i in range(len(cleaned_transcript)):
        segment = cleaned_transcript[i]
        if size + len(segment) > chunk_size:
            lst_chunk.append(' '.join(chunk))
            chunk = []
            size = 0
        chunk.append(segment)
        size += len(segment)
    if not lst_chunk:
        return ' '.join(chunk)
    return lst_chunk