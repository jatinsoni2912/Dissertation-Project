import csv
import io
import sys
from datetime import datetime
import sounddevice as sd
import scipy.io.wavfile as wav
import numpy as np
from faster_whisper import WhisperModel
from jiwer import wer

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
    
def word_error_rate(reference, hypothesis):
    return wer(reference, hypothesis)

def main():
    print("GeoQuery — WER Evaluation")
    print("Type a query, press Enter, then speak it aloud.")
    print("Leave query blank to finish.\n")

    load_model()
    results = []

    while True:
        typed = input("Query (or Enter to finish): ").strip()
        if not typed:
            break

        input("Press Enter to record...")
        audio = record_audio()

        print(" Transcribing...")
        transcript = transcribe(audio)
        wer = word_error_rate(typed, transcript)

        print(f"Transcript : {transcript}")
        print(f"WER : {wer:.1%}\n")

        results.append({"typed": typed, "transcript": transcript, "wer": round(wer, 3)})

    if not results:
        print("No results.")
        return
    
    mean_wer = sum(r["wer"] for r in results) / len(results)
    perfect = sum(1 for r in results if r["wer"] == 0.0)

    print(f"{'='*40}")
    print(f"Queries evaluated : {len(results)}")
    print(f"Mean WER : {mean_wer:.1%}")
    print(f"Perfect (WER=0) : {perfect}/{len(results)}")
    print(f"Queries with errors: {len(results)-perfect}/{len(results)}")
    print(f"{'='*40}")

    
    
