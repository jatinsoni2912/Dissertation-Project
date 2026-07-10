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
        return call_bedrock_model(prompt, model, max_tokens)
    
    return call_ollama_model(prompt, model, max_tokens)

def call_ollama_model(prompt, model, max_tokens):
    try:
        import ollama
        response = ollama.chat(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            options={"temperature": 0, "num_predict": max_tokens}
        )
        return response["message"]["content"].strip()
    except Exception as e:
        raise RuntimeError(f"Ollama call failed: {e}") from e

def call_bedrock_model(prompt, model, max_tokens):
    try:
        import boto3
        from botocore.config import Config

        region = os.getenv("AWS_DEFAULT_REGION", "eu-west-2")
        session = boto3.Session(region_name=region)
        client = session.client("bedrock-runtime", config=Config(connect_timeout=10, read_timeout=BEDROCK_READ_TIMEOUT, retries={"max_attempts": BEDROCK_MAX_ATTEMPTS, "mode": "standard"}))

        body = json.dumps({"messages": [{"role": "user", "content": prompt}], "max_tokens": max_tokens, "temperature": 0.0})

        response = client.invoke_model(modelId=model, body=body, contentType="application/json", accept="application/json")

        result = json.loads(response["body"].read())

        choices = result.get("choices", [])
        
        if choices:
            return choices[0]["message"]["content"].strip()

        content = result.get("content", [])
        
        if content:
            return content[0].get("text", "").strip()

        raise RuntimeError(f"Unexpected Bedrock response format: {list(result.keys())}")

    except RuntimeError:
        raise
    except Exception as e:
        raise RuntimeError(f"Bedrock call failed: {e}") from e

def list_models():
    if get_provider() == PROVIDER_BEDROCK:
        return BEDROCK_MODELS
    
    return OLLAMA_MODELS

def default_model():
    if get_provider() == PROVIDER_BEDROCK:
        return DEFAULT_BEDROCK_MODEL
    
    return DEFAULT_OLLAMA_MODEL