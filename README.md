# A Voz da Avó 🧡
*The Grandmother's Voice — As histórias dela. Para sempre.*

Record a loved one's stories, in their own voice, and let the family ask their memory questions — forever.
Built for my grandmother, a Portuguese emigrant in Luxembourg, so my children will always be able to hear
*her* tell *her* stories — in her language, with her words.

**100% local and open-source.** Her voice never leaves the house. No cloud, no subscription, no account, €0.

---

## Why this exists

My grandmother left a small village in Portugal for Luxembourg decades ago.
Her stories — the stone house, the three-day train ride, the café in Bonnevoie — live only in her head
and in her voice. One day I realised my children might never hear them from her lips.

So I built her this:

1. **She tells a story** — one big red button, she just talks (Portuguese, naturally).
2. **The app writes it down** — open-source Whisper transcribes every word, on our own machine.
3. **The family asks her memory questions** — *"Avó, como era a tua aldeia?"* — and an open-weight
   model (Gemma 3, running locally) answers **only** from her own stories, in warm European Portuguese,
   read aloud in her language.

If she never told that story, the app says so — and tells you to ask her on the next visit.
It will never invent her memories.

## Why open-source matters here

- **Privacy is the product.** These are a family's most intimate recordings. With a closed API they
  would live on someone else's server. Here they never leave the house.
- **It works with no internet** in her kitchen — recording, transcription, questions, voice.
- **It costs €0 forever.** No subscription between her and her grandchildren.
- **Every piece can be swapped** — Whisper, the embeddings, the model — because they're all open.

## Stack (everything open-source)

| Piece | Tech | Runs |
|---|---|---|
| Speech-to-text | [faster-whisper](https://github.com/SYSTRAN/faster-whisper) (Whisper `medium`, int8) | local CPU |
| Reasoning | [Gemma 3 (4B)](https://ollama.com/library/gemma3) via [Ollama](https://ollama.com) | local |
| Memory (RAG) | [nomic-embed-text](https://ollama.com/library/nomic-embed-text) embeddings + SQLite | local |
| Voice out | Browser SpeechSynthesis (`pt-PT`) | local, offline |
| Backend | Python + Flask (stdlib HTTP to Ollama) | any old laptop / home server |
| Frontend | Single-page HTML, installable PWA, big-button UI for non-tech elders | any phone |

No Docker required, no GPU required, no API keys. An old laptop on the home Wi-Fi is enough.

## Quickstart

```bash
# 1. Install Ollama and pull the two open models
ollama pull gemma3:4b
ollama pull nomic-embed-text

# 2. Install Python deps
pip install flask faster-whisper

# 3. Run
python3 server.py
# → open http://localhost:5577 on any phone/computer on the same network
```

Then: **Contar história** → press the red button → she talks → press again → saved & transcribed.
**Perguntar** → the family asks → answers grounded in her stories, with **Ouvir 🔊** to hear it aloud.

## How "ask her memory" works

```
audio ──▶ faster-whisper ──▶ story text ──▶ chunks ──▶ nomic embeddings ──▶ SQLite
                                                                      │
question ──▶ embed ──▶ cosine search (top-k chunks) ──▶ Gemma 3 with strict
"never invent" rules ──▶ warm answer in her language ──▶ SpeechSynthesis aloud
```

The system prompt forbids adding people, places or details that are not in her stories.
If the answer isn't there, the app says she hasn't told that one yet — and to ask her next Sunday.

## Roadmap

- [ ] WhatsApp voice-message import (our family's real archive of her)
- [ ] Export the whole memory as a printed family book (PDF)
- [ ] Grandchildren mode: questions in French/Luxembourgish, answers in her Portuguese + translation
- [ ] One-command installer for non-technical families

## License

MIT — take it, build it for someone you love.
