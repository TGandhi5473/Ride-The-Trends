-- Structured Silver Table
CREATE TABLE IF NOT EXISTS silver_social_posts (
    id SERIAL PRIMARY KEY,
    platform VARCHAR(50),
    source_id VARCHAR(255) UNIQUE,        -- YouTube VideoID or Bluesky URI
    author VARCHAR(255),
    content TEXT,
    raw_category VARCHAR(100),            -- What the API said it was
    predicted_category VARCHAR(100),      -- What your BERT model says it is
    engagement_score INT DEFAULT 0,
    processed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_silver_category ON silver_social_posts(predicted_category);
