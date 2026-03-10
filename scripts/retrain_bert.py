import sys
import torch
from pathlib import Path
from transformers import (
    DistilBertForSequenceClassification, 
    Trainer, 
    TrainingArguments, 
    DistilBertTokenizer,
    AutoConfig
)

# Ensure the root directory is in the path so we can import config.py
sys.path.append(str(Path(__file__).parent.parent))

from utils.feedback_processor import get_training_data
import config  # Central Source of Truth

# 1. Helper Dataset Class
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

def run_retraining():
    # Fetch human-corrected data from the database
    df = get_training_data()
    
    # 💡 50 is our 'Golden Number' from config.py
    if len(df) < config.TRAINING_THRESHOLD:
        print(f"⌛ Current samples: {len(df)}. Wait for {config.TRAINING_THRESHOLD} before retraining.")
        return

    print(f"🔄 Retraining initiated with {len(df)} samples...")

    # Load tokenizer from the current active model (base or previously refined)
    tokenizer = DistilBertTokenizer.from_pretrained(config.get_active_model_path())
    
    # --- 🏷️ PRO MOVE: Dynamic Label Mapping ---
    # This embeds your 'Tech', 'Finance', etc. labels into the model metadata
    model_config = AutoConfig.from_pretrained(
        config.BASE_MODEL_NAME,
        num_labels=len(config.LABEL_MAP),
        id2label={str(k): v for k, v in config.LABEL_MAP.items()},
        label2id={v: k for k, v in config.LABEL_MAP.items()}
    )

    # Load the model weights
    model = DistilBertForSequenceClassification.from_pretrained(
        config.get_active_model_path(), 
        config=model_config
    )

    # --- ⚖️ FREEZE BASE LAYERS ---
    # Only train the classification head. This makes it '0-cost' on CPU 
    # and prevents 'Catastrophic Forgetting' of base language patterns.
    for name, param in model.distilbert.named_parameters():
        param.requires_grad = False

    # 2. Tokenization using central constants
    encodings = tokenizer(
        df['text'].tolist(), 
        truncation=True, 
        padding=True, 
        max_length=config.MAX_SEQ_LENGTH
    )
    
    train_dataset = FeedbackDataset(encodings, df['label'].tolist())

    # 3. Training Arguments (Optimized for 2026 local hardware/CI)
    training_args = TrainingArguments(
        output_dir="./results",
        num_train_epochs=config.EPOCHS,
        per_device_train_batch_size=config.BATCH_SIZE,
        warmup_steps=10,
        weight_decay=0.01,
        logging_dir="./logs",
        logging_steps=5,
        use_cpu=True, # Safety for local trial runs and GitHub Actions
        report_to="none" # Prevents cloud logging clutter
    )

    # 4. The Trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
    )

    print("🚀 Fine-tuning DistilBERT on Human Feedback...")
    trainer.train()

    # 5. Save the 'Smarter' Model
    # The Classifier will now automatically detect this in config.get_active_model_path()
    save_path = str(config.REFINED_MODEL_PATH)
    model.save_pretrained(save_path)
    tokenizer.save_pretrained(save_path)
    
    print(f"✅ Model updated and saved to {save_path}")

if __name__ == "__main__":
    run_retraining()
