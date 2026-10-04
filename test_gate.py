#!/usr/bin/env python3
"""Retest: in-scope questions must get grounded answers, traps must get the honest refusal."""
import json, time, urllib.request

BASE = "https://tariff-ventures-income-insights.trycloudflare.com"

def post(ep, payload, timeout=300):
    req = urllib.request.Request(BASE + ep, data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(req, timeout=timeout))

questions = [
    ("IN ", "Pai, como é que nós viemos para o Luxemburgo?"),
    ("IN ", "Quantos anos tinhas quando vieste para o Luxemburgo?"),
    ("IN ", "Quem estava à espera quando chegámos?"),
    ("TRAP", "Pai, qual era o teu prato preferido quando eras pequeno?"),
    ("TRAP", "O Pai alguma vez falou de futebol?"),
    ("TRAP", "Como era a casa dos teus pais em Portugal?"),
]
for tag, q in questions:
    t0 = time.time()
    r = post("/api/ask", {"question": q})
    gated = f" [GATED:{r.get('gated')}]" if r.get("gated") else ""
    print(f"\n{tag} ({time.time()-t0:.0f}s, score={r.get('best_score')}{gated}): {q}")
    print("A:", r["answer"][:400])
