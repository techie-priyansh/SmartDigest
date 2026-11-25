# # from app.llm.gemini import summarize_transcript
# # from app.scrapers.youtube import (
# #     fetch_recent_videos,
# #     fetch_transcript,
# # )
# # from app.storage.videos import (
# #     save_video,
# #     update_summary,
# #     update_transcript,
# #     video_exists,
# # )


# # def ingest_youtube_channel(
# #     channel_id: str,
# #     lookback_hours: int = 24,
# # ) -> int:
# #     """
# #     Fetch recent YouTube videos, save metadata,
# #     extract transcripts, and generate summaries.

# #     Returns
# #     -------
# #     int
# #         Number of newly processed videos.
# #     """

# #     videos = fetch_recent_videos(
# #         channel_id=channel_id,
# #         lookback_hours=lookback_hours,
# #     )

# #     new_videos = 0

# #     for video in videos:

# #         video_id = video["video_id"]
# #         title = video["title"]

# #         # --------------------------------------------------
# #         # Check whether the video already exists
# #         # --------------------------------------------------

# #         if video_exists(video_id):
# #             print(
# #                 f"Skipping existing video: {title}"
# #             )
# #             continue

# #         # --------------------------------------------------
# #         # Save video metadata
# #         # --------------------------------------------------

# #         save_video(
# #             video_id=video_id,
# #             channel_id=channel_id,
# #             title=title,
# #             url=video["url"],
# #             published_at=video["published_at"],
# #         )

# #         new_videos += 1

# #         print(f"\nProcessing: {title}")

# #         # --------------------------------------------------
# #         # Fetch transcript
# #         # --------------------------------------------------

# #         try:

# #             transcript = fetch_transcript(
# #                 video_id
# #             )

# #             update_transcript(
# #                 video_id=video_id,
# #                 transcript=transcript,
# #                 status="success",
# #             )

# #             print(
# #                 f"Transcript saved "
# #                 f"({len(transcript)} characters)"
# #             )

# #         except Exception as error:

# #             update_transcript(
# #                 video_id=video_id,
# #                 transcript=None,
# #                 status="failed",
# #             )

# #             print(
# #                 f"Transcript unavailable: {error}"
# #             )

# #             # No transcript → cannot summarize.
# #             continue

# #         # --------------------------------------------------
# #         # Generate Gemini summary
# #         # --------------------------------------------------

# #         try:

# #             summary = summarize_transcript(
# #                 transcript=transcript,
# #                 title=title,
# #             )

# #             update_summary(
# #                 video_id=video_id,
# #                 summary=summary,
# #                 status="success",
# #             )

# #             print(
# #                 f"Summary saved "
# #                 f"({len(summary)} characters)"
# #             )

# #         except Exception as error:

# #             update_summary(
# #                 video_id=video_id,
# #                 summary=None,
# #                 status="failed",
# #             )

# #             print(
# #                 f"Summary generation failed: {error}"
# #             )

# #             # Continue with the next video.
# #             continue

# #     print(
# #         f"\nIngestion complete. "
# #         f"New videos saved: {new_videos}"
# #     )

# #     return new_videos


# from app.llm.gemini import summarize_transcript
# from app.scrapers.youtube import fetch_transcript
# from app.storage.videos import (
#     get_video,
#     update_summary,
#     update_transcript,
# )


# def process_video(video_id: str) -> bool:
#     """
#     Process an existing database video.

#     Fetches its transcript and generates a Gemini summary.

#     Returns
#     -------
#     bool
#         True if both transcript and summary succeed.
#     """

#     video = get_video(video_id)

#     if video is None:
#         raise ValueError(
#             f"Video '{video_id}' not found in database."
#         )

#     print(f"\nProcessing: {video.title}")

#     # --------------------------------------------------
#     # Transcript
#     # --------------------------------------------------

#     try:

#         transcript = fetch_transcript(
#             video.video_id
#         )

#         update_transcript(
#             video_id=video.video_id,
#             transcript=transcript,
#             status="success",
#         )

#         print(
#             f"Transcript saved "
#             f"({len(transcript)} characters)"
#         )

#     except Exception as error:

#         update_transcript(
#             video_id=video.video_id,
#             transcript=None,
#             status="failed",
#         )

#         print(
#             f"Transcript failed: {error}"
#         )

#         return False

#     # --------------------------------------------------
#     # Gemini summary
#     # --------------------------------------------------

#     try:

#         summary = summarize_transcript(
#             transcript=transcript,
#             title=video.title,
#         )

#         update_summary(
#             video_id=video.video_id,
#             summary=summary,
#             status="success",
#         )

#         print(
#             f"Summary saved "
#             f"({len(summary)} characters)"
#         )

#     except Exception as error:

#         update_summary(
#             video_id=video.video_id,
#             summary=None,
#             status="failed",
#         )

#         print(
#             f"Summary failed: {error}"
#         )

#         return False

#     return True


from app.llm.gemini import summarize_transcript
from app.scrapers.youtube import (
    fetch_recent_videos,
    fetch_transcript,
)
from app.storage.videos import (
    get_video,
    save_video,
    update_summary,
    update_transcript,
    video_exists,
)


# def process_video(video_id: str) -> bool:
#     """
#     Process an existing database video.

#     Fetches its transcript and generates a Gemini summary.

