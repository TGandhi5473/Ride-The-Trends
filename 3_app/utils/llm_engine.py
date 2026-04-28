import requests
import json
import openai
from core.config import Config

def generate_creative_assets(prompt_template: str):
    """
    Orchestrates the Last-Mile enrichment. 
    Prioritizes Local Ollama (Zero Cost) -> Fallback to OpenAI.
    """
    
    # 1. Try Local Ollama First
    try:
        payload = {
            "model": Config.OLLAMA_MODEL,
            "prompt": prompt_template,
            "stream": False
        }
        response = requests.post(
            f"{Config.OLLAMA_BASE_URL}/api/generate", 
            json=payload, 
            timeout=30 # Local CPUs can take a moment
        )
        if response.status_code == 200:
            return response.json().get("response")
    except Exception:
        # If Ollama isn't running, we check for OpenAI
        pass

    # 2. Fallback to OpenAI if key exists
    if Config.OPENAI_API_KEY:
        try:
            client = openai.OpenAI(api_key=Config.OPENAI_API_KEY)
            resp = client.chat.completions.create(
                model="gpt-4o-mini", # Cheap fallback
                messages=[{"role": "user", "content": prompt_template}]
            )
            return resp.choices[0].message.content
        except Exception as e:
            return f"❌ Cloud LLM Error: {str(e)}"

    return "🧊 No local LLM found. Please start Ollama or provide an API key."
