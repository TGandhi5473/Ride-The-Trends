import os
import psycopg2
import requests
from dotenv import load_dotenv

load_dotenv()

def test_db():
    print("--- Testing Database Connection ---")
    try:
        conn = psycopg2.connect(os.getenv("HOT_DB_URL"))
        cur = conn.cursor()
        cur.execute("SELECT version();")
        db_version = cur.fetchone()
        print(f"✅ Connected to: {db_version}")
        
        # Check if basic schema exists
        cur.execute("SELECT to_regclass('public.bronze_social_posts');")
        exists = cur.fetchone()[0]
        if exists:
            print("✅ Bronze table found.")
        else:
            print("❌ Table 'bronze_social_posts' not found. Did you run schema.sql?")
        
        cur.close()
        conn.close()
    except Exception as e:
        print(f"❌ DB Connection Failed: {e}")
        exit(1)

def test_youtube():
    print("\n--- Testing YouTube API ---")
    api_key = os.getenv("YOUTUBE_API_KEY")
    url = f"https://www.googleapis.com/youtube/v3/videos?part=snippet&id=Ks-_Mh1QhMc&key={api_key}"
    
    response = requests.get(url)
    if response.status_code == 200:
        print("✅ YouTube API Authenticated.")
    else:
        print(f"❌ YouTube API Failed: {response.status_code} - {response.text}")
        exit(1)

if __name__ == "__main__":
    test_db()
    test_youtube()
    print("\n🚀 ALL SYSTEMS GO: Pipeline is ready for production run.")
