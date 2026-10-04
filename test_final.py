#!/usr/bin/env python3
"""Final full e2e via PUBLIC url: grounded Qs, trap Q (must hit honesty gate), async voice clone."""
import json, time, urllib.request, urllib.error

BASE = "https://tariff-ventures-income-insights.trycloudflare.com"

def post(ep, payload, timeout=300):
    req = urllib.request.Request(BASE + ep, data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(req, timeout=timeout))

def get(ep, timeout=30):
    try:
        r = urllib.request.urlopen(BASE + ep, timeout=timeout)
        return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()

questions = [
    "Pai, como é que nós viemos para o Luxemburgo?",
    "O que aconteceu quando chegámos ao Luxemburgo?",
    "Quantos anos tinhas quando vieste para o Luxemburgo?",
    "Pai, qual era o teu prato preferido quando eras pequeno?",   # trap → gate
    "O Pai alguma vez falou de futebol?",                          # trap → gate
]
answers = []
for q in questions:
    t0 = time.time()
    r = post("/api/ask", {"question": q})
    gated = " [GATED]" if r.get("gated") else ""
    print(f"\nQ ({time.time()-t0:.0f}s, score={r.get('best_score')}{gated}): {q}")
    print("A:", r["answer"])
    answers.append(r["answer"])

# async voice clone of answer 1 via public url
print("\n--- voice clone (async) ---")
r = post("/api/speak_clone", {"text": answers[0], "lang": "pt"})
job = r["job_id"]
print("job:", job)
t0 = time.time()
while True:
    time.sleep(4)
    code, body = get("/api/speak_clone/" + job, timeout=30)
    if code == 202:
        print(f"  pending... {time.time()-t0:.0f}s")
        continue
    if code == 200:
        open("/opt/data/projet/avozdaavo/docs/answer_in_his_voice.wav", "wb").write(body)
        print(f"VOICE OK: {len(body)} bytes in {time.time()-t0:.0f}s via public url")
        break
    print("ERROR", code, body[:200])
    break
