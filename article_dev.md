---
title: A Voz dos Meus — I turned my father's voice into a memory my children can talk to
published: false
tags: devchallenge, weekendchallenge, hf26challenge, gemma
cover_image: COVER_IMAGE_URL
---

*This is a submission for the [Hacktoberfest Weekend Challenge: Build for a Friend](https://dev.to/challenges/hacktoberfest-weekend-2026-10-01) — and for the **Best Use of Gemma** category.*

---

We film our children growing up. Nobody films our parents growing old.

My father left Portugal and came to Luxembourg decades ago, and he carries his whole
story the way fathers do — he only lets it out in pieces, at the table, when something
reminds him. How he arrived. The work. The Sundays. The friends who became family.
Ask him directly and he shrugs: *"Não é nada."* It's nothing.

It's not nothing. A few weeks ago, watching him tell one of those pieces, I had the
thought that started this project:

**My children might never hear him tell any of it.**

Not a recording of it. Not a transcript of it. *Him* telling it — in Portuguese, in his
order, with his detours. When he stops, the stories stop. Every family on Earth is
running the same silent countdown. Mine is no different.

So for this challenge I built him — and really, every family — a memory we can keep
talking to.

## A Voz dos Meus — The Voice of the Ones We Love

The concept fits in one sentence, and it isn't really about my father:
**the people we love most are the ones we record least — so capture their voice, and let the family ask their memory questions. Forever.**

Father, grandmother, aunt, the friend who's like family — *pai, avó, tia* — the concept
is the same. That's why the app is called *A Voz dos Meus*, "the voice of my people",
and not "the voice of my dad". He's simply the first voice in ours.

There are exactly three screens, because he's not a user, he's my father:

![Asking his memory a question](SHOT_ASK_URL)

1. **Contar história** — one big red button. He presses it, talks as long as he wants,
   presses it again. That's the entire interface. (There is no step 2.)
2. **Histórias** — every story, transcribed, with his original audio underneath, so the
   grandchildren hear *his* voice, not a synthesizer's.
3. **Perguntar** — the family asks: *"Pai, como era a tua aldeia em Portugal?"* — and his
   memory answers in warm, simple European Portuguese, with an **Ouvir 🔊** button that
   reads it aloud, and a **Traduire 🇫🇷** one for the grandkids whose Portuguese is,
   let's say, a work in progress.

Here's the whole thing in motion — question, answer, the story library, the one-button recorder:

![Demo of the full flow](DEMO_GIF_URL)

**Live demo:** [DEMO_URL](DEMO_URL) — it's a temporary tunnel to the same home box my
father uses, so it might be slow; it's a kitchen appliance, not a datacenter.
**Source:** [github.com/jeffreyturov-dev/avozdosmeus](https://github.com/jeffreyturov-dev/avozdosmeus) (MIT — take it, build it for someone you love).

## The part that matters most: what it refuses to do

The first version of the "ask" feature did something that looked like a success and was
actually a betrayal.

I asked it a question my father had never answered in any of his stories. The model,
eager to please, **invented** an answer — warm, plausible, in his voice, and completely
false. A memory machine that hallucinates isn't a memory machine. It's a fiction machine
wearing my father's voice.

For a product that's a bug. For a family archive it's a moral failure. If my daughter
asks this thing a question in twenty years, I need to trust the answer the way I'd trust
her grandfather.

So the heart of the app is a refusal. The answering prompt runs under absolute rules —
no invented people, places, dates or details, ever, not even "to complete a sentence
nicely". Now, when the story isn't there, it answers roughly this:

> *"Meu filho, o Pai ainda não contou essa história — pergunta-lhe na próxima visita."*

"My son, your father hasn't told that story yet — ask him on the next visit."

It stays inside what he actually said, it admits the gap, and — my favorite detail —
**it sends the family back to him**. The app knows its job is not to replace my father.
Its job is to make sure he gets asked while he can still answer.

## How it works (everything open, everything local)

```
 his voice ─▶ faster-whisper ─▶ story text ─▶ chunks ─▶ embeddings ─▶ SQLite
                                                         │
 a question ─▶ embed ─▶ cosine search over his stories ─▶ Gemma 3 (local)
              ─▶ answer under "never invent" rules ─▶ read aloud (pt-PT)
```

- **faster-whisper** (`medium`, int8) transcribes his Portuguese on a plain CPU — no GPU
  anywhere in this project.
- **nomic-embed-text** turns each story chunk into a vector, stored in a humble SQLite
  file. His whole memory is a folder you can copy to a USB stick.
- **Gemma 3 (4B)** via Ollama does the reasoning: retrieval over *his* stories, answer
  construction under the no-invention rules, story titling, and the Portuguese→French
  translation for the grandchildren.
- **The browser's own SpeechSynthesis** reads answers aloud in pt-PT — which means even
  the voice-out works with the router unplugged.

The backend is a single Flask file talking to Ollama over localhost HTTP. The frontend is
one HTML page. No Docker, no accounts, no API keys, no build step. An old laptop on the
home Wi-Fi is the entire infrastructure — which is precisely the point.

## Why open-source wasn't a choice here — it was the requirement

Every "why open matters" section talks philosophy. Mine is simpler: **I was not going to
put my father's voice on a stranger's server.**

- **His stories are among the most private data my family owns.** Where he came from, who
  he loved, the things he only says in his own language. A closed API would mean shipping
  that intimacy to a datacenter I can't see, under terms I can't negotiate. With an
  open-weight model running in my home, his voice physically never leaves the house.
  The threat model is my Wi-Fi password.
- **It has to work in a kitchen, not in a demo.** No internet? Everything above still
  runs: recording, transcription, retrieval, answers, voice. Closed models turn into a
  blank screen the moment the connection drops — his doesn't.
- **It has to cost €0 forever.** A subscription is a thing that gets cancelled. This is
  meant to outlive my father, and ideally me. Open models don't send invoices to my children.
- **It has to be ownable by the next family.** Every component — Whisper, the embeddings,
  Gemma, the UI — is open and swappable. When a better open Portuguese model appears,
  his memory upgrades without asking anyone's permission.

That's what "open innovation" means when the person is someone you love: not a license
badge, but a promise you can actually keep — *your voice stays yours*.

## What happens next Sunday

The roadmap writes itself, and it isn't mine anymore — it's the family's: one archive per
person (*Pai* today, *Avó* next, the tia who tells the scandalous ones after that),
WhatsApp voice-message import, a printed family book for Christmas.

But none of that is the point. The point is that next Sunday, at the table, when he lets
out one of those pieces and shrugs *"não é nada"* — I'll press a red button.

And it will be something. Forever.

---

## Built with

- **[Gemma 3](https://ollama.com/library/gemma3)** (open-weight, via [Ollama](https://ollama.com)) —
  the brain: grounded answering under strict no-invention rules, titling, translation.
  *Entered in **Best Use of Gemma**.*
- **[faster-whisper](https://github.com/SYSTRAN/faster-whisper)** — open-source speech-to-text, CPU-only.
- **[nomic-embed-text](https://ollama.com/library/nomic-embed-text)** — open embeddings for the memory retrieval.
- Python + Flask + SQLite + one HTML page. Repo: **[github.com/jeffreyturov-dev/avozdosmeus](https://github.com/jeffreyturov-dev/avozdosmeus)** (MIT).

*If you have someone whose voice you'd miss — fork it. This weekend is long enough to save it.*
