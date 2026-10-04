#!/usr/bin/env bash
# Watchdog: keep A Voz da Avó demo (Flask + Ollama + cloudflared) alive for judging week.
set -u
APP=/opt/data/projet/avozdaavo
export OLLAMA_MODELS=/opt/data/ollama/models OLLAMA_HOST=127.0.0.1:11434

# 1. Ollama
if ! curl -s -m 5 http://127.0.0.1:11434/api/tags >/dev/null 2>&1; then
  pkill -f "ollama serve" 2>/dev/null; sleep 2
  nohup /opt/data/ollama/bin/ollama serve >> /opt/data/ollama/serve.log 2>&1 &
  sleep 5
fi

# 2. Flask app
if ! curl -s -m 5 http://127.0.0.1:5577/api/health >/dev/null 2>&1; then
  pkill -f "python3 server.py" 2>/dev/null; sleep 2
  cd "$APP" && PYTHONUNBUFFERED=1 nohup python3 server.py >> "$APP/server.log" 2>&1 &
  sleep 4
fi

# 3. Tunnel — restart if dead; if URL changed, patch README + article and push
CUR=$(grep -o "https://[a-z0-9-]*\.trycloudflare\.com" "$APP/README.md" | head -1)
if ! curl -s -m 10 "${CUR:-https://invalid.invalid}/api/health" >/dev/null 2>&1; then
  pkill -f "cloudflared tunnel" 2>/dev/null; sleep 2
  nohup /tmp/cloudflared tunnel --url http://127.0.0.1:5577 > /tmp/cloudflared_avo.log 2>&1 &
  for i in $(seq 1 15); do
    sleep 4
    NEW=$(grep -o "https://[a-z0-9-]*\.trycloudflare\.com" /tmp/cloudflared_avo.log | head -1)
    [ -n "$NEW" ] && break
  done
  if [ -n "${NEW:-}" ] && [ "$NEW" != "$CUR" ]; then
    sed -i "s|https://[a-z0-9-]*\.trycloudflare\.com|$NEW|g" "$APP/README.md" "$APP/article_dev.md" 2>/dev/null
    echo "TUNNEL_URL_CHANGED $CUR -> $NEW"
  fi
fi
