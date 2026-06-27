#!/bin/bash
# TerraPilot - Inicia todos os serviços para gravação
set -e

echo "🌱 Iniciando TerraPilot..."
echo ""

# Ativa venv
source .venv/bin/activate

# Mata processos antigos (se existirem)
pkill -f "uvicorn src.api.main" 2>/dev/null || true
pkill -f "http.server 8080" 2>/dev/null || true
pkill -f "http.server 8081" 2>/dev/null || true
pkill -f "http.server 8082" 2>/dev/null || true
sleep 1

echo "📡 [1/4] Iniciando API (porta 8001)..."
uvicorn src.api.main:app --host 0.0.0.0 --port 8001 > /tmp/terrapilot-api.log 2>&1 &
API_PID=$!

echo "📱 [2/4] Iniciando PWA do Raimundo (porta 8080)..."
cd frontend/pwa
python3 -m http.server 8080 > /tmp/terrapilot-pwa.log 2>&1 &
PWA_PID=$!
cd ../..

echo "👩‍💼 [3/4] Iniciando Painel da Luana (porta 8081)..."
cd frontend/analyst
python3 -m http.server 8081 > /tmp/terrapilot-analyst.log 2>&1 &
ANALYST_PID=$!
cd ../..

echo "💬 [4/4] Iniciando Simulador WhatsApp (porta 8082)..."
cd frontend/pwa
python3 -m http.server 8082 > /tmp/terrapilot-whatsapp.log 2>&1 &
WHATSAPP_PID=$!
cd ../..

# Aguarda API subir
echo ""
echo "⏳ Aguardando API subir..."
for i in {1..10}; do
    if curl -s http://localhost:8001/health > /dev/null 2>&1; then
        echo "✅ API online!"
        break
    fi
    sleep 1
done

echo ""
echo "═══════════════════════════════════════════════"
echo "  🎬 TODOS OS SERVIÇOS RODANDO"
echo "═══════════════════════════════════════════════"
echo ""
echo "  📱 PWA do Raimundo:    http://localhost:8080"
echo "  👩‍💼 Painel da Luana:    http://localhost:8081"
echo "  💬 Simulador WhatsApp: http://localhost:8082/whatsapp-simulator.html"
echo "  📖 API Swagger:        http://localhost:8001/docs"
echo "  ❤️  Health check:       http://localhost:8001/health"
echo ""
echo "  PIDs: API=$API_PID | PWA=$PWA_PID | Analista=$ANALYST_PID | WA=$WHATSAPP_PID"
echo ""
echo "  Para parar: pkill -f 'http.server|uvicorn src.api.main'"
echo "═══════════════════════════════════════════════"
echo ""
echo "Pressione Ctrl+C para parar tudo"

# Captura Ctrl+C
trap "echo ''; echo '🛑 Parando serviços...'; kill $API_PID $PWA_PID $ANALYST_PID $WHATSAPP_PID 2>/dev/null; echo '✅ Pronto.'; exit" INT

wait