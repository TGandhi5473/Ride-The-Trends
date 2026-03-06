import os
import datetime
import psycopg2
from atproto import Client
from googleapiclient.discovery import build
from dotenv import load_dotenv
from nlp_engine.processor import AntiSlopProcessor

load_dotenv()

class IngestionWorker:
    def __init__(self):
        # Initialize Databases
        self.hot_conn = psycopg2.connect(os.getenv("HOT_DB_URL"))
        self.cold_conn = psycopg2.connect(os.getenv("COLD_DB_URL"))
        
        # Initialize NLP Engine
        self.processor = AntiSlopProcessor()
        
        # Initialize API Clients
        self.bsky = Client()
        self.bsky.login(os.getenv("BSKY_HANDLE"), os.getenv("BSKY_PASSWORD"))
        self.youtube = build("youtube", "v3", developerKey=os.getenv("YOUTUBE_API_KEY"))

    def save_to_databases(self, data):
        """Writes enriched trend data to both Hot and Cold DBs."""
        # Process NLP
        embedding = self.processor.generate_embedding(data['content'])
        keywords = self.processor.extract_anti_slop_keywords(data['content'])
        
        sql = """
            INSERT INTO trends (platform, external_id, content, metadata, embedding, anti_slop_keywords, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (external_id) DO NOTHING;
        """
        params = (
            data['platform'], data['id'], data['content'], 
            data['metadata'], embedding, keywords, data['timestamp']
        )

        for conn in [self.hot_conn, self.cold_conn]:
            with conn.cursor() as cur:
                cur.execute(sql.replace("trends", "trends" if conn == self.hot_conn else "trends_archive"), params)
            conn.commit()

    def fetch_bluesky_trends(self):
        """Scrapes recent popular posts (skeets) from Bluesky."""
        print("Fetching Bluesky trends...")
        # Strategy: Search for high-engagement keywords or general global feed
        response = self.bsky.app.bsky.feed.get_timeline(algorithm="reverse-chronological", limit=20)
        for feed_view in response.feed:
            post = feed_view.post
            self.save_to_databases({
                'platform': 'bluesky',
                'id': post.uri,
                'content': post.record.text,
                'metadata': '{"author": "' + post.author.handle + '"}',
                'timestamp': post.record.created_at
            })

    def fetch_youtube_trends(self, region="US"):
        """Fetches top trending videos via YouTube Data API."""
        print(f"Fetching YouTube trends for {region}...")
        request = self.youtube.videos().list(
            part="snippet,statistics",
            chart="mostPopular",
            regionCode=region,
            maxResults=10
        )
        response = request.execute()
        for item in response.get("items", []):
            self.save_to_databases({
                'platform': 'youtube',
                'id': item['id'],
                'content': item['snippet']['title'] + " " + item['snippet']['description'],
                'metadata': '{"channel": "' + item['snippet']['channelTitle'] + '"}',
                'timestamp': datetime.datetime.utcnow()
            })

if __name__ == "__main__":
    worker = IngestionWorker()
    worker.fetch_bluesky_trends()
    worker.fetch_youtube_trends()
