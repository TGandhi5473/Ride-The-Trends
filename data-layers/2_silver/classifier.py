import os
import torch
import numpy as np
from transformers import pipeline

class SocialClassifier:
    def __init__(self):
        self.local_path = "./app/models/refined_bert_v2"
        self.base_model = "distilbert-base-uncased"
        # Check for CUDA (NVIDIA) or MPS (Apple Silicon)
        if torch.cuda.is_available():
            self.device = 0
        elif torch.backends.mps.is_available():
            self.device = "mps"
        else:
            self.device = -1

        self.current_model = self.local_path if (os.path.isdir(self.local_path) and os.path.exists(f"{self.local_path}/config.json")) else self.base_model
        print(f"🎯 Model Target: {self.current_model}")

        # Standard classification pipeline
        self.classifier = pipeline(
            "text-classification", 
            model=self.current_model, 
            device=self.device,
            truncation=True,
            max_length=512
        )
        
        # Feature extraction (using the CLS token strategy)
        self.feature_extractor = pipeline(
            "feature-extraction", 
            model=self.current_model, 
            device=self.device,
            truncation=True
        )

    def predict_batch_with_vectors(self, texts):
        if not texts:
            return [], [], []

        # 1. Classification with Batching
        raw_results = self.classifier(texts, batch_size=16)
        labels = [res['label'] for res in raw_results]
        confidences = [res['score'] for res in raw_results]

        # 2. Optimized Embedding Extraction
        # We take the [CLS] token (index 0) for the most stable semantic representation
        raw_features = self.feature_extractor(texts, batch_size=16)
        
        embeddings = []
        for feature in raw_features:
            # feature shape: [1, seq_len, 768]
            # [0][0] selects the first token (CLS) of the sequence
            cls_vector = np.array(feature[0][0]) 
            embeddings.append(cls_vector)
            
        return labels, confidences, embeddings
