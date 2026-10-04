#!/usr/bin/env python3
"""Full e2e via PUBLIC url: ask about his real story, then synthesize the answer in his voice."""
import json, time, urllib.request

BASE = "https://tariff-ventures-income-insights.trycloudflare.com"

def post(ep, payload, timeout=300, raw=False):
    req = urllib.request.Request(BASE + ep, data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json"})
    r = urllib.request.urlopen(req, timeout=timeout)
    return r.read() if raw else json.load(r)

questions = [
    "Pai, como é que nós viemos para o Luxemburgo?",
    "O que aconteceu quando chegámos ao Luxemburgo?",
    "Pai, qual era o teu prato preferido quando eras pequeno?",  # trap — must say he never told
]
answers = []
for q in questions:
    t0 = time.time()
    r = post("/api/ask", {"question": q})
    print(f"\nQ ({time.time()-t0:.0f}s): {q}")
    print("A:", r["answer"])
    answers.append(r["answer"])

# voice clone the first answer through the PUBLIC url
t0 = time.time()
audio = post("/api/speak_clone", {"text": answers[0], "lang": "pt"}, timeout=600, raw=True)
dt = time.time() - t0
open("/opt/data/projet/avozdaavo/docs/answer_in_his_voice.wav", "wb").write(audio)
print(f"\nVOICE: {len(audio)} bytes in {dt:.0f}s (public url)")
