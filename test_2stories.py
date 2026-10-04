#!/usr/bin/env python3
"""Verify memory with 2 stories: cross-story + single-story + trap questions."""
import json, time, urllib.request

BASE = "https://tariff-ventures-income-insights.trycloudflare.com"

def post(ep, payload, timeout=300):
    req = urllib.request.Request(BASE + ep, data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(req, timeout=timeout))

questions = [
    "Quais línguas é que aprendeste na escola no Luxemburgo?",
    "Qual foi a tua primeira língua estrangeira?",
    "Quantos anos tinhas quando chegaste ao Luxemburgo?",
    "Pai, o que é que comias na escola?",   # trap
]
for q in questions:
    t0 = time.time()
    r = post("/api/ask", {"question": q})
    gated = f" [GATED:{r.get('gated')}]" if r.get("gated") else ""
    print(f"\nQ ({time.time()-t0:.0f}s, score={r.get('best_score')}{gated}): {q}")
    print("A:", r["answer"][:350])
    print("sources:", r.get("sources"))
