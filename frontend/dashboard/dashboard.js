// Dados mockados (em produção, viriam da API)
let submissions = [
    {
        id: '1',
        farmer_id: 'raimundo_001',
        area_ha: 50,
        vegetation_type: 'Cerrado',
        gps_coords: [-15.7801, -47.9292],
        confidence_score: 87,
        flag_status: 'Aprovado',
        reasoning: 'Área dentro dos parâmetros esperados para Cerrado',
        timestamp: '2026-01-09T10:30:00Z',
        status: 'approved'
    },
    {
        id: '2',
        farmer_id: 'maria_042',
        area_ha: 120,
        vegetation_type: 'Amazônia',
        gps_coords: [-3.1234, -60.5678],
        confidence_score: 45,
        flag_status: 'Revisão Manual',
        reasoning: 'Área muito grande requer validação humana',
        timestamp: '2026-01-09T11:15:00Z',
        status: 'pending'
    },
    {
        id: '3',
        farmer_id: 'joao_087',
        area_ha: 0.5,
        vegetation_type: 'Mata Atlântica',
        gps_coords: [-23.5505, -46.6333],
        confidence_score: 20,
        flag_status: 'Inconsistente',
        reasoning: 'Área declarada é muito pequena',
        timestamp: '2026-01-09T12:00:00Z',
        status: 'pending'
    }
];

let currentFilter = 'all';
let selectedSubmission = null;

// Inicialização
document.addEventListener('DOMContentLoaded', () => {
    renderSubmissions();
    updateStats();
    setupEventListeners();
});

function setupEventListeners() {
    // Filtros
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            document.querySelectorAll('.filter-btn').forEach(b => {
                b.classList.remove('active', 'bg-blue-600', 'text-white');
                b.classList.add('bg-gray-200', 'text-gray-700');
            });
            e.target.classList.add('active', 'bg-blue-600', 'text-white');
            e.target.classList.remove('bg-gray-200', 'text-gray-700');
            
            currentFilter = e.target.dataset.filter;
            renderSubmissions();
        });
    });
    
    // Modal
    document.getElementById('close-modal').addEventListener('click', closeModal);
    document.getElementById('approve-btn').addEventListener('click', () => handleDecision('approved'));
    document.getElementById('reject-btn').addEventListener('click', () => handleDecision('rejected'));
}

function renderSubmissions() {
    const tbody = document.getElementById('submissions-table');
    
    let filtered = submissions;
    if (currentFilter !== 'all') {
        filtered = submissions.filter(s => s.status === currentFilter);
    }
    
    tbody.innerHTML = filtered.map(sub => `
        <tr class="hover:bg-gray-50 cursor-pointer" onclick="openModal('${sub.id}')">
            <td class="px-6 py-4 text-sm text-gray-900">${sub.id}</td>
            <td class="px-6 py-4 text-sm font-medium text-gray-900">${sub.farmer_id}</td>
            <td class="px-6 py-4 text-sm text-gray-900">${sub.area_ha}</td>
            <td class="px-6 py-4 text-sm text-gray-900">${sub.vegetation_type}</td>
            <td class="px-6 py-4">
                <div class="flex items-center">
                    <div class="w-24 bg-gray-200 rounded-full h-2 mr-2">
                        <div class="bg-${getScoreColor(sub.confidence_score)}-600 h-2 rounded-full" 
                             style="width: ${sub.confidence_score}%"></div>
                    </div>
                    <span class="text-sm font-medium">${sub.confidence_score}%</span>
                </div>
            </td>
            <td class="px-6 py-4">
                <span class="px-2 py-1 text-xs font-semibold rounded-full ${getStatusBadge(sub.status)}">
                    ${getStatusLabel(sub.status)}
                </span>
            </td>
            <td class="px-6 py-4 text-sm">
                <button class="text-blue-600 hover:text-blue-900 font-medium">Ver Detalhes</button>
            </td>
        </tr>
    `).join('');
}

function updateStats() {
    const pending = submissions.filter(s => s.status === 'pending').length;
    const approved = submissions.filter(s => s.status === 'approved').length;
    const rejected = submissions.filter(s => s.status === 'rejected').length;
    
    document.getElementById('stat-pending').textContent = pending;
    document.getElementById('stat-approved').textContent = approved;
    document.getElementById('stat-rejected').textContent = rejected;
}

function openModal(id) {
    selectedSubmission = submissions.find(s => s.id === id);
    
    const modalContent = document.getElementById('modal-content');
    modalContent.innerHTML = `
        <div class="space-y-4">
            <div class="grid grid-cols-2 gap-4">
                <div>
                    <p class="text-sm text-gray-600">ID do Produtor</p>
                    <p class="font-semibold">${selectedSubmission.farmer_id}</p>
                </div>
                <div>
                    <p class="text-sm text-gray-600">Área (hectares)</p>
                    <p class="font-semibold">${selectedSubmission.area_ha}</p>
                </div>
                <div>
                    <p class="text-sm text-gray-600">Tipo de Vegetação</p>
                    <p class="font-semibold">${selectedSubmission.vegetation_type}</p>
                </div>
                <div>
                    <p class="text-sm text-gray-600">Coordenadas GPS</p>
                    <p class="font-semibold text-sm">${selectedSubmission.gps_coords.join(', ')}</p>
                </div>
            </div>
            
            <div class="border-t pt-4">
                <p class="text-sm text-gray-600 mb-2">Análise da IA</p>
                <div class="bg-blue-50 p-4 rounded-lg">
                    <div class="flex items-center mb-2">
                        <span class="text-sm font-semibold mr-2">Confiança:</span>
                        <span class="text-lg font-bold text-blue-600">${selectedSubmission.confidence_score}%</span>
                    </div>
                    <p class="text-sm text-gray-700">${selectedSubmission.reasoning}</p>
                </div>
            </div>
            
            <div>
                <p class="text-sm text-gray-600">Status Atual</p>
                <span class="inline-block px-3 py-1 text-sm font-semibold rounded-full ${getStatusBadge(selectedSubmission.status)}">
                    ${getStatusLabel(selectedSubmission.status)}
                </span>
            </div>
        </div>
    `;
    
    document.getElementById('detail-modal').classList.remove('hidden');
}

function closeModal() {
    document.getElementById('detail-modal').classList.add('hidden');
    selectedSubmission = null;
}

function handleDecision(decision) {
    if (!selectedSubmission) return;
    
    selectedSubmission.status = decision;
    
    // Em produção, enviaria para API
    console.log(`Decisão: ${decision} para submissão ${selectedSubmission.id}`);
    
    closeModal();
    renderSubmissions();
    updateStats();
    
    alert(`✅ Cadastro ${decision === 'approved' ? 'aprovado' : 'rejeitado'} com sucesso!`);
}

function getScoreColor(score) {
    if (score >= 80) return 'green';
    if (score >= 50) return 'yellow';
    return 'red';
}

function getStatusBadge(status) {
    const badges = {
        pending: 'bg-yellow-100 text-yellow-800',
        approved: 'bg-green-100 text-green-800',
        rejected: 'bg-red-100 text-red-800'
    };
    return badges[status] || 'bg-gray-100 text-gray-800';
}

function getStatusLabel(status) {
    const labels = {
        pending: '⏳ Pendente',
        approved: '✅ Aprovado',
        rejected: '❌ Rejeitado'
    };
    return labels[status] || status;
}

// Expor função globalmente para onclick
window.openModal = openModal;