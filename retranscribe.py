#!/usr/bin/env python3
"""Retranscribe the real story with large-v3-turbo and compare to current DB text."""
import time
from faster_whisper import WhisperModel

path = "/opt/data/projet/avozdaavo/data/audio/a72a97e2.webm"
m = WhisperModel("large-v3-turbo", device="cpu", compute_type="int8")
t0 = time.time()
segs, info = m.transcribe(path, beam_size=5, language="pt")
text = " ".join(s.text.strip() for s in segs).strip()
print(f"--- large-v3-turbo ({time.time()-t0:.0f}s) ---")
print(text)
