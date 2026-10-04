#!/usr/bin/env python3
"""
A Voz dos Meus — The Voice of the Ones We Love.
Record a loved one's stories. Let the family ask their memory questions.
Built first for my father. Works for any voice you never want to lose.
100% local & open-source: faster-whisper (STT) + nomic-embed-text (RAG)
+ Gemma 3 via Ollama (reasoning). No data ever leaves the house.
"""
import json, math, os, sqlite3, subprocess, time, uuid
from flask import Flask, request, jsonify, send_from_directory

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data")
AUDIO = os.path.join(DATA, "audio")
os.makedirs(AUDIO, exist_ok=True)

OLLAMA = os.environ.get("OLLAMA_HOST", "http://127.0.0.1:11434")
GEN_MODEL = os.environ.get("GEN_MODEL", "gemma3:4b")
EMB_MODEL = os.environ.get("EMB_MODEL", "nomic-embed-text")

app = Flask(__name__, static_folder="static", static_url_path="/static")

# ---------------- DB ----------------

def db():
    c = sqlite3.connect(os.path.join(DATA, "avo.db"))
    c.execute("""CREATE TABLE IF NOT EXISTS stories(
        id TEXT PRIMARY KEY, title TEXT, text TEXT, lang TEXT,
        audio TEXT, duration REAL, created REAL)""")
    c.execute("""CREATE TABLE IF NOT EXISTS chunks(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        story_id TEXT, seq INTEGER, text TEXT, emb TEXT)""")
    return c

# ---------------- Ollama helpers ----------------

def ollama(path, payload, timeout=180):
    import urllib.request
    req = urllib.request.Request(
        OLLAMA + path, data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(req, timeout=timeout))

def embed(text):
    r = ollama("/api/embeddings", {"model": EMB_MODEL, "prompt": text})
    return r["embedding"]

def cosine(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a)) or 1e-9
    nb = math.sqrt(sum(x * x for x in b)) or 1e-9
    return dot / (na * nb)

def generate(prompt, system, num_predict=420):
    r = ollama("/api/generate", {
        "model": GEN_MODEL, "prompt": prompt, "system": system,
        "stream": False,
        "options": {"temperature": 0.35, "num_predict": num_predict}}, timeout=300)
    return (r.get("response") or "").strip()

# ---------------- Whisper (lazy) ----------------

_whisper = None
def transcribe(path):
    global _whisper
    if _whisper is None:
        from faster_whisper import WhisperModel
        _whisper = WhisperModel("large-v3-turbo", device="cpu", compute_type="int8")
    segs, info = _whisper.transcribe(path, beam_size=5)
    text = " ".join(s.text.strip() for s in segs).strip()
    dur = getattr(info, "duration", 0.0)
    return text, (info.language or "pt"), dur

# ---------------- Chunking ----------------

def chunk_text(text, words=110, overlap=25):
    ws = text.split()
    if not ws:
        return []
    out, i = [], 0
    while i < len(ws):
        out.append(" ".join(ws[i:i + words]))
        i += max(1, words - overlap)
    return out

# ---------------- Routes ----------------

@app.route("/")
def index():
    return send_from_directory("static", "index.html")

@app.route("/api/health")
def health():
    try:
        tags = ollama_tags()
        return jsonify({"ok": True, "models": tags})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

def ollama_tags():
    import urllib.request
    r = json.load(urllib.request.urlopen(OLLAMA + "/api/tags", timeout=10))
    return [m["name"] for m in r.get("models", [])]

@app.route("/api/stories", methods=["GET"])
def list_stories():
    c = db()
    rows = c.execute(
        "SELECT id,title,text,lang,audio,duration,created FROM stories ORDER BY created DESC").fetchall()
    return jsonify([{
        "id": r[0], "title": r[1], "text": r[2], "lang": r[3],
        "audio": "/audio/" + r[4] if r[4] else None,
        "duration": r[5], "created": r[6]} for r in rows])

@app.route("/audio/<path:name>")
def audio_file(name):
    return send_from_directory(AUDIO, name)

