import os
import tempfile
import time
from faster_whisper import WhisperModel

whisper_model = None
whisper_model_size = None


def load_whisper(model_size="base"):
    
    global whisper_model, whisper_model_size

    if whisper_model is not None and whisper_model_size == model_size:
        return whisper_model

    print(f"[ASR] Loading Whisper {model_size}...")
    
    whisper_model = WhisperModel(model_size, device="cpu", compute_type="int8")
    whisper_model_size = model_size
    
    print("[ASR] Whisper ready")

    return whisper_model

def transcribe(audio_bytes, model_size="base"):
    
    model = load_whisper(model_size)

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        tmp.write(audio_bytes)
        tmp_path = tmp.name

    try:
        t0 = time.time()

        segments, info = model.transcribe(tmp_path, language="en", beam_size=5,vad_filter=True)
        segments = list(segments)
        duration = time.time() - t0

        text = " ".join(s.text.strip() for s in segments).strip()

        if segments:
            avg_logprob = sum(s.avg_logprob for s in segments) / len(segments)
            confidence = max(0.0, min(1.0, 1.0 + avg_logprob / 2.0))
        
        else:
            confidence = 0.0

        return {
            "text": text,
            "confidence": round(confidence, 2),
            "language": info.language,
            "duration_s": round(duration, 2),
            "segments": [{"start": s.start, "end": s.end, "text": s.text.strip(),} for s in segments],
            }

    finally:
        os.unlink(tmp_path)
