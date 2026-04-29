import requests
import openai
import torch
from transformers import pipeline, DistilBertForSequenceClassification, DistilBertTokenizer
from core.config import Config
from core.logger import logger

def get_critic_score(text: str):
    """
    Uses the refined DistilBERT model to predict the quality of a generated hook.
    Returns a score where higher = better alignment with user feedback.
    """
    try:
        model_path = Config.get_active_bert_path()
        # Load the specific refined version saved by your retraining script
        tokenizer = DistilBertTokenizer.from_pretrained(model_path)
        model = DistilBertForSequenceClassification.from_pretrained(model_path)
        
        # Create a pipeline for inference
        critic = pipeline("text-classification", model=model, tokenizer=tokenizer)
        result = critic(text)[0]
        
        # Convert label/score to a normalized probability of 'APPROVE'
        # If label is REJECT, we flip the confidence (e.g., 0.9 REJECT = 0.1 APPROVE)
        if result['label'] == 'APPROVE':
            return result['score']
        else:
            return 1 - result['score']
            
    except Exception as e:
        logger.warning(f"Critic scoring failed, defaulting to neutral (0.5): {e}")
        return 0.5

def generate_creative_assets(prompt_template: str, n_candidates: int = 3):
    """
    The Actor-Critic Loop:
    1. Generates 'n' candidates from Ollama/OpenAI.
    2. Scores them using the refined BERT model.
    3. Returns the best performing creative hook.
    """
    candidates = []

    # --- Phase 1: Generation (Actor) ---
    for _ in range(n_candidates):
        content = None
        # Try Local Ollama
        try:
            payload = {
                "model": Config.OLLAMA_MODEL,
                "prompt": f"{prompt_template}\nResponse should be a single, punchy ad hook.",
                "stream": False
            }
            response = requests.post(
                f"{Config.OLLAMA_BASE_URL}/api/generate", 
                json=payload, 
                timeout=30
            )
            if response.status_code == 200:
                content = response.json().get("response")
        except Exception:
            pass

        # Fallback to OpenAI
        if not content and Config.OPENAI_API_KEY:
            try:
                client = openai.OpenAI(api_key=Config.OPENAI_API_KEY)
                resp = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt_template}]
                )
                content = resp.choices[0].message.content
            except Exception as e:
                logger.error(f"Cloud LLM Fallback failed: {e}")

        if content:
            candidates.append(content.strip())

    if not candidates:
        return "❌ Error: No candidates generated. Check Ollama status or API keys."

    # --- Phase 2: Validation (Critic) ---
    # Score all candidates using the retrained weights
    scored_candidates = [
        {"text": c, "score": get_critic_score(c)} for c in candidates
    ]
    
    # Sort by BERT's quality score descending
    scored_candidates.sort(key=lambda x: x['score'], reverse=True)
    
    best_hook = scored_candidates[0]['text']
    logger.info(f"Top hook selected with BERT confidence: {scored_candidates[0]['score']:.2f}")

    return best_hook
