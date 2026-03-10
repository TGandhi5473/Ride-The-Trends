import os
import torch
import numpy as np
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification

class SocialClassifier:
    def __init__(self):
        # 1. Priority Loading Logic
        self.local_path = "./app/models/refined_bert_v2"
        self.base_model = "distilbert-base-uncased"
        self.device = 0 if torch.cuda.is_available() else -1  # Pipeline uses 0 for GPU, -1 for CPU

        if os.path.isdir(self.local_path) and os.path.exists(f"{self.local_path}/config.json"):
            print(f"🎯 Loading Fine-Tuned Model: {self.local_path}")
            self.current_model = self.local_path
        else:
            print(f"🌐 Falling back to Base Model: {self.base_model}")
            self.current_model = self.base_model

        # 2. Initialize Pipelines
        # Standard classification pipeline
        self.classifier = pipeline(
            "text-classification", 
            model=self.current_model, 
            device=self.device
        )
        
        # Feature extraction for the 768-dim vectors (Gold Layer)
        self.feature_extractor = pipeline(
            "feature-extraction", 
            model=self.current_model, 
            device=self.device
        )

        # Labels mapping (Consistent with YouTube API and Retraining Script)
        self.label_map = {0: "Finance", 1: "Tech", 2: "Gaming", 3: "Politics", 4: "OTHER"}

    def predict_batch_with_vectors(self, texts):
        """
        Enrichment Layer: Returns labels, confidence, and 768-dim embeddings.
        Essential for 'Semantic Briefing' and 'Audit Hub'.
        """
        if not texts:
            return [], [], []

        # 1. Run Classification
        # return_all_scores=True allows us to capture confidence levels
        raw_results = self.classifier(texts)
        labels = [res['label'] for res in raw_results]
        confidences = [res['score'] for res in raw_results]

        # 2. Get Mean-Pooled Embeddings
        # raw_features shape: [batch, tokens, 768]
        raw_features = self.feature_extractor(texts)
        
        embeddings = []
        for feature in raw_features:
            tensor_feat = torch.tensor(feature)
            # Mean-pooling across the token dimension to get a fixed-size vector
            mean_vec = torch.mean(tensor_feat, dim=1).squeeze().numpy()
            embeddings.append(mean_vec)
            
        return labels, confidences, embeddings

    def classify_and_filter(self, texts, threshold=0.45):
        """
        Adds the 'Other' logic: If confidence is too low, label as 'OTHER'
        to trigger the Niche Discovery tab in the Audit Hub.
        """
        labels, confs, vectors = self.predict_batch_with_vectors(texts)
        
        final_labels = []
        for label, conf in zip(labels, confs):
            if conf < threshold:
                final_labels.append("OTHER")
            else:
                final_labels.append(label)
                
        return final_labels, confs, vectors
