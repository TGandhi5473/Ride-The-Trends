import sys
import torch
import pandas as pd
from pathlib import Path
from transformers import (
    DistilBertForSequenceClassification, 
    Trainer, 
    TrainingArguments, 
    DistilBertTokenizer,
    AutoConfig
)

# Aligning paths to the new structure
sys.path.append(str(Path(__file__).parent.parent))

from core import Config, get_neon_engine, setup_logger

logger = setup_logger("BERT-Retrainer")

class FeedbackDataset(torch.utils.data.Dataset):
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
    """Fetch human-corrected feedback from Neon."""
    engine = get_neon_engine()
    query = "SELECT text, label_id as label FROM gold.human_feedback WHERE used_for_training = FALSE"
    try:
        df = pd.read_sql(query, engine)
        return df
    except Exception as e:
        logger.error(f"Failed to fetch training data: {e}")
        return pd.DataFrame()

def run_retraining():
    df = get_training_data()
    
    # Use Config constants instead of old 'config.py'
    if len(df) < Config.TRAINING_THRESHOLD:
        logger.info(f"⌛ Current samples: {len(df)}. Threshold: {Config.TRAINING_THRESHOLD}. Skipping.")
        return

    logger.info(f"🔄 Retraining initiated with {len(df)} samples...")

    # Path management using Config
    model_path = Config.get_active_model_path()
    tokenizer = DistilBertTokenizer.from_pretrained(model_path)
    
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

    # Freeze base layers for CPU-friendly training
    for name, param in model.distilbert.named_parameters():
        param.requires_grad = False

    encodings = tokenizer(
        df['text'].tolist(), 
        truncation=True, 
        padding=True, 
        max_length=Config.MAX_SEQ_LENGTH
    )
    
    train_dataset = FeedbackDataset(encodings, df['label'].tolist())

    training_args = TrainingArguments(
        output_dir="./results",
        num_train_epochs=3, # Adjusted for small feedback batches
        per_device_train_batch_size=8,
        warmup_steps=10,
        weight_decay=0.01,
        logging_dir="./logs",
        use_cpu=True,
        report_to="none"
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
    )

    logger.info("🚀 Fine-tuning DistilBERT on Human Feedback...")
    trainer.train()

    # Save to the Refined path defined in Config
    save_path = str(Config.REFINED_MODEL_PATH)
    model.save_pretrained(save_path)
    tokenizer.save_pretrained(save_path)
    
    # IMPORTANT: Mark data as used in DB so we don't overfit on the same samples
    # (Logic: UPDATE gold.human_feedback SET used_for_training = TRUE)
    
    logger.info(f"✅ Model updated and saved to {save_path}")

if __name__ == "__main__":
    run_retraining()
