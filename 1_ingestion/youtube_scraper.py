from googleapiclient.discovery import build
from core import Config, QuotaExceededError
from .base_scraper import BaseScraper

class YouTubeScraper(BaseScraper):
    def __init__(self):
        # BaseScraper handles self.platform = "youtube" and self.is_active = True
        super().__init__(platform="youtube")
        
        # Pull from centralized Config (GitHub Secrets safe)
        self.api_key = Config.YOUTUBE_API_KEY
        
        if not self.api_key:
            self.is_active = False
            return

        try:
            self.youtube = build("youtube", "v3", developerKey=self.api_key)
        except Exception:
            self.is_active = False

    def fetch_trending(self, topic: str, limit: int = 10):
        """Precision: Get what's actually popular for the creative team."""
        try:
            request = self.youtube.search().list(
                q=topic,
                part="snippet",
                type="video",
                maxResults=limit,
                order="viewCount" 
            )
            response = request.execute()
            return response.get("items", [])
        except Exception as e:
            # Map the Google API error to our core QuotaExceededError
            if "quotaExceeded" in str(e):
                self.is_active = False
                raise QuotaExceededError("youtube")
            raise

    def format_payload(self, item):
        """Standardizing the 'Raw' JSON for the Bronze layer."""
        snippet = item.get("snippet", {})
        return {
            "source_id": item["id"].get("videoId"),
            "title": snippet.get("title"),
            "description": snippet.get("description"),
            "channel": snippet.get("channelTitle"),
            "published_at": snippet.get("publishedAt"),
            "thumbnails": snippet.get("thumbnails", {}).get("high", {}).get("url")
        }
