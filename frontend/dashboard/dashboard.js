// Dados mockados (em produção viriam da API)
let submissions = [
    {
        id: 'CAR-2026-001',
        farmer_id: 'raimundo_001',
        farmer_name: 'Raimundo dos Santos',
        area_ha: 50,
        vegetation_types: ['Cerrado'],
        gps_coords: [-15.7801, -47.9292],
        confidence_score: 92,
        flag_status: 'Aprovado',
        reasoning: 'Área de 50ha de Cerrado dentro dos parâmetros legais. APP preservada conforme imagem. Reserva Legal compatível com o bioma.',
        timestamp: '2026-06-09T08:30:00Z',
        status: 'pending',
        photos_count: 5
    },
    {
        id: 'CAR-2026-002',
        farmer_id: 'maria_042',
        farmer_name: 'Maria Aparecida Silva',
        area_ha: 120,
        vegetation_types: ['Amazônia', 'Mata Atlântica'],
        gps_coords: [-3.1234, -60.5678],
        confidence_score: 45,
        flag_status: 'Revisão Manual',
        reasoning: 'Área extensa requer validação presencial. Duas formações vegetais distintas detectadas. Possível sobreposição com Terra Indígena próxima.',
        timestamp: '2026-06-09T09:15:00Z',
        status: 'pending',
        photos_count: 8
    },
    {
        id: 'CAR-2026-003',
        farmer_id: 'joao_087',
        farmer_name: 'João Pereira Lima',
        area_ha: 0.5,
        vegetation_types: ['Mata Atlântica'],
        gps_coords: [-23.5505, -46.6333],
        confidence_score: 18,
        flag_status: 'Inconsistente',
        reasoning: 'Área declarada inferior ao módulo fiscal mínimo da região. Coordenadas apontam para zona urbana. Necessita verificação documental.',
        timestamp: '2026-06-09T10:00:00Z',
        status: 'pending',
        photos_count: 2
    },
    {
        id: 'CAR-2026-004',
        farmer_id: 'ana_156',
        farmer_name: 'Ana Carolina Souza',
        area_ha: 35,
        vegetation_types: ['Caatinga'],
        gps_coords: [-8.0542, -34.8891],
        confidence_score: 88,
        flag_status: 'Aprovado',
        reasoning: 'Cadastro consistente com dados do INCRA. Vegetação de Caatinga preservada. APP de rio perene demarcada corretamente.',
        timestamp: '2026-06-09T07:45:00Z',
        status: 'approved',
        photos_count: 4
    },
    {
        id: 'CAR-2026-005',
        farmer_id: 'carlos_203',
        farmer_name: 'Carlos Eduardo Oliveira',
        area_ha: 200,
        vegetation_types: ['Pantanal'],
        gps_coords: [-19.0154, -57.6542],
        confidence_score: 35,
        flag_status: 'Revisão Manual',
        reasoning: 'Área significativa no bioma Pantanal. Necessária análise de impacto ambiental. Verificar licenciamento de atividade pecuária.',
        timestamp: '2026-06-09T11:30:00Z',
        status: 'pending',
        photos_count: 12
    },
    {
        id: 'CAR-2026-006',
        farmer_id: 'fatima_089',
        farmer_name: 'Fátima Rodrigues',
        area_ha: 15,
        vegetation_types: ['Pampa'],
        gps_coords: [-30.0345, -51.2301],
        confidence_score: 22,
        flag_status: 'Rejeitado',
        reasoning: 'Sobreposição detectada com Unidade de Conservação Federal. Documentação apresentada incompatível com a localização geográfica.',
        timestamp: '2026-06-09T06:20:00Z',
        status: 'rejected',
        photos_count: 3
    }
];

let currentFilter = 'all';
let selectedSubmission = null;

// Inicialização
document.addEventListener('DOMContentLoaded', () => {
    renderTable();
    updateStats();
    setupEvents();
});

function setupEvents() {
    // Filtros
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            currentFilter = btn.dataset.filter;
            renderTable();
        });
    });
    
    // Modal
    document.getElementById('modal-close').addEventListener('click', closeModal);
    document.getElementById('modal-overlay').addEventListener('click', (e) => {
        if (e.target.id === 'modal-overlay') closeModal();
    });
    
    // Ações
    document.getElementById('btn-approve').addEventListener('click', () => handleDecision('approved'));
    document.getElementById('btn-reject').addEventListener('click', () => handleDecision('rejected'));
    
    // ESC para fechar modal
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') closeModal();
    });
}

