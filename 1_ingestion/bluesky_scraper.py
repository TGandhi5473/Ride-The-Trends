from atproto import Client
from .base_scraper import BaseScraper

class BlueskyScraper(BaseScraper):
    def __init__(self):
        super().__init__(platform="bluesky")
        self.client = Client()
        # Neon Note: These will be GitHub Secrets in production
        self.client.login(os.getenv("BSKY_HANDLE"), os.getenv("BSKY_PASSWORD"))

    def fetch_trending(self, topic: str, limit: int = 10):
        # Searching the firehose for relevant discourse
        response = self.client.app.bsky.feed.search_posts(params={'q': topic, 'limit': limit})
        return response.posts

    def format_payload(self, post):
        return {
            "source_id": post.uri,
            "text": post.record.text,
            "author": post.author.handle,
            "created_at": post.record.created_at,
            "like_count": post.like_count,
            "reply_count": post.reply_count
        }
