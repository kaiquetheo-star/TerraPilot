#!/usr/bin/env bash
set -e

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "📱 Validando responsividade mobile..."

PWA_PID=""
if ! curl -sf http://localhost:8080 > /dev/null; then
    echo "Iniciando PWA..."
    cd frontend/pwa && python3 -m http.server 8080 &
    PWA_PID=$!
    sleep 2
    cd "$ROOT"
fi

if [ -d ".venv" ]; then
    # shellcheck disable=SC1091
    source .venv/bin/activate
fi

pip install pytest-playwright > /dev/null 2>&1 || true
playwright install chromium > /dev/null 2>&1 || true

pytest scripts/test_mobile_responsiveness.py -v

if [ -n "$PWA_PID" ]; then
    kill "$PWA_PID" 2>/dev/null || true
fi

echo "✅ Validação mobile concluída"