#     Returns
#     -------
#     bool
#         True if transcript and summary succeed.
#     """

#     video = get_video(video_id)

#     if video is None:
#         raise ValueError(
#             f"Video '{video_id}' not found in database."
#         )

#     print(f"\nProcessing: {video.title}")

#     # --------------------------------------------------
#     # Transcript
#     # --------------------------------------------------

#     try:

#         transcript = fetch_transcript(
#             video.video_id
#         )

#         update_transcript(
#             video_id=video.video_id,
#             transcript=transcript,
#             status="success",
#         )

#         print(
#             f"Transcript saved "
#             f"({len(transcript)} characters)"
#         )

#     except Exception as error:

#         update_transcript(
#             video_id=video.video_id,
#             transcript=None,
#             status="failed",
#         )

#         print(
#             f"Transcript failed: {error}"
#         )

#         return False

#     # --------------------------------------------------
#     # Gemini summary
#     # --------------------------------------------------

#     try:

#         summary = summarize_transcript(
#             transcript=transcript,
#             title=video.title,
#         )

#         update_summary(
#             video_id=video.video_id,
#             summary=summary,
#             status="success",
#         )

#         print(
#             f"Summary saved "
#             f"({len(summary)} characters)"
#         )

#     except Exception as error:

#         update_summary(
#             video_id=video.video_id,
#             summary=None,
#             status="failed",
#         )

#         print(
#             f"Summary failed: {error}"
#         )

#         return False

#     return True

def process_video(video_id: str) -> bool:
    """
    Process a video using its current database state.

    Retries only the pipeline stages that have not succeeded.

    Returns
    -------
    bool
        True if transcript and summary are both successful.
    """

    video = get_video(video_id)

    if video is None:
        raise ValueError(
            f"Video '{video_id}' not found in database."
        )

    print(f"\nProcessing: {video.title}")

    # ---------------------------------------------------------
    # Step 1: Transcript
    # ---------------------------------------------------------

    if video.transcript_status == "success":
        print("Transcript already available. Skipping.")

    else:
        print("Fetching transcript...")

        try:
            transcript = fetch_transcript(video.video_id)

            update_transcript(
                video_id=video.video_id,
                transcript=transcript,
                status="success",
            )

            # Keep local object in sync
            video.transcript = transcript
            video.transcript_status = "success"

            print(
                f"Transcript saved "
                f"({len(transcript)} characters)"
            )

        except Exception as error:
            update_transcript(
                video_id=video.video_id,
                transcript=None,
                status="failed",
            )

            print(f"Transcript failed: {error}")
            return False

    # ---------------------------------------------------------
    # Step 2: Summary
    # ---------------------------------------------------------

    if video.summary_status == "success":
        print("Summary already available. Skipping.")
        return True

    print("Generating Gemini summary...")

    try:
        summary = summarize_transcript(
            transcript=video.transcript,
            title=video.title,
        )

        update_summary(
            video_id=video.video_id,
            summary=summary,
            status="success",
        )

        print(
            f"Summary saved "
            f"({len(summary)} characters)"
        )

    except Exception as error:
        update_summary(
            video_id=video.video_id,
            summary=None,
            status="failed",
        )

        print(f"Summary failed: {error}")
        return False

    return True


def ingest_youtube_channel(
    channel_id: str,
    lookback_hours: int = 24,
    max_items: int | None = None,
) -> int:
    """
    Fetch recent YouTube videos and process new videos.

    Pipeline:
        RSS → PostgreSQL → Transcript → Gemini → PostgreSQL

    Returns
    -------
    int
        Number of newly discovered videos.
    """

    print(
        f"\nFetching videos from channel: {channel_id}"
    )

    videos = fetch_recent_videos(
        channel_id=channel_id,
        lookback_hours=lookback_hours,
    )

    print(
        f"Found {len(videos)} recent videos."
    )

    if max_items is not None and len(videos) > max_items:
        videos = sorted(
            videos,
            key=lambda video: video["published_at"],
            reverse=True,
        )[:max_items]

        print(f"Processing only the newest {max_items}.")

    new_videos = 0
    successful = 0
    failed = 0

    for video in videos:

        video_id = video["video_id"]
        title = video["title"]

        # --------------------------------------------------
        # Deduplication
        # --------------------------------------------------

        if video_exists(video_id):

            print(
                f"\nSkipping existing video: {title}"
            )

            continue

        # --------------------------------------------------
        # Save metadata
        # --------------------------------------------------

        save_video(
            video_id=video_id,
            channel_id=channel_id,
            title=title,
            url=video["url"],
            published_at=video["published_at"],
        )

        new_videos += 1

        print(
            f"\nNew video discovered: {title}"
        )

        # --------------------------------------------------
        # Process transcript + summary
        # --------------------------------------------------

        try:

            success = process_video(video_id)

            if success:
                successful += 1
            else:
                failed += 1

        except Exception as error:

            failed += 1

            print(
                f"Unexpected processing error: {error}"
            )

    # ------------------------------------------------------
    # Final statistics
    # ------------------------------------------------------

    print("\n" + "=" * 50)
    print("INGESTION COMPLETE")
    print("=" * 50)

    print(f"Videos discovered : {len(videos)}")
    print(f"New videos        : {new_videos}")
    print(f"Successful        : {successful}")
    print(f"Failed            : {failed}")
    print("=" * 50)

    return new_videos