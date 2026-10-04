#!/usr/bin/env bash
# torch 2.8 (CPU) — last line that does NOT require CUDA-linked torchcodec for coqui-tts
set -e
V=/opt/data/projet/avozdaavo/venv-xtts/bin
$V/pip uninstall -y -q torchcodec 2>/dev/null || true
$V/pip install -q torch==2.8.0 torchaudio==2.8.0 --index-url https://download.pytorch.org/whl/cpu
echo "TORCH28_OK"
