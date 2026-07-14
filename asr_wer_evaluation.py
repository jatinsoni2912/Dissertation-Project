import csv
import io
import sys
from datetime import datetime
import sounddevice as sd
import scipy.io.wavfile as wav
import numpy as np
from faster_whisper import WhisperModel


SAMPLE_RATE = 16000
RECORD_SECONDS = 6

model = None

def load_model():
    global model
    
    if model is None:
        print("Loading Whisper (base)...")
        model = WhisperModel("base", device="cpu", compute_type="int8")
        print("Ready.\n")

    return model

def record_audio():
    print(f" Recording {RECORD_SECONDS}s — speak now...")
    audio = sd.rec(int(RECORD_SECONDS * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=1, dtype="int16")
    sd.wait()
    print(" Done.")
    buf = io.BytesIO()
    wav.write(buf, SAMPLE_RATE, audio)
    return buf.getvalue()

def transcribe(audio_bytes):
    import tempfile, os
    model = load_model()
    
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        tmp.write(audio_bytes)
        path = tmp.name
    
    try:
        segments, _ = model.transcribe(path, language="en", beam_size=5, vad_filter=True)
        return " ".join(s.text.strip() for s in segments).strip()
    
    finally:
        os.unlink(path)