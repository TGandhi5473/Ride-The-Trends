import os
import requests
from atproto import Client

class BronzeScraper:
    def __init__(self):
        # 1. YouTube Setup
        self.yt_key = os.getenv("YOUTUBE_API_KEY")
        
        # We keep this as your "Fixed" map for targeted YouTube pulls
        self.yt_category_map = {
            "Film & Animation": "1",
            "Autos & Vehicles": "2",
            "Music": "10",
            "Pets & Animals": "15",
            "Sports": "17",
            "Gaming": "20",
            "People & Blogs": "22",
            "Comedy": "23",
            "Entertainment": "24",
            "News & Politics": "25",
            "Howto & Style": "26",
            "Education": "27",
            "Science & Technology": "28"
        }

        # 2. Bluesky Setup
        self.bsky_client = Client()
        self.bsky_client.login(
            os.getenv("BSKY_HANDLE"), 
            os.getenv("BSKY_PASSWORD")
        )

    # --- YouTube Methods ---

    def fetch_youtube_by_category(self, category_name):
        """Fetches top 50 videos for a specific YouTube category."""
        cat_id = self.yt_category_map.get(category_name)
        if not cat_id:
            print(f"Category {category_name} not found in map.")
            return []

        url = (
            f"https://www.googleapis.com/youtube/v3/videos?"
            f"part=snippet,statistics&chart=mostPopular&regionCode=US"
            f"&videoCategoryId={cat_id}&maxResults=50&key={self.yt_key}"
        )
        response = requests.get(url)
        return response.json().get('items', [])

    def fetch_youtube_global_popular(self):
        """Fetches the overall top 50 across ALL categories in one call."""
        url = (
            f"https://www.googleapis.com/youtube/v3/videos?"
            f"part=snippet,statistics&chart=mostPopular&regionCode=US"
            f"&maxResults=50&key={self.yt_key}"
        )
        response = requests.get(url)
        return response.json().get('items', [])

    # --- Bluesky Methods ---

    def fetch_bluesky_topics(self):
        """
        Fetches dynamic trending topics/hashtags from Bluesky.
        Returns a list of topic names (strings).
        """
        try:
            # Using the unspecced trending endpoint to get what's 'Hot' right now
            trends = self.bsky_client.app.bsky.unspecced.get_trending_topics()
            # Returns a list of trending topic objects; we just want the names
            return [t.topic for t in trends.topics]
        except Exception as e:
            print(f"Error fetching Bluesky trends: {e}")
            return []

    def fetch_bluesky_by_topic(self, topic, max_results=100):
        """
        Fetches posts for a specific topic using pagination.
        """
        all_posts = []
        cursor = None
        
        try:
            while len(all_posts) < max_results:
                params = {'q': topic, 'limit': 100, 'cursor': cursor}
                fetched = self.bsky_client.app.bsky.feed.search_posts(params=params)
                
                all_posts.extend(fetched.posts)

                if not fetched.cursor or len(fetched.posts) == 0:
                    break
                    
                cursor = fetched.cursor
            
            return all_posts[:max_results]
        except Exception as e:
            print(f"Error searching Bluesky for {topic}: {e}")
            return []
