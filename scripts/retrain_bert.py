import sys
import torch
import pandas as pd
from pathlib import Path
from sqlalchemy import text
from transformers import (
    DistilBertForSequenceClassification, 
    Trainer, 
    TrainingArguments, 
    DistilBertTokenizer,
    AutoConfig
)

# Aligning paths to the project root
sys.path.append(str(Path(__file__).parent.parent))

from core.config import Config
from core.database import get_neon_engine
from core.logger import logger  # Assuming standard structured logger

class FeedbackDataset(torch.utils.data.Dataset):
    """Custom Dataset for handling tokenized text and human labels."""
    def __init__(self, encodings, labels):
        self.encodings = encodings
        self.labels = labels

    def __getitem__(self, idx):
        item = {key: torch.tensor(val[idx]) for key, val in self.encodings.items()}
        item['labels'] = torch.tensor(self.labels[idx])
        return item

    def __len__(self):
        return len(self.labels)

def get_training_data():
    """Fetch human-corrected feedback from the Gold Layer."""
    engine = get_neon_engine()
    # We only pull data that hasn't been used in a previous training run
    query = "SELECT text, label_id as label FROM gold.human_feedback WHERE used_for_training = FALSE"
    try:
        df = pd.read_sql(query, engine)
        return df
    except Exception as e:
        logger.error(f"Failed to fetch training data from Neon: {e}")
        return pd.DataFrame()

def mark_data_as_used():
    """Prevents the model from overfitting by marking rows as processed in the DB."""
    engine = get_neon_engine()
    update_query = text("UPDATE gold.human_feedback SET used_for_training = TRUE WHERE used_for_training = FALSE")
    try:
        with engine.begin() as conn:
            conn.execute(update_query)
        logger.info("✅ Database updated: Feedback samples archived as 'used'.")
    except Exception as e:
        logger.error(f"Failed to update database records: {e}")

def run_retraining():
    df = get_training_data()
    
    # 1. Check Threshold (Logic Gate)
    if len(df) < Config.TRAINING_THRESHOLD:
        logger.info(f"⌛ Current samples: {len(df)}. Need: {Config.TRAINING_THRESHOLD}. Skipping retraining.")
        return

    logger.info(f"🔄 Retraining initiated with {len(df)} samples...")

    # 2. Path Management & Tokenizer
    # Uses the 'Refined' path if it exists, else the 'Base' path
    model_path = Config.get_active_model_path()
    tokenizer = DistilBertTokenizer.from_pretrained(model_path)
    
    # 3. Model Configuration (Ensures Label IDs align with UI)
    model_config = AutoConfig.from_pretrained(
        Config.BASE_MODEL_NAME,
        num_labels=len(Config.LABEL_MAP),
        id2label={str(k): v for k, v in Config.LABEL_MAP.items()},
        label2id={v: k for k, v in Config.LABEL_MAP.items()}
    )

    model = DistilBertForSequenceClassification.from_pretrained(
        model_path, 
        config=model_config
    )

    # 4. CPU-Friendly Freezing
    # We freeze the transformer backbone and only train the classification head
    for name, param in model.distilbert.named_parameters():
        param.requires_grad = False
    logger.info("❄️ DistilBERT backbone frozen. Training classification head only.")

    # 5. Tokenization
    encodings = tokenizer(
        df['text'].tolist(), 
        truncation=True, 
        padding=True, 
        max_length=Config.MAX_SEQ_LENGTH
    )
    
    train_dataset = FeedbackDataset(encodings, df['label'].tolist())

    # 6. Training Arguments (Optimized for standard laptops/CPUs)
    training_args = TrainingArguments(
        output_dir="./results",
        num_train_epochs=3,
        per_device_train_batch_size=8,
        warmup_steps=5,
        weight_decay=0.01,
        logging_dir="./logs",
        use_cpu=True,        # Force CPU to avoid CUDA errors in demo
        report_to="none"     # Disable W&B/external logging
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
    )

    # 7. Execute Fine-Tuning
    logger.info("🚀 Fine-tuning started...")
    trainer.train()

    # 8. Save Weights
    save_path = str(Config.REFINED_MODEL_PATH)
    model.save_pretrained(save_path)
    tokenizer.save_pretrained(save_path)
    
    # 9. Close the Loop
    mark_data_as_used()
    logger.info(f"✅ Success: Refined model saved to {save_path}")

if __name__ == "__main__":
    run_retraining()