function getPriority(score) {
    if (score >= 80) return 'low';
    if (score >= 50) return 'medium';
    return 'high';
}

function getPriorityLabel(score) {
    if (score >= 80) return '🟢 Baixa';
    if (score >= 50) return '🟡 Média';
    return '🔴 Alta';
}

function getStatusBadge(status) {
    const map = {
        pending: { class: 'status-pending', label: '⏳ Pendente' },
        approved: { class: 'status-approved', label: '✅ Aprovado' },
        rejected: { class: 'status-rejected', label: '❌ Rejeitado' }
    };
    return map[status] || map.pending;
}

function getConfidenceClass(score) {
    if (score >= 80) return 'high';
    if (score >= 50) return 'medium';
    return 'low';
}

function renderTable() {
    const tbody = document.getElementById('submissions-table');
    const emptyState = document.getElementById('empty-state');
    
    let filtered = submissions;
    if (currentFilter !== 'all') {
        filtered = submissions.filter(s => s.status === currentFilter);
    }
    
    // Ordenar: pendentes primeiro, depois por confidence score (asc - mais críticos primeiro)
    filtered.sort((a, b) => {
        if (a.status === 'pending' && b.status !== 'pending') return -1;
        if (a.status !== 'pending' && b.status === 'pending') return 1;
        return a.confidence_score - b.confidence_score;
    });
    
    if (filtered.length === 0) {
        tbody.innerHTML = '';
        emptyState.classList.remove('hidden');
        return;
    }
    
    emptyState.classList.add('hidden');
    
    tbody.innerHTML = filtered.map(sub => {
        const priority = getPriority(sub.confidence_score);
        const statusBadge = getStatusBadge(sub.status);
        const confClass = getConfidenceClass(sub.confidence_score);
        
        return `
            <tr>
                <td>
                    <span class="priority-badge priority-${priority}">
                        ${getPriorityLabel(sub.confidence_score)}
                    </span>
                </td>
                <td>
                    <div style="font-weight: 500;">${sub.farmer_name}</div>
                    <div style="font-size: 11px; color: #64748b;">${sub.farmer_id}</div>
                </td>
                <td>${sub.area_ha}</td>
                <td>${sub.vegetation_types.join(', ')}</td>
                <td>
                    <div class="confidence-cell">
                        <div class="confidence-bar">
                            <div class="confidence-fill ${confClass}" style="width: ${sub.confidence_score}%"></div>
                        </div>
                        <span class="confidence-value" style="color: ${confClass === 'high' ? '#16a34a' : confClass === 'medium' ? '#d97706' : '#dc2626'}">${sub.confidence_score}%</span>
                    </div>
                </td>
                <td>
                    <span class="status-badge ${statusBadge.class}">${statusBadge.label}</span>
                </td>
                <td>
                    <button class="action-btn" onclick="openModal('${sub.id}')">
                        Ver Detalhes
                    </button>
                </td>
            </tr>
        `;
    }).join('');
    
    updateCounts();
}

function updateStats() {
    const pending = submissions.filter(s => s.status === 'pending').length;
    const approved = submissions.filter(s => s.status === 'approved').length;
    const rejected = submissions.filter(s => s.status === 'rejected').length;
    
    document.getElementById('stat-pending').textContent = pending;
    document.getElementById('stat-approved').textContent = approved;
    document.getElementById('stat-rejected').textContent = rejected;
}

function updateCounts() {
    document.getElementById('count-all').textContent = submissions.length;
    document.getElementById('count-pending').textContent = submissions.filter(s => s.status === 'pending').length;
    document.getElementById('count-approved').textContent = submissions.filter(s => s.status === 'approved').length;
    document.getElementById('count-rejected').textContent = submissions.filter(s => s.status === 'rejected').length;
}

