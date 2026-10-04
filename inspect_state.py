#!/usr/bin/env python3
"""Inspect DB + audio files state, and probe recordings (duration, transcription preview)."""
import json, os, sqlite3, subprocess

DATA = "/opt/data/projet/avozdaavo/data"
c = sqlite3.connect(os.path.join(DATA, "avo.db"))
rows = c.execute("SELECT id,title,lang,audio,duration,created FROM stories").fetchall()
print("DB stories:")
for r in rows:
    print(" ", r)

for f in sorted(os.listdir(os.path.join(DATA, "audio"))):
    p = os.path.join(DATA, "audio", f)
    try:
        out = subprocess.run(["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
                              "-of", "csv=p=0", p], capture_output=True, text=True, timeout=15)
        print(f, os.path.getsize(p), "bytes | duration:", out.stdout.strip(), "s")
    except Exception as e:
        print(f, "probe fail", e)
