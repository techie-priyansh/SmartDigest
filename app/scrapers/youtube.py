from youtube_transcript_api import YouTubeTranscriptApi


def fetch_transcript(video_id: str) -> str:
    """
    Fetch a YouTube video's transcript and return it as clean text.
    """
    api = YouTubeTranscriptApi()

    try:
        transcript = api.fetch(video_id)

        clean_text = " ".join(
            snippet.text.strip()
            for snippet in transcript
            if snippet.text.strip()
        )

        if not clean_text:
            raise ValueError("Transcript is empty.")

        return clean_text

    except Exception as e:
        raise RuntimeError(
            f"Failed to fetch transcript for video '{video_id}': {e}"
        ) from e