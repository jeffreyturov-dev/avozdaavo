#!/usr/bin/env bash
# Install transformers 4.57.1 then start the XTTS voice server (downloads weights on first run)
set -e
cd /opt/data/projet/avozdaavo
if ! ./venv-xtts/bin/pip show transformers 2>/dev/null | grep -q "Version: 4.57.1"; then
  ./venv-xtts/bin/pip install -q "transformers==4.57.1"
fi
echo "TRANSFORMERS_OK"
export PYTHONUNBUFFERED=1 COQUI_TOS_AGREED=1
exec ./venv-xtts/bin/python voice_server.py
