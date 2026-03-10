import torch
from transformers import (
    DistilBertForSequenceClassification, 
    Trainer, 
    TrainingArguments, 
    DistilBertTokenizer
)
from utils.feedback_processor import get_training_data

# 1. Helper Dataset Class (Required for the Trainer)
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
    df = get_training_data()
    
    # 💡 50 is the "golden number" to prevent the model from getting 
    # 'biased' by just one or two weird examples.
    if len(df) < 50:
        print(f"⌛ Current samples: {len(df)}. Wait for 50 before retraining.")
        return

    model_name = "distilbert-base-uncased"
    tokenizer = DistilBertTokenizer.from_pretrained(model_name)
    
    # Load model with 4 labels (matching your label_map in feedback_processor)
    model = DistilBertForSequenceClassification.from_pretrained(
        model_name, 
        num_labels=4
    )

    # --- ⚖️ PRO MOVE: FREEZE BASE LAYERS ---
    # We only train the classifier head. This makes it '0-cost' on CPU 
    # and prevents 'Catastrophic Forgetting'.
    for name, param in model.distilbert.named_parameters():
        param.requires_grad = False

    # 2. Tokenization
    encodings = tokenizer(
        df['text'].tolist(), 
        truncation=True, 
        padding=True, 
        max_length=128 # Keep it short for faster training
    )
    
    train_dataset = FeedbackDataset(encodings, df['label'].tolist())

    # 3. Training Arguments
    training_args = TrainingArguments(
        output_dir="./results",
        num_train_epochs=3,
        per_device_train_batch_size=16, # Larger batch size since we froze layers
        warmup_steps=10,
        weight_decay=0.01,
        logging_dir="./logs",
        logging_steps=5,
        use_cpu=True # Force CPU to avoid GPU OOM errors on local trial runs
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
    # Your Classifier will now load from this path in your main app
    model.save_pretrained("./app/models/refined_bert_v2")
    tokenizer.save_pretrained("./app/models/refined_bert_v2")
    
    print("✅ Model updated and saved to ./app/models/refined_bert_v2")

if __name__ == "__main__":
    run_retraining()
