---
title: A Voz dos Meus — my father waited with flowers. I built a memory that never forgets
published: false
tags: devchallenge, weekendchallenge, hf26challenge, gemma
cover_image: https://raw.githubusercontent.com/jeffreyturov-dev/avozdosmeus/master/docs/cover.png
---

*This is a submission for the [Hacktoberfest Weekend Challenge: Build for a Friend](https://dev.to/challenges/hacktoberfest-weekend-2026-10-01) — and for the **Best Use of Gemma** category.*

---

In 1996, a six-year-old boy got on a bus in Amares, near Braga, for a long ride north with other Portuguese families. He doesn't remember any other children on that bus — emigration was mostly parents back then. When the bus finally reached Luxembourg, his father was standing there, waiting for them, holding a bunch of flowers for his mother.

That boy was me. The man with the flowers is my father.

We film our children growing up. Nobody films our parents growing old. My father carried his whole life to Luxembourg and lets the story out only in pieces, at the table, when something reminds him — and if you ask directly, he shrugs: *"Não é nada."* It's nothing.

It's not nothing. So for this challenge I built the person I love most a memory the family can keep talking to — and the very first voice I put in it was my own, telling the story where he's the hero.

## A Voz dos Meus — The Voice of the Ones We Love

The concept fits in one sentence, and it isn't really about my father:
**the people we love most are the ones we record least — so capture their voices, and let the family ask their memory questions. Forever.**

Father, grandmother, aunt, the friend who's like family — *pai, avó, tia* — the concept is the same, which is why the app is called *A Voz dos Meus*, "the voice of my people". My father is simply the reason it exists.

Three screens, because he's not a user, he's my father:

![Asking the memory a question](https://raw.githubusercontent.com/jeffreyturov-dev/avozdosmeus/master/docs/shot_ask.png)

1. **Contar história** — one big red button. Press it, talk as long as you want, press it again. That's the entire interface. (There is no step 2.)
2. **Histórias** — every story transcribed, with the original audio underneath, so the grandchildren hear *his* voice, not a synthesizer's.
3. **Perguntar** — the family asks: *"Pai, como é que nós viemos para o Luxemburgo?"* — and the memory answers in warm, simple European Portuguese. Read it instantly with **Ouvir 🔊**, translate it for the grandkids with **Traduire 🇫🇷** — or press the button that still gives me goosebumps:

   **Na voz dele 🧡** — the answer is synthesized *in his own cloned voice*, by an open-source model running in my home.

**Live demo:** [https://tariff-ventures-income-insights.trycloudflare.com](https://tariff-ventures-income-insights.trycloudflare.com) — a temporary tunnel to the same home box my family uses; it's a kitchen appliance, not a datacenter, so be patient with it (voice cloning on a CPU takes ~2 minutes — real time for real love).
**Source:** [github.com/jeffreyturov-dev/avozdosmeus](https://github.com/jeffreyturov-dev/avozdosmeus) (MIT — take it, build it for someone you love).

![The first story in the archive](https://raw.githubusercontent.com/jeffreyturov-dev/avozdosmeus/master/docs/shot_stories.png)

## The part that matters most: what it refuses to do

The first version of the "ask" feature did something that looked like a success and was actually a betrayal.

I asked it: *"Pai, qual era o teu prato preferido quando eras pequeno?"* — what was your favorite dish as a kid? He has never told that story. The model, eager to please, **invented one** — grilled sardines with potatoes and kale, warm and plausible and completely false. A memory machine that hallucinates isn't a memory machine. It's a fiction machine wearing my father's voice.

For a product, that's a bug. For a family archive, it's a moral failure. If my daughter asks this thing a question in twenty years, I need to trust the answer the way I'd trust her grandfather.

So I rebuilt the answer path around a refusal, in three layers:

1. **Retrieval** — the question is embedded and matched against story chunks (open embeddings, local SQLite).
2. **A strict classifier** — before *any* prose is generated, a separate pass asks: *"Do these stories explicitly contain the answer? Reply only SIM or NÃO."* If NÃO, the generative model **is never called**. A model cannot hallucinate what it never sees.
3. **No-invention rules** — when the stories do contain the answer, the answering prompt runs under absolute rules: no invented people, places, dates or details. Not even to complete a sentence nicely.

Today, that same trap question gets this answer — every time, deterministically:

> *"O Pai ainda não contou essa história. Pergunta-lhe na próxima visita — e se ele contar, grava-a aqui. 🧡"*

"Your father hasn't told that story yet. Ask him on the next visit — and if he tells it, record it here."

![The honest refusal](https://raw.githubusercontent.com/jeffreyturov-dev/avozdosmeus/master/docs/shot_honest.png)

It admits the gap, and — my favorite detail — **it sends the family back to him**. The app knows its job is not to replace my father. Its job is to make sure he gets asked while he can still answer.

## How it works (everything open, everything local)

```
 his voice ─▶ faster-whisper ─▶ story text ─▶ chunks ─▶ embeddings ─▶ SQLite
                                                         │
 a question ─▶ embed ─▶ retrieve ─▶ strict classifier ─▶ Gemma 3 (local,
              "never invent" rules) ─▶ answer ─▶ read aloud ─▶ or cloned
              in HIS voice by XTTS v2 — all of it inside my home
```

- **faster-whisper** (`large-v3-turbo`, int8) transcribes the stories on a plain CPU — no GPU anywhere in this project.
- **nomic-embed-text** vectors in a humble SQLite file. His whole memory is a folder you can copy to a USB stick.
- **Gemma 3 (4B)** via Ollama is the brain: the honesty classifier, the grounded answering, story titling, and the Portuguese→French translation for the grandchildren.
- **XTTS v2** (open-source voice cloning) reads answers *in his voice* — synthesized locally, from one minute of his real audio.
- **Browser SpeechSynthesis** handles the instant read-aloud — so even that works with the router unplugged.

The backend is a single Flask file. The frontend is one HTML page. No Docker, no accounts, no API keys, no build step. An old laptop on the home Wi-Fi is the entire infrastructure — which is precisely the point.

## Why open-source wasn't a choice here — it was the requirement

Every "why open matters" section talks philosophy. Mine is simpler: **I was not going to put my father's voice on a stranger's server.**

- **His stories are among the most private data my family owns.** Where he came from, who he waited for with flowers. A closed API would mean shipping that intimacy to a datacenter I can't see, under terms I can't negotiate. With open-weight models running in my home, his voice — and its digital double — physically never leaves the house. The threat model is my Wi-Fi password.
- **Voice cloning makes this non-negotiable.** I'm creating a model of a real person's voice. If that capability lived in a cloud account, the consent conversation gets murky fast. Local and open means *his voiceprint belongs to him, full stop* — I can show him exactly where it lives, and delete it by deleting a folder.
- **It has to work in a kitchen, not in a demo.** No internet? Everything above still runs. Closed models turn into a blank screen the moment the connection drops — his memory doesn't.
- **It has to cost €0 forever.** A subscription is a thing that gets cancelled. This is meant to outlive my father, and ideally me. Open models don't send invoices to my children.
- **It has to be ownable by the next family.** Every component — Whisper, the embeddings, Gemma, XTTS, the UI — is open and swappable. When a better open Portuguese model appears, his memory upgrades without asking anyone's permission.

That's what "open innovation" means when the person is someone you love: not a license badge, but a promise you can actually keep — *your voice stays yours*.

## What happens next Sunday

The roadmap writes itself, and it isn't mine anymore — it's the family's: one archive per person (*Pai* today, *Avó* next, the tia who tells the scandalous ones after that), WhatsApp voice-message import, a printed family book for Christmas.

But none of that is the point. The point is that next Sunday, at the table, when he lets out one of those pieces and shrugs *"não é nada"* — I'll press a red button.

And it will be something. Forever. In his own voice.

---

## Built with

- **[Gemma 3](https://ollama.com/library/gemma3)** (open-weight, via [Ollama](https://ollama.com)) — the brain: honesty classifier, grounded answering, titling, translation. *Entered in **Best Use of Gemma**.*
- **[faster-whisper](https://github.com/SYSTRAN/faster-whisper)** — open-source speech-to-text, CPU-only.
- **[XTTS v2](https://github.com/idiap/coqui-ai-TTS)** — open-source voice cloning (CPML, non-commercial) so answers can sound like *him*.
- **[nomic-embed-text](https://ollama.com/library/nomic-embed-text)** — open embeddings for memory retrieval.
- Python + Flask + SQLite + one HTML page. Repo: **[github.com/jeffreyturov-dev/avozdosmeus](https://github.com/jeffreyturov-dev/avozdosmeus)** (MIT).

*If you have someone whose voice you'd miss — fork it. This weekend is long enough to save it.*
