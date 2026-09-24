import os
import random
import time

from dotenv import load_dotenv
from google import genai


load_dotenv()


# Models are tried in this order.
GEMINI_MODELS = [
    "gemini-3.6-flash",
    "gemini-3.5-flash",
    "gemini-3.1-flash-lite",
    "gemini-flash-latest",
]


# Number of retries after the initial attempt.
MAX_RETRIES = 3

# Initial retry delay.
BASE_DELAY = 5

# Maximum delay between retries.
MAX_DELAY = 60


def get_gemini_client():
    """Create and return a Gemini API client."""

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY is not set. "
            "Add it to the .env file."
        )

    return genai.Client(api_key=api_key)


def _is_retryable_error(error: Exception) -> bool:
    """
    Return True when the Gemini error is temporary
    and should be retried.
    """

    error_text = str(error).upper()

    retryable_codes = (
        "429",
        "500",
        "503",
        "504",
        "RESOURCE_EXHAUSTED",
        "INTERNAL",
        "UNAVAILABLE",
        "DEADLINE_EXCEEDED",
    )

    return any(
        code in error_text
        for code in retryable_codes
    )


def _wait_before_retry(attempt: int) -> None:
    """
    Exponential backoff with jitter.

    Approximate delays:
        attempt 0 -> 5 seconds
        attempt 1 -> 10 seconds
        attempt 2 -> 20 seconds
    """

    delay = min(
        BASE_DELAY * (2 ** attempt),
        MAX_DELAY,
    )

    jitter = random.uniform(0, 2)

    total_delay = delay + jitter

    print(
        f"Waiting {total_delay:.1f}s before retry..."
    )

    time.sleep(total_delay)


def _generate_with_model(
    client,
    model: str,
    prompt: str,
) -> str:
    """
    Generate content using one Gemini model.

    Retries temporary failures using exponential backoff.
    """

    for attempt in range(MAX_RETRIES + 1):

        try:

            print(
                f"Trying model: {model} "
                f"(attempt {attempt + 1}/{MAX_RETRIES + 1})"
            )

            response = client.models.generate_content(
                model=model,
                contents=prompt,
            )

            if not response.text:
                raise RuntimeError(
                    f"{model} returned an empty response."
                )

            print(
                f"Successfully generated response "
                f"using {model}"
            )

            return response.text.strip()

        except Exception as error:

            print(
                f"{model} failed: "
                f"{type(error).__name__}: {error}"
            )

            # Non-temporary error.
            if not _is_retryable_error(error):
                raise

            # No retries remaining.
            if attempt >= MAX_RETRIES:
                break

            _wait_before_retry(attempt)

    raise RuntimeError(
        f"Model {model} failed after "
        f"{MAX_RETRIES + 1} attempts."
    )


def summarize_transcript(
    transcript: str,
    title: str,
) -> str:
    """
    Summarize a YouTube video transcript using Gemini.

    Multiple Gemini models are attempted automatically
    if temporary API failures occur.
    """

    if not transcript.strip():
        raise ValueError(
            "Transcript cannot be empty."
        )

    if not title.strip():
        raise ValueError(
            "Title cannot be empty."
        )

    client = get_gemini_client()

    prompt = f"""
You are an AI news editor.

Summarize the following news video clearly and objectively.

Video title:
{title}

Transcript:
{transcript}

Requirements:
- Write a concise summary in 3-5 paragraphs.
- Focus on the key facts, events, people, and developments.
- Remove repetition and filler from the transcript.
- Do not invent information that is not present in the transcript.
- Maintain a neutral journalistic tone.
"""

    last_error = None

    for model in GEMINI_MODELS:

        try:

            return _generate_with_model(
                client=client,
                model=model,
                prompt=prompt,
            )

        except Exception as error:

            last_error = error

            print(
                f"\n{model} unavailable."
            )

            print(
                "Switching to the next Gemini model...\n"
            )

    raise RuntimeError(
        "Gemini summarization failed with all "
        "configured models."
    ) from last_error