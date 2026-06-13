#!/usr/bin/env bash
# TerraPilot - Deploy idempotente para Alibaba Cloud ECS
# Execute este script dentro de uma instância Ubuntu ECS.

set -euo pipefail

APP_NAME="terrapilot"
REPO_URL="${REPO_URL:-https://github.com/kaiquetheodoro/TerraPilot.git}"
APP_DIR="${APP_DIR:-/opt/TerraPilot}"
IMAGE_NAME="${IMAGE_NAME:-terrapilot:latest}"
CONTAINER_NAME="${CONTAINER_NAME:-terrapilot}"
APP_PORT="${APP_PORT:-8000}"
PUBLIC_PORT="${PUBLIC_PORT:-80}"
ECS_REGION="${ECS_REGION:-ap-southeast-1}"
LOGTAIL_SCRIPT_URL="https://logtail-release-${ECS_REGION}.oss-${ECS_REGION}.aliyuncs.com/linux64/logtail.sh"

log() {
    echo "[$(date '+%H:%M:%S')] $1"
}

require_sudo() {
    if ! sudo -n true 2>/dev/null; then
        log "🔐 Este script precisa de sudo. Você pode ser solicitado a informar a senha."
        sudo true
    fi
}

install_system_packages() {
    # Atualização idempotente do sistema e pacotes mínimos para deploy.
    log "📦 Atualizando sistema e instalando dependências base..."
    sudo apt update
    sudo apt install -y ca-certificates curl git gnupg lsb-release
}

install_docker() {
    # Instala Docker apenas quando ainda não estiver disponível.
    if command -v docker >/dev/null 2>&1; then
        log "🐳 Docker já instalado: $(docker --version)"
        return
    fi

    log "🐳 Instalando Docker..."
    curl -fsSL https://get.docker.com -o /tmp/get-docker.sh
    sudo sh /tmp/get-docker.sh
    sudo usermod -aG docker "${USER}"
    log "✅ Docker instalado. Se o grupo docker não aplicar nesta sessão, o script usará sudo."
}

sync_repository() {
    # Clona na primeira execução e faz pull nas execuções seguintes.
    log "📥 Sincronizando repositório em ${APP_DIR}..."
    if [ -d "${APP_DIR}/.git" ]; then
        sudo git -C "${APP_DIR}" fetch origin main
        sudo git -C "${APP_DIR}" reset --hard origin/main
    else
        sudo mkdir -p "$(dirname "${APP_DIR}")"
        sudo git clone "${REPO_URL}" "${APP_DIR}"
    fi
    sudo chown -R "${USER}:${USER}" "${APP_DIR}"
}

configure_environment() {
    # Cria .env a partir do template sem sobrescrever credenciais já configuradas.
    log "⚙️  Configurando variáveis de ambiente..."
    cd "${APP_DIR}"
    if [ ! -f .env ]; then
        cp .env.example .env
        log "⚠️  .env criado a partir de .env.example."
        log "⚠️  Edite /opt/TerraPilot/.env com credenciais reais antes do tráfego de produção."
    else
        log "✅ .env existente preservado."
    fi
}

build_and_run_container() {
    # Rebuild sempre usa o código atual; container antigo é removido se existir.
    log "🏗️  Buildando imagem Docker ${IMAGE_NAME}..."
    cd "${APP_DIR}"
    sudo docker build -t "${IMAGE_NAME}" .

    if sudo docker ps -a --format '{{.Names}}' | grep -qx "${CONTAINER_NAME}"; then
        log "♻️  Removendo container anterior ${CONTAINER_NAME}..."
        sudo docker rm -f "${CONTAINER_NAME}" >/dev/null
    fi

    log "▶️  Iniciando container ${CONTAINER_NAME}..."
    sudo docker run -d \
        --name "${CONTAINER_NAME}" \
        --restart unless-stopped \
        --env-file .env \
        -p "${PUBLIC_PORT}:${APP_PORT}" \
        "${IMAGE_NAME}"
}

install_logtail() {
    # Instala o Logtail Agent para envio de logs ao Alibaba Cloud SLS.
    log "📊 Instalando/verificando Alibaba Cloud Logtail Agent..."
    if command -v ilogtail >/dev/null 2>&1 || [ -d /usr/local/ilogtail ]; then
        log "✅ Logtail Agent já parece instalado."
        return
    fi

    curl -fsSL "${LOGTAIL_SCRIPT_URL}" -o /tmp/logtail.sh
    chmod +x /tmp/logtail.sh
    sudo /tmp/logtail.sh install "${ECS_REGION}"
    log "✅ Logtail Agent instalado para região ${ECS_REGION}."
}

wait_for_healthcheck() {
    # Healthcheck local garante que o FastAPI subiu antes de encerrar o deploy.
    log "🩺 Aguardando healthcheck em http://localhost:${PUBLIC_PORT}/health..."
    for attempt in $(seq 1 30); do
        if curl -fsS "http://localhost:${PUBLIC_PORT}/health" >/dev/null; then
            log "✅ Healthcheck OK na tentativa ${attempt}."
            return
        fi
        sleep 2
    done

    log "❌ Healthcheck falhou. Últimos logs do container:"
    sudo docker logs --tail 80 "${CONTAINER_NAME}" || true
    exit 1
}

print_summary() {
    PUBLIC_IP="$(curl -fsS --max-time 3 ifconfig.me || echo '<ECS_PUBLIC_IP>')"
    log "🎉 Deploy concluído!"
    log "🌐 API: http://${PUBLIC_IP}:${PUBLIC_PORT}"
    log "🩺 Health: http://${PUBLIC_IP}:${PUBLIC_PORT}/health"
    log "📌 Status: código pronto; conta Alibaba Cloud em verificação de identidade desde 08/06/2026."
    log "🔒 Abra a porta ${PUBLIC_PORT} no Security Group da ECS, se ainda não estiver aberta."
}

main() {
    log "🚀 Iniciando deploy do ${APP_NAME} na Alibaba Cloud ECS..."
    require_sudo
    install_system_packages
    install_docker
    sync_repository
    configure_environment
    build_and_run_container
    install_logtail
    wait_for_healthcheck
    print_summary
}

main "$@"