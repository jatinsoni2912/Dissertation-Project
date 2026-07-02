import os
import tempfile
import time
from faster_whisper import WhisperModel

whisper_model = None
whisper_model_size = None


def load_whisper(model_size: str = "base"):
    
    global whisper_model, whisper_model_size

    if whisper_model is not None and whisper_model_size == model_size:
        return whisper_model

    print(f"[ASR] Loading Whisper {model_size}...")
    
    whisper_model = WhisperModel(model_size, device="cpu", compute_type="int8")
    whisper_model_size = model_size
    
    print("[ASR] Whisper ready")

    return whisper_model