function openModal(id) {
    selectedSubmission = submissions.find(s => s.id === id);
    if (!selectedSubmission) return;
    
    const modalBody = document.getElementById('modal-body');
    const modalFooter = document.getElementById('modal-footer');
    const confClass = getConfidenceClass(selectedSubmission.confidence_score);
    
    modalBody.innerHTML = `
        <div class="detail-grid">
            <div class="detail-item">
                <label>ID do Produtor</label>
                <span>${selectedSubmission.farmer_id}</span>
            </div>
            <div class="detail-item">
                <label>Nome</label>
                <span>${selectedSubmission.farmer_name}</span>
            </div>
            <div class="detail-item">
                <label>Área (hectares)</label>
                <span>${selectedSubmission.area_ha} ha</span>
            </div>
            <div class="detail-item">
                <label>Vegetação</label>
                <span>${selectedSubmission.vegetation_types.join(', ')}</span>
            </div>
            <div class="detail-item">
                <label>Coordenadas GPS</label>
                <span style="font-family: monospace; font-size: 12px;">${selectedSubmission.gps_coords[0].toFixed(4)}, ${selectedSubmission.gps_coords[1].toFixed(4)}</span>
            </div>
            <div class="detail-item">
                <label>Fotos Enviadas</label>
                <span>📷 ${selectedSubmission.photos_count} fotos</span>
            </div>
        </div>
        
        <div class="ai-analysis">
            <div class="ai-analysis-title">
                🤖 Análise da IA TerraPilot
                <span class="ai-confidence" style="color: ${confClass === 'high' ? '#16a34a' : confClass === 'medium' ? '#d97706' : '#dc2626'}; margin-left: auto;">
                    ${selectedSubmission.confidence_score}%
                </span>
            </div>
            <div class="ai-analysis-content">
                ${selectedSubmission.reasoning}
            </div>
        </div>
        
        <div style="font-size: 11px; color: #94a3b8; text-align: center;">
            Submetido em ${new Date(selectedSubmission.timestamp).toLocaleString('pt-BR')}
        </div>
    `;
    
    // Mostrar/esconder botões baseado no status
    if (selectedSubmission.status === 'pending') {
        modalFooter.innerHTML = `
            <button class="modal-btn modal-btn-reject" id="btn-reject">❌ Rejeitar</button>
            <button class="modal-btn modal-btn-approve" id="btn-approve">✅ Aprovar</button>
        `;
        document.getElementById('btn-approve').addEventListener('click', () => handleDecision('approved'));
        document.getElementById('btn-reject').addEventListener('click', () => handleDecision('rejected'));
    } else {
        const statusLabel = selectedSubmission.status === 'approved' ? '✅ Aprovado' : '❌ Rejeitado';
        modalFooter.innerHTML = `
            <div style="flex: 1; text-align: center; padding: 12px; background: ${selectedSubmission.status === 'approved' ? '#f0fdf4' : '#fef2f2'}; border-radius: 10px; color: ${selectedSubmission.status === 'approved' ? '#16a34a' : '#dc2626'}; font-weight: 600;">
                Decisão final: ${statusLabel}
            </div>
        `;
    }
    
    document.getElementById('modal-overlay').classList.add('active');
}

function closeModal() {
    document.getElementById('modal-overlay').classList.remove('active');
    selectedSubmission = null;
}

function handleDecision(decision) {
    if (!selectedSubmission) return;
    
    const btnApprove = document.getElementById('btn-approve');
    const btnReject = document.getElementById('btn-reject');
    const btn = decision === 'approved' ? btnApprove : btnReject;
    
    // Feedback visual
    btn.classList.add(decision === 'approved' ? 'success' : 'rejected');
    btn.textContent = decision === 'approved' ? '✅ Aprovado!' : '❌ Rejeitado!';
    btn.disabled = true;
    if (btnApprove) btnApprove.disabled = true;
    if (btnReject) btnReject.disabled = true;
    
    // Atualizar dados
    selectedSubmission.status = decision;
    
    setTimeout(() => {
        closeModal();
        renderTable();
        updateStats();
        showToast(decision === 'approved' 
            ? `✅ Cadastro de ${selectedSubmission.farmer_name} aprovado!` 
            : `❌ Cadastro de ${selectedSubmission.farmer_name} rejeitado`);
    }, 800);
}

function showToast(message) {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.classList.add('visible');
    setTimeout(() => toast.classList.remove('visible'), 3000);
}

// Expor para onclick inline
window.openModal = openModal;