@app.route("/api/stories", methods=["POST"])
def add_story():
    """multipart: audio file + optional title. OR json: {title, text} to add a written story."""
    if request.content_type and "application/json" in request.content_type:
        body = request.get_json(force=True)
        title = (body.get("title") or "História").strip()
        text = (body.get("text") or "").strip()
        if not text:
            return jsonify({"error": "texto vazio"}), 400
        sid, lang, dur, fname = str(uuid.uuid4())[:8], "pt", 0.0, None
    else:
        f = request.files.get("audio")
        if not f:
            return jsonify({"error": "no audio"}), 400
        ext = os.path.splitext(f.filename or "audio.webm")[1] or ".webm"
        sid = str(uuid.uuid4())[:8]
        fname = sid + ext
        path = os.path.join(AUDIO, fname)
        f.save(path)
        try:
            text, lang, dur = transcribe(path)
        except Exception as e:
            return jsonify({"error": "transcription failed: " + str(e)}), 500
        if not text:
            return jsonify({"error": "não percebi — tenta de novo mais perto do microfone"}), 422
        title = (request.form.get("title") or "").strip()
        if not title:
            title = make_title(text)

    c = db()
    c.execute("INSERT INTO stories VALUES(?,?,?,?,?,?,?)",
              (sid, title, text, lang, fname, dur, time.time()))
    for i, ch in enumerate(chunk_text(text)):
        c.execute("INSERT INTO chunks(story_id,seq,text,emb) VALUES(?,?,?,?)",
                  (sid, i, ch, json.dumps(embed(ch))))
    c.commit()
    return jsonify({"id": sid, "title": title, "text": text, "lang": lang,
                    "audio": ("/audio/" + fname) if fname else None, "duration": dur})

@app.route("/api/stories/<sid>", methods=["DELETE"])
def del_story(sid):
    c = db()
    c.execute("DELETE FROM stories WHERE id=?", (sid,))
    c.execute("DELETE FROM chunks WHERE story_id=?", (sid,))
    c.commit()
    return jsonify({"ok": True})

def make_title(text):
    t = generate(
        "Dá um título muito curto (2 a 5 palavras, em português europeu) para esta história. "
        "Responde APENAS com o título.\n\nHistória: " + text[:900],
        "És um assistente que escreve títulos curtos.", num_predict=20)
    t = t.strip().strip('"').split("\n")[0]
    return t[:60] or "História"

SYSTEM_ASK = (
    "Tu és a memória viva do Pai — um pai português que emigrou para o Luxemburgo. "
    "Respondes à família com carinho, em português europeu simples, 3 a 6 frases.\n"
    "REGRAS ABSOLUTAS:\n"
    "1. Usa APENAS factos presentes nas histórias fornecidas. NUNCA inventes pessoas, "
    "lugares, objetos, datas ou pormenores — nem 'para completar a frase'.\n"
    "2. Não adiciones familiares que não aparecem nas histórias (nem pais, nem irmãos, nem filhos).\n"
    "3. Se a pergunta não tiver resposta nas histórias, diz APENAS isto, com ternura: que o Pai "
    "ainda não contou essa história, e que lhe devem perguntar na próxima visita. NADA MAIS.\n"
    "4. Quando responderes com base numa história, não juntes frases finais sobre 'histórias "
    "que faltam contar' — responde só ao que foi perguntado.\n"
    "5. Podes usar expressões carinhosas ('meu filho', 'minha filha', 'ai que saudades') mas os "
    "factos ficam exatamente como ele os contou."
)

HONEST_NO_STORY = (
    "O Pai ainda não contou essa história. Pergunta-lhe na próxima visita — "
    "e se ele contar, grava-a aqui. 🧡"
)

# Deterministic honesty gate: a model cannot hallucinate what it never sees.
# Layer 1: very low embedding similarity -> honest answer, no LLM at all.
# Layer 2: a strict classifier decides whether the stories actually CONTAIN
# the answer; only then does the generative model speak.
SIM_HARD_FLOOR = float(os.environ.get("SIM_HARD_FLOOR", "0.30"))

CLASSIFIER_SYS = (
    "És um classificador rigoroso. Respondes APENAS com a palavra SIM ou a palavra NÃO. "
    "Dizes SIM unicamente se a resposta à pergunta estiver EXPLICITAMENTE escrita nas histórias. "
    "Se as histórias falam de outro assunto, ou só roçam o tema sem responder, dizes NÃO."
)

def stories_contain_answer(ctx, q):
    v = generate(
        f"HISTÓRIAS:\n{ctx}\n\nPERGUNTA: {q}\n\nEstas histórias contêm a resposta à pergunta? "
        "Responde APENAS 'SIM' ou 'NÃO'.",
        CLASSIFIER_SYS, num_predict=6)
    return v.strip().upper().startswith("SIM")

