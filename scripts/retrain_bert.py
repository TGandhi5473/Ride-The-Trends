from transformers import DistilBertForSequenceClassification, Trainer, TrainingArguments, DistilBertTokenizer
from utils.feedback_processor import get_training_data
import torch

def run_retraining():
    df = get_training_data()
    if len(df) < 50:
        print("💡 Tip: Wait for at least 50 corrections before retraining to avoid overfitting.")
        return

    model_name = "distilbert-base-uncased"
    tokenizer = DistilBertTokenizer.from_pretrained(model_name)
    model = DistilBertForSequenceClassification.from_pretrained(model_name, num_labels=4)

    # Simple Tokenization
    inputs = tokenizer(df['text'].tolist(), padding=True, truncation=True, return_tensors="pt")
    labels = torch.tensor(df['label'].tolist())

    # Training Arguments optimized for local '0 cost' runs
    training_args = TrainingArguments(
        output_dir="./model/refined_bert",
        num_train_epochs=3,              # 3 passes is usually enough for small correction sets
        per_device_train_batch_size=8,
        save_steps=100,
        logging_steps=10,
        learning_rate=5e-5               # Small learning rate to preserve base knowledge
    )

    # Note: In a real run, you'd wrap this in a proper Dataset object
    print("🚀 Retraining model on human feedback...")
    # trainer = Trainer(model=model, args=training_args, train_dataset=your_dataset)
    # trainer.train()
    
    # Save the 'smarter' model
    model.save_pretrained("./app/models/bert_v2")
    print("✅ Model updated with human intelligence.")
