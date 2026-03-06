import os
from keybert import KeyBERT
from sentence_transformers import SentenceTransformer

class AntiSlopProcessor:
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        """
        Initializes local NLP models. 
        all-MiniLM-L6-v2 produces 384-dimensional embeddings (matches our DB schema).
        """
        self.model = SentenceTransformer(model_name)
        self.kw_model = KeyBERT(model=self.model)

    def generate_embedding(self, text):
        """
        Generates a vector embedding for semantic search in the Hot/Cold DBs.
        """
        return self.model.encode(text).tolist()

    def extract_anti_slop_keywords(self, text):
        """
        Extracts high-utility keywords using MMR (Maximal Marginal Relevance).
        This reduces generic 'slop' by maximizing diversity among keywords.
        """
        keywords = self.kw_model.extract_keywords(
            text, 
            keyphrase_ngram_range=(1, 2), 
            stop_words='english', 
            use_mmr=True, 
            diversity=0.7,
            top_n=5
        )
        # Returns just the string keywords, ignoring the score tuples
        return [k[0] for k in keywords]

if __name__ == "__main__":
    # Quick Test
    processor = AntiSlopProcessor()
    sample_text = "The decentralized nature of the AT Protocol is driving a new wave of authentic social interaction."
    
    print(f"Keywords: {processor.extract_anti_slop_keywords(sample_text)}")
    print(f"Embedding Length: {len(processor.generate_embedding(sample_text))}")
