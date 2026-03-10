import time

def fetch_youtube_by_category(self, category_name):
    cat_id = self.yt_category_map.get(category_name)
    if not cat_id: return []

    url = f"https://www.googleapis.com/youtube/v3/videos?part=snippet,statistics&chart=mostPopular&regionCode=US&videoCategoryId={cat_id}&maxResults=50&key={self.yt_key}"
    
    try:
        response = requests.get(url)
        response.raise_for_status() # Check for 403/401/500 errors
        data = response.json()
        return data.get('items', [])
    except requests.exceptions.RequestException as e:
        print(f"YouTube API Failure: {e}")
        # In a real pipeline, you'd log this to your 'Quarantine' log
        return []

def fetch_bluesky_by_topic(self, topic, max_results=100):
    all_posts = []
    cursor = None
    
    try:
        while len(all_posts) < max_results:
            # Use the proper params dict
            fetched = self.bsky_client.app.bsky.feed.search_posts(
                params={'q': topic, 'limit': 100, 'cursor': cursor}
            )
            
            if not fetched.posts:
                break
                
            # CRITICAL: Convert Object to Dictionary for your JSONB column
            # .model_dump() is standard for Pydantic-based models in v2
            batch = [post.model_dump() if hasattr(post, 'model_dump') else post.__dict__ for post in fetched.posts]
            all_posts.extend(batch)

            if not fetched.cursor:
                break
            
            cursor = fetched.cursor
            time.sleep(0.1) # Respectful backoff
            
        return all_posts[:max_results]
    except Exception as e:
        print(f"Bluesky Search Error: {e}")
        return []
