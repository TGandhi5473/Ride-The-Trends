from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from core import Config, QuotaExceededError
from .base_scraper import BaseScraper

class YouTubeScraper(BaseScraper):
    def __init__(self):
        super().__init__(platform="youtube")
        
        # Pull from centralized Config
        self.api_key = Config.YOUTUBE_API_KEY
        
        if not self.api_key:
            self.logger.error("Missing YouTube API Key in Config.")
            self.is_active = False
            return

        try:
            self.youtube = build("youtube", "v3", developerKey=self.api_key)
        except Exception as e:
            self.logger.error(f"Failed to initialize YouTube client: {e}")
            self.is_active = False

    def fetch_trending(self, topic: str, limit: int = 10):
        """Fetch popular videos based on view count for a specific topic."""
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

        except HttpError as e:
            # Hardened Quota Check: Look for 403 Forbidden (Standard for Quota Exceeded)
            if e.resp.status in [403, 429]:
                self.is_active = False
                self.logger.critical("🛑 YouTube Quota Exceeded or Rate Limited.")
                raise QuotaExceededError("youtube")
            raise

        except Exception as e:
            self.logger.error(f"Unexpected YouTube API error: {e}")
            raise

    def format_payload(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Standardizing YouTube specific JSON for the Bronze layer."""
        snippet = item.get("snippet", {})
        return {
            "source_id": item.get("id", {}).get("videoId"),
            "title": snippet.get("title"),
            "description": snippet.get("description"),
            "channel": snippet.get("channelTitle"),
            "published_at": snippet.get("publishedAt"),
            "thumbnails": snippet.get("thumbnails", {}).get("high", {}).get("url")
        }
