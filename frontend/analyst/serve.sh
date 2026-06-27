#!/usr/bin/env bash
# Serve o frontend do módulo analista na porta 8081
# Uso: bash frontend/analyst/serve.sh

cd "$(dirname "$0")"
echo "🌿 TerraPilot Analista — http://localhost:8081"
echo "   API esperada em http://localhost:8001"
python3 -m http.server 8081
