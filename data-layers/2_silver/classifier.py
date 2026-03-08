import torch
from transformers import pipeline

class SocialClassifier:
    def __init__(self):
        # Using a model that supports both classification and feature extraction
        self.model_name = "distilbert-base-uncased"
        self.pipe = pipeline("text-classification", model=self.model_name)
        self.feature_extractor = pipeline("feature-extraction", model=self.model_name)
        
        # Expanded based on YouTube API Categories (1, 10, 17, 20, 25, 27, 28)
        self.categories = [
            "Finance", "Tech", "Gaming", "Politics", "Entertainment", 
            "Education", "Science & Technology", "Sports", "Music", 
            "Howto & Style", "Autos & Vehicles", "OTHER"
        ]

    def predict_batch(self, texts):
        """Standard classification for simple labeling."""
        results = self.pipe(texts)
        return [res['label'] for res in results]

    def predict_batch_with_vectors(self, texts):
        """
        NEW: Returns both labels and 768-dim embeddings.
        Essential for the 'Semantic Briefing' Gold Layer feature.
        """
        # 1. Get Labels
        labels = self.predict_batch(texts)
        
        # 2. Get Mean-Pooled Embeddings
        # Feature extraction returns [batch, tokens, 768]
        raw_features = self.feature_extractor(texts)
        
        embeddings = []
        for feature in raw_features:
            # We take the mean across the token dimension (dim 1) 
            # to get a single 768-dim vector per text
            tensor_feat = torch.tensor(feature)
            mean_vec = torch.mean(tensor_feat, dim=1).squeeze()
            embeddings.append(mean_vec.numpy())
            
        return labels, embeddings
