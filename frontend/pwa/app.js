// Estado da aplicação
let currentGPS = null;
let pendingSubmissions = [];

// Elementos do DOM
const statusBar = document.getElementById('status-bar');
const carForm = document.getElementById('car-form');
const getGpsBtn = document.getElementById('get-gps-btn');
const gpsDisplay = document.getElementById('gps-display');
const pendingCountDiv = document.getElementById('pending-count');
const countNumber = document.getElementById('count-number');
const syncBtn = document.getElementById('sync-btn');
const toast = document.getElementById('toast');
const toastMessage = document.getElementById('toast-message');

// Inicialização
document.addEventListener('DOMContentLoaded', () => {
    loadPendingSubmissions();
    updateOnlineStatus();
    setupEventListeners();
    registerServiceWorker();
});

// Event Listeners
function setupEventListeners() {
    // Monitorar conexão
    window.addEventListener('online', updateOnlineStatus);
    window.addEventListener('offline', updateOnlineStatus);
    
    // Capturar GPS
    getGpsBtn.addEventListener('click', captureGPS);
    
    // Submeter formulário
    carForm.addEventListener('submit', handleSubmit);
    
    // Sincronizar
    syncBtn.addEventListener('click', syncSubmissions);
}

// Atualizar status online/offline
function updateOnlineStatus() {
    if (navigator.onLine) {
        statusBar.textContent = '🟢 ONLINE - Pronto para sincronizar';
        statusBar.className = 'fixed top-0 left-0 right-0 p-2 text-center text-sm font-bold z-50 status-online';
    } else {
        statusBar.textContent = '🔴 OFFLINE - Dados serão salvos localmente';
        statusBar.className = 'fixed top-0 left-0 right-0 p-2 text-center text-sm font-bold z-50 status-offline';
    }
}

// Capturar coordenadas GPS
function captureGPS() {
    if (!navigator.geolocation) {
        showToast('❌ Geolocalização não suportada neste dispositivo');
        return;
    }
    
    getGpsBtn.disabled = true;
    getGpsBtn.textContent = '⏳ Capturando...';
    
    navigator.geolocation.getCurrentPosition(
        (position) => {
            currentGPS = {
                lat: position.coords.latitude,
                lng: position.coords.longitude,
                accuracy: position.coords.accuracy
            };
            
            document.getElementById('gps-lat').value = currentGPS.lat;
            document.getElementById('gps-lng').value = currentGPS.lng;
            
            gpsDisplay.innerHTML = `
                <p class="text-green-400 font-bold">✅ Localização capturada!</p>
                <p class="text-sm mt-2">Lat: ${currentGPS.lat.toFixed(6)}</p>
                <p class="text-sm">Lng: ${currentGPS.lng.toFixed(6)}</p>
                <p class="text-sm text-gray-500">Precisão: ${currentGPS.accuracy.toFixed(0)}m</p>
            `;
            
            getGpsBtn.disabled = false;
            getGpsBtn.textContent = '📍 Capturar Novamente';
            showToast('✅ Localização capturada com sucesso!');
        },
        (error) => {
            gpsDisplay.innerHTML = `<p class="text-red-400">❌ Erro: ${error.message}</p>`;
            getGpsBtn.disabled = false;
            getGpsBtn.textContent = '📍 Tentar Novamente';
            showToast('❌ Não foi possível capturar localização');
        },
        {
            enableHighAccuracy: true,
            timeout: 10000,
            maximumAge: 0
        }
    );
}

// Submeter formulário
async function handleSubmit(e) {
    e.preventDefault();
    
    const submission = {
        id: Date.now().toString(),
        farmer_id: document.getElementById('farmer-id').value,
        area_ha: parseFloat(document.getElementById('area-ha').value),
        vegetation_type: document.getElementById('vegetation-type').value,
        gps_coords: currentGPS ? [currentGPS.lat, currentGPS.lng] : null,
        notes: document.getElementById('notes').value,
        timestamp: new Date().toISOString(),
        synced: false
    };
    
    // Validar GPS
    if (!submission.gps_coords) {
        showToast('❌ Capture a localização GPS antes de salvar');
        return;
    }
    
    // Salvar localmente
    pendingSubmissions.push(submission);
    savePendingSubmissions();
    
    // Limpar formulário
    carForm.reset();
    currentGPS = null;
    gpsDisplay.innerHTML = 'Aguardando captura...';
    
    showToast('✅ Cadastro salvo! Será sincronizado quando houver conexão.');
    
    // Tentar sincronizar se online
    if (navigator.onLine) {
        await syncSubmissions();
    }
}

// Salvar no localStorage
function savePendingSubmissions() {
    localStorage.setItem('terrapilot_submissions', JSON.stringify(pendingSubmissions));
    updatePendingCount();
}

// Carregar do localStorage
function loadPendingSubmissions() {
    const stored = localStorage.getItem('terrapilot_submissions');
    if (stored) {
        pendingSubmissions = JSON.parse(stored);
        updatePendingCount();
    }
}

// Atualizar contador
function updatePendingCount() {
    const count = pendingSubmissions.filter(s => !s.synced).length;
    
    if (count > 0) {
        countNumber.textContent = count;
        pendingCountDiv.classList.remove('hidden');
    } else {
        pendingCountDiv.classList.add('hidden');
    }
}

// Sincronizar com backend
async function syncSubmissions() {
    const unsynced = pendingSubmissions.filter(s => !s.synced);
    
    if (unsynced.length === 0) {
        showToast('✅ Todos os cadastros já estão sincronizados');
        return;
    }
    
    showToast(`🔄 Sincronizando ${unsynced.length} cadastros...`);
    
    for (const submission of unsynced) {
        try {
            const response = await fetch('http://localhost:8000/api/validate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(submission)
            });
            
            if (response.ok) {
                submission.synced = true;
                showToast(`✅ Cadastro ${submission.farmer_id} sincronizado!`);
            } else {
                throw new Error(`HTTP ${response.status}`);
            }
        } catch (error) {
            console.error('Erro ao sincronizar:', error);
            showToast(`❌ Erro ao sincronizar ${submission.farmer_id}`);
        }
    }
    
    savePendingSubmissions();
}

// Mostrar toast
function showToast(message) {
    toastMessage.textContent = message;
    toast.classList.remove('hidden');
    
    setTimeout(() => {
        toast.classList.add('hidden');
    }, 3000);
}

// Registrar Service Worker (PWA)
function registerServiceWorker() {
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.register('service-worker.js')
            .then(() => console.log('Service Worker registrado'))
            .catch(err => console.log('Erro ao registrar Service Worker:', err));
    }
}