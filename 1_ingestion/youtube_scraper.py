import os
from googleapiclient.discovery import build
from .base_scraper import BaseScraper

class YouTubeScraper(BaseScraper):
    def __init__(self):
        super().__init__(platform="youtube")
        self.api_key = os.getenv("YOUTUBE_API_KEY")
        self.youtube = build("youtube", "v3", developerKey=self.api_key)

    def fetch_trending(self, topic: str, limit: int = 10):
        # Using search.list to find high-velocity videos for the creative team
        request = self.youtube.search().list(
            q=topic,
            part="snippet",
            type="video",
            maxResults=limit,
            order="viewCount" # Precision: Get what's actually popular
        )
        response = request.execute()
        return response.get("items", [])

    def format_payload(self, item):
        """Extracting precisely what a creative needs for a prompt."""
        snippet = item.get("snippet", {})
        return {
            "source_id": item["id"]["videoId"],
            "title": snippet.get("title"),
            "description": snippet.get("description"),
            "channel": snippet.get("channelTitle"),
            "published_at": snippet.get("publishedAt"),
            "thumbnails": snippet.get("thumbnails", {}).get("high", {}).get("url")
        }
