#!/usr/bin/env python3
"""Compare whisper models on the tricky test audio."""
import time
from faster_whisper import WhisperModel

path = "/opt/data/projet/avozdaavo/testdata/viagem.mp3"
for size in ["large-v3-turbo"]:
    t0 = time.time()
    m = WhisperModel(size, device="cpu", compute_type="int8")
    load = time.time() - t0
    t0 = time.time()
    segs, info = m.transcribe(path, beam_size=5)
    text = " ".join(s.text.strip() for s in segs)
    print(f"{size}: load={load:.0f}s transcribe={time.time()-t0:.0f}s")
    print("TEXT:", text)
