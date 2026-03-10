import os
import torch
import numpy as np
from transformers import pipeline
from config import get_active_model_path, LABEL_MAP, MAX_SEQ_LENGTH

class SocialClassifier:
    def __init__(self):
        # Use the dynamic path from config.py
        self.current_model = get_active_model_path()
        
        # --- 🖥️ Device Detection (2026 Hardware standards) ---
        if torch.cuda.is_available():
            self.device = 0 # NVIDIA GPU
        elif torch.backends.mps.is_available():
            self.device = "mps" # Apple Silicon (M1/M2/M3/M4)
        else:
            self.device = -1 # CPU Fallback
            
        print(f"🎯 Loading Social Intelligence Model: {self.current_model} on {self.device}")

        # 1. Standard Classification Pipeline
        # We specify the LABEL_MAP in the pipeline to ensure 'LABEL_0' becomes 'Tech'
        self.classifier = pipeline(
            "text-classification", 
            model=self.current_model, 
            device=self.device,
            truncation=True,
            max_length=MAX_SEQ_LENGTH
        )
        
        # 2. Feature Extraction (For Semantic/Vector Search)
        # Using the same model ensures the vector space stays aligned with the labels
        self.feature_extractor = pipeline(
            "feature-extraction", 
            model=self.current_model, 
            device=self.device,
            truncation=True,
            max_length=MAX_SEQ_LENGTH
        )

    def _format_label(self, raw_label):
        """
        Safety utility to map 'LABEL_X' strings to human-readable names 
        if the model was saved without a label dictionary.
        """
        if raw_label in LABEL_MAP.values():
            return raw_label
        
        # Handle 'LABEL_0' -> 0 -> 'Tech'
        try:
            label_id = int(raw_label.split('_')[-1])
            return LABEL_MAP.get(label_id, "Other")
        except (ValueError, IndexError):
            return "Other"

    def predict_batch_with_vectors(self, texts):
        """
        Core Inference Engine: Returns (Labels, Confidences, Embeddings)
        """
        if not texts:
            return [], [], []

        # Step A: Batch Classification
        # Batching at 16 is the 'sweet spot' for most local CPUs/GPUs in 2026
        raw_results = self.classifier(texts, batch_size=16)
        
        labels = [self._format_label(res['label']) for res in raw_results]
        confidences = [res['score'] for res in raw_results]

        # Step B: Optimized Embedding Extraction (The CLS Token Strategy)
        # We take the [CLS] token (index 0) because it contains the 
        # aggregated semantic summary of the entire sentence.
        raw_features = self.feature_extractor(texts, batch_size=16)
        
        embeddings = []
        for feature in raw_features:
            # feature shape: [1, seq_len, 768]
            # [0][0] selects the first token (CLS) vector
            cls_vector = np.array(feature[0][0]) 
            embeddings.append(cls_vector)
            
        return labels, confidences, embeddings

if __name__ == "__main__":
    # Quick Integration Test
    clf = SocialClassifier()
    test_texts = ["Bitcoin price is surging", "New GPU architecture announced by NVIDIA"]
    l, c, e = clf.predict_batch_with_vectors(test_texts)
    
    for text, label, conf in zip(test_texts, l, c):
        print(f"Text: {text} | Result: {label} ({conf:.2%})")
