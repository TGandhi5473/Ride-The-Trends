from transformers import pipeline

class SocialClassifier:
    def __init__(self):
        # Load your specific model or a generic zero-shot classifier
        self.pipe = pipeline("text-classification", model="distilbert-base-uncased")
        self.categories = ["Finance", "Tech", "Gaming", "Politics", "OTHER"]

    def predict_batch(self, texts):
        """Processes multiple rows at once for speed."""
        results = self.pipe(texts)
        return [res['label'] for res in results]
