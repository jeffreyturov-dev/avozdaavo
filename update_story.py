#!/usr/bin/env python3
"""Replace story text with the clean large-v3-turbo transcription and re-embed its chunks."""
import json, os, sqlite3, urllib.request

DB = "/opt/data/projet/avozdaavo/data/avo.db"
OLLAMA = "http://127.0.0.1:11434"
SID = "a72a97e2"

CLEAN = ("Em 1996, tinha eu seis anos, andava na escola infantária em Amares, em Braga, "
         "e quando a minha mãe e o meu pai já tinham decidido que a gente ia emigrar para "
         "o Luxemburgo, no entanto eu tinha seis anos. Eu lembro-me de ter vindo dentro de "
         "um autocarro, numa longa viagem com outros portugueses. Eu não me lembro de ter "
         "visto outras crianças dentro do autocarro. Eu acho que era poucas famílias com "
         "filhos que tinham emigrado naquela altura. No entanto, quando cheguei a Luxemburgo, "
         "o meu pai estava à espera, com um ramo de flores à espera da minha mãe, "
         "e à espera de nos acolher.")

def embed(text):
    req = urllib.request.Request(OLLAMA + "/api/embeddings",
        data=json.dumps({"model": "nomic-embed-text", "prompt": text}).encode(),
        headers={"Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(req, timeout=60))["embedding"]

def chunk_text(text, words=110, overlap=25):
    ws = text.split()
    out, i = [], 0
    while i < len(ws):
        out.append(" ".join(ws[i:i + words]))
        i += max(1, words - overlap)
    return out

c = sqlite3.connect(DB)
c.execute("UPDATE stories SET text=?, title=? WHERE id=?",
          (CLEAN, "A viagem de autocarro, 1996", SID))
c.execute("DELETE FROM chunks WHERE story_id=?", (SID,))
for i, ch in enumerate(chunk_text(CLEAN)):
    c.execute("INSERT INTO chunks(story_id,seq,text,emb) VALUES(?,?,?,?)",
              (SID, i, ch, json.dumps(embed(ch))))
c.commit()
print("story updated + re-embedded:", c.execute("SELECT COUNT(*) FROM chunks WHERE story_id=?", (SID,)).fetchone()[0], "chunks")
