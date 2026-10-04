#!/usr/bin/env bash
# transformers 4.57.x: satisfies coqui-tts>=4.57 AND still has isin_mps_friendly (removed only in 5.x)
set -e
/opt/data/projet/avozdaavo/venv-xtts/bin/pip install -q "transformers==4.57.1"
echo "TRANSFORMERS_457_OK"
