#!/usr/bin/env python3
"""
Voice-clone micro-service for A Voz dos Meus.
Loads Coqui XTTS v2 ONCE, then synthesizes answers in the recorded voice.
Runs fully local (CPU). XTTS v2 = Coqui Public Model License (non-commercial).
"""
import io, os, sys, time, hashlib, json
from http.server import BaseHTTPRequestHandler, HTTPServer

REF_AUDIO = os.environ.get("VOICE_REF", "/opt/data/projet/avozdaavo/data/audio/a72a97e2.webm")
CACHE = "/opt/data/projet/avozdaavo/data/voice_cache"
PORT = int(os.environ.get("VOICE_PORT", "5578"))
os.makedirs(CACHE, exist_ok=True)

print("[voice] loading XTTS v2 ...", flush=True)
t0 = time.time()
import torch
from TTS.api import TTS

device = "cpu"
tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)
print(f"[voice] model ready in {time.time()-t0:.0f}s", flush=True)

# reference must be wav for XTTS — convert once with ffmpeg
REF_WAV = os.path.join(CACHE, "reference.wav")
if not os.path.exists(REF_WAV) or os.path.getmtime(REF_WAV) < os.path.getmtime(REF_AUDIO):
    import subprocess
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", REF_AUDIO,
                    "-ar", "22050", "-ac", "1", REF_WAV], check=True)
    print("[voice] reference converted", flush=True)

class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _send(self, code, body=b"", ctype="audio/wav"):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/health":
            self._send(200, b'{"ok":true}', "application/json")
        else:
            self._send(404, b"{}", "application/json")

    def do_POST(self):
        if self.path != "/speak":
            self._send(404, b"{}", "application/json")
            return
        try:
            n = int(self.headers.get("Content-Length", "0"))
            body = json.loads(self.rfile.read(n) or b"{}")
            text = (body.get("text") or "").strip()
            lang = (body.get("lang") or "pt").strip()
            if not text:
                self._send(400, b'{"error":"empty"}', "application/json")
                return
            key = hashlib.sha1((lang + "|" + text).encode()).hexdigest()[:16]
            wav_path = os.path.join(CACHE, key + ".wav")
            if not os.path.exists(wav_path):
                t0 = time.time()
                tts.tts_to_file(text=text, file_path=wav_path,
                                speaker_wav=REF_WAV, language=lang)
                print(f"[voice] synth {len(text)} chars in {time.time()-t0:.0f}s", flush=True)
            with open(wav_path, "rb") as f:
                self._send(200, f.read())
        except Exception as e:
            print("[voice] ERROR", e, flush=True)
            self._send(500, json.dumps({"error": str(e)}).encode(), "application/json")

if __name__ == "__main__":
    print(f"[voice] serving on 127.0.0.1:{PORT}", flush=True)
    HTTPServer(("127.0.0.1", PORT), H).serve_forever()
