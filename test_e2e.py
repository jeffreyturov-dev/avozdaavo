#!/usr/bin/env python3
"""End-to-end test: upload 3 PT story audios, ask grounded + out-of-scope questions."""
import json, os, time, urllib.request

BASE = "http://127.0.0.1:5577"

def post_file(path, field="audio"):
    boundary = "----testboundary"
    fname = os.path.basename(path)
    data = open(path, "rb").read()
    body = (f"--{boundary}\r\nContent-Disposition: form-data; name=\"{field}\"; "
            f"filename=\"{fname}\"\r\nContent-Type: audio/mpeg\r\n\r\n").encode() + data + \
           f"\r\n--{boundary}--\r\n".encode()
    req = urllib.request.Request(BASE + "/api/stories", data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"})
    return json.load(urllib.request.urlopen(req, timeout=600))

def post_json(ep, payload):
    req = urllib.request.Request(BASE + ep, data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(req, timeout=300))

# health first
h = json.load(urllib.request.urlopen(BASE + "/api/health", timeout=15))
print("HEALTH:", h)

td = "/opt/data/projet/avozdaavo/testdata"
for f in ["aldeia.mp3", "viagem.mp3", "cafe.mp3"]:
    t0 = time.time()
    r = post_file(os.path.join(td, f))
    print(f"\nUPLOAD {f} ({time.time()-t0:.0f}s)")
    print("  title:", r.get("title"))
    print("  lang:", r.get("lang"), "| dur:", round(r.get("duration", 0), 1), "s")
    print("  text:", (r.get("text") or "")[:200])

questions = [
    "Avó, como era a tua aldeia em Portugal?",
    "Como é que a Avó veio para o Luxemburgo?",
    "O que é que vocês faziam aos domingos?",
    "Qual é a receita do bolo da Avó?",  # out of scope — must say she never told
]
for q in questions:
    t0 = time.time()
    r = post_json("/api/ask", {"question": q})
    print(f"\nQ ({time.time()-t0:.0f}s): {q}")
    print("A:", r.get("answer"))
    print("sources:", r.get("sources"))

# translate check
r = post_json("/api/translate", {"text": "Eu nasci numa aldeia pequena perto de Bragança.", "target": "français"})
print("\nTRANSLATE:", r.get("translation"))
print("\nSTATS:", json.load(urllib.request.urlopen(BASE + "/api/stats", timeout=10)))
