# Per-source caps keep Gemini usage inside the free-tier daily quota.
# Newest items are processed first.
MAX_ARTICLES_PER_FEED = 5
MAX_VIDEOS_PER_CHANNEL = 2


# Verify all sources any time with:  python -m app.check_sources
YOUTUBE_SOURCES = [
    {
        "name": "Sky News",
        "channel_id": "UCoMdktPbSTixAyNGwb-UYkQ",
    },
    {
        "name": "Two Minute Papers",
        "channel_id": "UCbfYPyITQ-7l4upoX8nvctg",
    },
    {
        "name": "Yannic Kilcher",
        "channel_id": "UCZHmQk67mSJgfCCTn7xBfew",
    },
    {
        "name": "Fireship",
        "channel_id": "UCsBjURrPoezykLs9EqgamOA",
    },
    {
        "name": "AI Explained",
        "channel_id": "UCNJ1Ymd5yFuUPtn21xtRbbw",
    },
]


RSS_SOURCES = [
    {
        "name": "BBC News",
        "feed_url": "https://feeds.bbci.co.uk/news/rss.xml",
    },
    {
        "name": "OpenAI News",
        "feed_url": "https://openai.com/news/rss.xml",
    },
    {
        "name": "TechCrunch AI",
        "feed_url": "https://techcrunch.com/category/artificial-intelligence/feed/",
    },
    {
        "name": "The Verge",
        "feed_url": "https://www.theverge.com/rss/index.xml",
    },
    {
        "name": "MIT Technology Review",
        "feed_url": "https://www.technologyreview.com/feed/",
    },
    {
        "name": "VentureBeat AI",
        "feed_url": "https://venturebeat.com/category/ai/feed/",
    },
    {
        "name": "Ars Technica",
        "feed_url": "https://feeds.arstechnica.com/arstechnica/index",
    },
    {
        "name": "Google AI Blog",
        "feed_url": "https://blog.google/technology/ai/rss/",
    },
    {
        "name": "Hugging Face Blog",
        "feed_url": "https://huggingface.co/blog/feed.xml",
    },
    {
        "name": "NVIDIA Blog",
        "feed_url": "https://blogs.nvidia.com/feed/",
    },
    {
        "name": "Towards Data Science",
        "feed_url": "https://towardsdatascience.com/feed",
    },
    {
        "name": "Supply Chain Dive",
        "feed_url": "https://www.supplychaindive.com/feeds/news/",
    },
]


DEFAULT_USER = {
    "email": "your_email@example.com",
    "name": "Priyansh",
    "interests": (
        "generative AI, LLMs, machine learning, "
        "supply chain analytics, data engineering"
    ),
}
