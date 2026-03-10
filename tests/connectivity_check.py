import os
import psycopg2
import requests
from dotenv import load_dotenv

load_dotenv()

def test_db():
    print("--- 🗄️ Testing Database & pgvector ---")
    try:
        conn = psycopg2.connect(os.getenv("HOT_DB_URL"), connect_timeout=5)
        cur = conn.cursor()
        
        # 1. Check pgvector extension (Required for Gold Layer)
        cur.execute("SELECT extname FROM pg_extension WHERE extname = 'vector';")
        vector_exists = cur.fetchone()
        if vector_exists:
            print("✅ pgvector extension is enabled.")
        else:
            print("❌ pgvector NOT found. Run 'CREATE EXTENSION vector;' in your DB.")

        # 2. Check if Medallion schema exists
        cur.execute("SELECT to_regclass('public.bronze_social_posts');")
        exists = cur.fetchone()[0]
        if exists:
            print("✅ Medallion schema (Bronze) detected.")
        else:
            print("⚠️ Table 'bronze_social_posts' not found. Ensure 3_gold/schema.sql was run.")
        
        cur.close()
        conn.close()
    except Exception as e:
        print(f"❌ DB Connection Failed: {e}")
        exit(1)

def test_external_apis():
    print("\n--- 🌐 Testing API Authentication ---")
    
    # YouTube Check
    yt_key = os.getenv("YOUTUBE_API_KEY")
    yt_url = f"https://www.googleapis.com/youtube/v3/videos?part=snippet&id=Ks-_Mh1QhMc&key={yt_key}"
    yt_res = requests.get(yt_url, timeout=5)
    
    if yt_res.status_code == 200:
        print("✅ YouTube API: Authorized.")
    else:
        print(f"❌ YouTube API Failed: {yt_res.status_code}")
        exit(1)

    # Bluesky Check (Smoke test for handle existence)
    bsky_handle = os.getenv("BSKY_HANDLE")
    if bsky_handle:
        bsky_url = f"https://bsky.social/xrpc/com.atproto.identity.resolveHandle?handle={bsky_handle}"
        bsky_res = requests.get(bsky_url, timeout=5)
        if bsky_res.status_code == 200:
            print(f"✅ Bluesky: Handle '{bsky_handle}' resolved.")
        else:
            print(f"❌ Bluesky: Could not resolve handle '{bsky_handle}'.")
            exit(1)

if __name__ == "__main__":
    test_db()
    test_external_apis()
    print("\n🚀 ALL SYSTEMS GO: Environment is verified for production run.")