@app.route("/api/ask", methods=["POST"])
def ask():
    q = (request.get_json(force=True).get("question") or "").strip()
    if not q:
        return jsonify({"error": "pergunta vazia"}), 400
    c = db()
    rows = c.execute("SELECT story_id, text, emb FROM chunks").fetchall()
    if not rows:
        return jsonify({"answer": "Ainda não há histórias gravadas. Grava a primeira história do Pai!",
                        "sources": []})
    qe = embed(q)
    scored = sorted(((cosine(qe, json.loads(r[2])), r[0], r[1]) for r in rows),
                    key=lambda x: -x[0])[:6]
    best = scored[0][0]
    if best < SIM_HARD_FLOOR:
        return jsonify({"answer": HONEST_NO_STORY, "sources": [], "gated": "floor",
                        "best_score": round(best, 3)})
    ctx = "\n\n---\n\n".join(s[2] for s in scored if s[0] > 0.25)
    if not stories_contain_answer(ctx, q):
        return jsonify({"answer": HONEST_NO_STORY, "sources": [], "gated": "classifier",
                        "best_score": round(best, 3)})
    answer = generate(f"HISTÓRIAS DO PAI:\n{ctx}\n\nPERGUNTA DA FAMÍLIA: {q}\n\nRESPOSTA:",
                      SYSTEM_ASK)
    src = sorted({s[1] for s in scored if s[0] > 0.25})
    return jsonify({"answer": answer, "sources": src, "best_score": round(best, 3)})

@app.route("/api/translate", methods=["POST"])
def translate():
    body = request.get_json(force=True)
    text = (body.get("text") or "").strip()
    target = (body.get("target") or "français").strip()
    if not text:
        return jsonify({"error": "texto vazio"}), 400
    out = generate(f"Traduis en {target}, naturel et simple :\n\n{text}",
                   "Tu es un traducteur. Retourne UNIQUEMENT la traduction.", num_predict=400)
    return jsonify({"translation": out})

VOICE_SVC = os.environ.get("VOICE_SVC", "http://127.0.0.1:5578")
_voice_jobs = {}  # job_id -> {"status": pending|done|error, "audio": bytes|None, "error": str}

def _voice_worker(job_id, text, lang):
    import urllib.request
    try:
        req = urllib.request.Request(
            VOICE_SVC + "/speak",
            data=json.dumps({"text": text, "lang": lang}).encode(),
            headers={"Content-Type": "application/json"})
        audio = urllib.request.urlopen(req, timeout=900).read()
        _voice_jobs[job_id].update(status="done", audio=audio)
    except Exception as e:
        _voice_jobs[job_id].update(status="error", error=str(e))

@app.route("/api/speak_clone", methods=["POST"])
def speak_clone_start():
    """Start async voice-clone synthesis (CPU XTTS can take ~2min; Cloudflare kills long requests)."""
    import threading
    body = request.get_json(force=True)
    text = (body.get("text") or "").strip()
    if not text:
        return jsonify({"error": "texto vazio"}), 400
    job_id = str(uuid.uuid4())[:10]
    _voice_jobs[job_id] = {"status": "pending", "audio": None, "error": None}
    threading.Thread(target=_voice_worker, args=(job_id, text, body.get("lang") or "pt"),
                     daemon=True).start()
    return jsonify({"job_id": job_id})

@app.route("/api/speak_clone/<job_id>")
def speak_clone_poll(job_id):
    job = _voice_jobs.get(job_id)
    if not job:
        return jsonify({"error": "job desconhecido"}), 404
    if job["status"] == "pending":
        return jsonify({"status": "pending"}), 202
    if job["status"] == "error":
        return jsonify({"status": "error", "error": job["error"]}), 500
    audio = job.pop("audio")  # one-shot delivery frees memory
    return app.response_class(audio, mimetype="audio/wav")

@app.route("/api/stats")
def stats():
    c = db()
    ns = c.execute("SELECT COUNT(*) FROM stories").fetchone()[0]
    nw = c.execute("SELECT COALESCE(SUM(LENGTH(text)-LENGTH(REPLACE(text,' ',''))+1),0) FROM stories").fetchone()[0]
    return jsonify({"stories": ns, "words": int(nw or 0)})

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5577, threaded=True)
