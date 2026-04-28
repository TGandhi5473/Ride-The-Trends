from atproto import Client
from core import Config, ProviderAuthenticationError
from .base_scraper import BaseScraper

class BlueskyScraper(BaseScraper):
    def __init__(self):
        # BaseScraper handles self.platform = "bluesky" and self.is_active = True
        super().__init__(platform="bluesky")
        self.client = Client()
        
        # Use centralized Config for GitHub Secrets safety
        self.handle = Config.BSKY_HANDLE
        self.password = Config.BSKY_PASSWORD

        if not self.handle or not self.password:
            self.is_active = False
            return

        try:
            self.client.login(self.handle, self.password)
        except Exception as e:
            self.is_active = False
            # Raise custom exception for the worker to log
            raise ProviderAuthenticationError(f"Bluesky login failed: {e}")

    def fetch_trending(self, topic: str, limit: int = 10):
        """Searching the firehose for relevant discourse."""
        try:
            response = self.client.app.bsky.feed.search_posts(
                params={'q': topic, 'limit': limit}
            )
            return response.posts
        except Exception as e:
            # Bluesky doesn't have a strict public quota like YT, 
            # but we catch general API failures here.
            raise

    def format_payload(self, post):
        """Standardizing the 'Raw' JSON for the Bronze layer."""
        return {
            "source_id": post.uri,
            "text": post.record.text,
            "author": post.author.handle,
            "created_at": post.record.created_at,
            "like_count": getattr(post, 'like_count', 0),
            "reply_count": getattr(post, 'reply_count', 0)
        }
