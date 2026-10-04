#!/usr/bin/env python3
"""Test voice cloning: synthesize an app-style answer in the recorded voice."""
import json, time, urllib.request, subprocess

text = ("Meu filho, em mil novecentos e noventa e seis eu tinha seis anos quando viemos "
        "de autocarro de Amares para o Luxemburgo. Quando chegámos, o teu avô estava à "
        "nossa espera com um ramo de flores.")

t0 = time.time()
req = urllib.request.Request(
    "http://127.0.0.1:5578/speak",
    data=json.dumps({"text": text, "lang": "pt"}).encode(),
    headers={"Content-Type": "application/json"})
audio = urllib.request.urlopen(req, timeout=600).read()
dt = time.time() - t0

out = "/opt/data/projet/avozdaavo/docs/test_clone.wav"
open(out, "wb").write(audio)

probe = subprocess.run(["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
                        "-of", "csv=p=0", out], capture_output=True, text=True)
rms = subprocess.run(["ffmpeg", "-i", out, "-af", "volumedetect", "-f", "null", "-"],
                     capture_output=True, text=True)
mean_vol = [l for l in rms.stderr.splitlines() if "mean_volume" in l]
max_vol = [l for l in rms.stderr.splitlines() if "max_volume" in l]

print(f"synth: {len(audio)} bytes in {dt:.0f}s | audio duration: {probe.stdout.strip()}s")
print(mean_vol, max_vol)
print("saved:", out)
