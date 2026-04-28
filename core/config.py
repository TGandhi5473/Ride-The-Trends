import os

class Config:
    # --- Database & Scrapers ---
    DATABASE_URL = os.getenv("DATABASE_URL")
    YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
    BSKY_HANDLE = os.getenv("BSKY_HANDLE")
    BSKY_PASSWORD = os.getenv("BSKY_PASSWORD")

    # --- LLM Settings ---
    # Default to local Ollama. If running in a container, use host.docker.internal
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:1b") # Fast & tiny
    
    # Optional Cloud fallback
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

    @classmethod
    def validate_config(cls):
        critical_keys = ["DATABASE_URL", "YOUTUBE_API_KEY"]
        missing = [key for key in critical_keys if not getattr(cls, key)]
        if missing:
            raise EnvironmentError(f"🚨 Missing critical secrets: {', '.join(missing)}")

Config.validate_config()
