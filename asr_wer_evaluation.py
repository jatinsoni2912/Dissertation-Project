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