import json
import os

from dotenv import load_dotenv
load_dotenv()

PROVIDER_OLLAMA  = "ollama"
PROVIDER_BEDROCK = "bedrock"

OLLAMA_MODELS  = ["qwen2.5-coder:1.5b"]
BEDROCK_MODELS = ["google.gemma-3-4b-it"]

DEFAULT_OLLAMA_MODEL  = "qwen2.5-coder:1.5b"
DEFAULT_BEDROCK_MODEL = "google.gemma-3-4b-it"

BEDROCK_READ_TIMEOUT  = 20
BEDROCK_MAX_ATTEMPTS  = 2

def get_provider():
    return os.getenv("OLLAMA_PROVIDER", PROVIDER_OLLAMA).lower()

def call_model(prompt, model, max_tokens=512):
    provider = get_provider()
    
    if provider == PROVIDER_BEDROCK:
        return call_bedrock(prompt, model, max_tokens)
    
    return call_ollama(prompt, model, max_tokens)
