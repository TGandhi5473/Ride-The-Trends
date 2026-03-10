import os
from pathlib import Path

# --- PROJECT PATHS ---
ROOT_DIR = Path(__file__).parent
MODEL_DIR = ROOT_DIR / "app" / "models"
BASE_MODEL_NAME = "distilbert-base-uncased"
REFINED_MODEL_PATH = MODEL_DIR / "refined_bert_v2"

# --- CATEGORY SCHEMA (The "Source of Truth") ---
# These IDs MUST match the integers expected by the BERT Head
LABEL_MAP = {
    0: "Tech",
    1: "Finance",
    2: "Lifestyle",
    3: "Other" # The 'Other' bucket triggers the HITL/Retraining loop
}

# Inverse map for UI display
ID_TO_LABEL = LABEL_MAP
LABEL_TO_ID = {v: k for k, v in LABEL_MAP.items()}

# --- ML HYPERPARAMETERS ---
TRAINING_THRESHOLD = 50  # Minimum samples needed in silver_human_labels to trigger retrain
MAX_SEQ_LENGTH = 128
BATCH_SIZE = 16
EPOCHS = 3

# --- DB SETTINGS ---
# Using ENV variables for security, but providing defaults for local dev
HOT_DB_URL = os.getenv("HOT_DB_URL", "postgresql://user:pass@localhost:5432/trends_hot")

def get_active_model_path():
    """Returns the refined model if it exists, otherwise the base BERT."""
    if REFINED_MODEL_PATH.exists():
        return str(REFINED_MODEL_PATH)
    return BASE_MODEL_NAME
