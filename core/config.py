import os
from pathlib import Path

class Config:
    # --- Database & Scrapers ---
    DATABASE_URL = os.getenv("DATABASE_URL")
    YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
    BSKY_HANDLE = os.getenv("BSKY_HANDLE")
    BSKY_PASSWORD = os.getenv("BSKY_PASSWORD")

    # --- LLM Settings (The Actor) ---
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:1b")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

    # --- BERT Settings (The Critic) ---
    # We define where the model is saved after user feedback sessions
    MODEL_DIR = Path(__file__).parent.parent / "models"
    BERT_BASE_MODEL = "bert-base-uncased"
    BERT_REFINED_PATH = MODEL_DIR / "refined_bert"
    
    # HITL Thresholds
    TRAINING_THRESHOLD = 50  # Only retrain once we have 50 new user 'likes/dislikes'
    LABEL_MAP = {0: "REJECT", 1: "APPROVE"}

    @classmethod
    def get_active_bert_path(cls):
        """
        Logic Switch: Use the 'smart' model if it exists, 
        otherwise fall back to the base model.
        """
        if cls.BERT_REFINED_PATH.exists():
            return str(cls.BERT_REFINED_PATH)
        return cls.BERT_BASE_MODEL

    @classmethod
    def validate_config(cls):
        critical_keys = ["DATABASE_URL", "YOUTUBE_API_KEY"]
        missing = [key for key in critical_keys if not getattr(cls, key)]
        if missing:
            raise EnvironmentError(f"🚨 Missing critical secrets: {', '.join(missing)}")
        
        # Ensure model directory exists for persistence
        cls.MODEL_DIR.mkdir(exist_ok=True)

Config.validate_config()
