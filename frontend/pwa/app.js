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
const syncStatus = document.getElementById('sync-status');
const syncBar = document.getElementById('sync-bar');
const syncPercentage = document.getElementById('sync-percentage');
const syncStatusText = document.getElementById('sync-status-text');
const submitBtn = document.getElementById('submit-btn');
const photoInput = document.getElementById('photos');
const photoPreview = document.getElementById('photo-preview');

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
    
    // Preview de fotos
    photoInput.addEventListener('change', handlePhotoPreview);
    
    // Validação em tempo real
    document.getElementById('area-ha').addEventListener('input', validateArea);
}

// Validar área em tempo real
function validateArea(e) {
    const area = parseFloat(e.target.value);
    const validationMsg = e.target.parentElement.nextElementSibling;
    
    if (e.target.value && area < 0.1) {
        e.target.classList.add('border-red-500');
        e.target.classList.remove('border-gray-200', 'border-green-500');
        if (validationMsg) validationMsg.textContent = '⚠️ Área mínima: 0.1 ha';
    } else if (e.target.value && area > 10000) {
        e.target.classList.add('border-red-500');
        e.target.classList.remove('border-gray-200', 'border-green-500');
        if (validationMsg) validationMsg.textContent = '⚠️ Área muito grande, verifique';
    } else if (e.target.value) {
        e.target.classList.remove('border-red-500');
        e.target.classList.add('border-green-500');
        if (validationMsg) validationMsg.textContent = '✓ Área válida';
    } else {
        e.target.classList.remove('border-red-500', 'border-green-500');
        e.target.classList.add('border-gray-200');
        if (validationMsg) validationMsg.textContent = 'Mínimo: 0.1 ha';
    }
}

// Preview de fotos
function handlePhotoPreview(e) {
    photoPreview.innerHTML = '';
    const files = e.target.files;
    
    for (let i = 0; i < files.length && i < 6; i++) {
        const file = files[i];
        const reader = new FileReader();
        
        reader.onload = (event) => {
            const img = document.createElement('div');
            img.className = 'relative aspect-square rounded-lg overflow-hidden bg-gray-200';
            img.innerHTML = `
                <img src="${event.target.result}" class="w-full h-full object-cover">
                <div class="absolute bottom-0 left-0 right-0 bg-black bg-opacity-50 text-white text-xs p-1 text-center">
                    Foto ${i + 1}
                </div>
            `;
            photoPreview.appendChild(img);
        };
        
        reader.readAsDataURL(file);
    }
    
    if (files.length > 0) {
        showToast(`📸 ${files.length} foto(s) selecionada(s)`);
    }
}

// Atualizar status online/offline
function updateOnlineStatus() {
    if (navigator.onLine) {
        statusBar.innerHTML = '<i class="fas fa-wifi mr-2"></i><span>ONLINE - Pronto para sincronizar</span>';
        statusBar.className = 'fixed top-0 left-0 right-0 p-3 text-center text-sm font-bold z-50 status-online shadow-lg';
    } else {
        statusBar.innerHTML = '<i class="fas fa-wifi-slash mr-2"></i><span>OFFLINE - Dados serão salvos localmente</span>';
        statusBar.className = 'fixed top-0 left-0 right-0 p-3 text-center text-sm font-bold z-50 status-offline shadow-lg';
    }
}

// Capturar coordenadas GPS
function captureGPS() {
    if (!navigator.geolocation) {
        showToast('❌ Geolocalização não suportada neste dispositivo');
        return;
    }
    
    getGpsBtn.disabled = true;
    getGpsBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Capturando...';
    
    navigator.geolocation.getCurrentPosition(
        (position) => {
            currentGPS = {
                lat: position.coords.latitude,
                lng: position.coords.longitude,
                accuracy: position.coords.accuracy
            };
            
            document.getElementById('gps-lat').value = currentGPS.lat;
            document.getElementById('gps-lng').value = currentGPS.lng;
            
            gpsDisplay.className = 'p-4 bg-green-50 border-2 border-green-500 rounded-lg';
            gpsDisplay.innerHTML = `
                <div class="flex items-center justify-center mb-2">
                    <i class="fas fa-check-circle text-green-600 text-2xl mr-2"></i>
                    <p class="text-green-800 font-bold">Localização capturada!</p>
                </div>
                <div class="grid grid-cols-2 gap-2 text-sm">
                    <div class="bg-white p-2 rounded">
                        <p class="text-xs text-gray-500">Latitude</p>
                        <p class="font-mono font-bold text-green-700">${currentGPS.lat.toFixed(6)}</p>
                    </div>
                    <div class="bg-white p-2 rounded">
                        <p class="text-xs text-gray-500">Longitude</p>
                        <p class="font-mono font-bold text-green-700">${currentGPS.lng.toFixed(6)}</p>
                    </div>
                </div>
                <p class="text-xs text-gray-600 mt-2 text-center">
                    <i class="fas fa-crosshairs mr-1"></i>Precisão: ${currentGPS.accuracy.toFixed(0)}m
                </p>
            `;
            
            getGpsBtn.disabled = false;
            getGpsBtn.innerHTML = '<i class="fas fa-redo mr-2"></i>Capturar Novamente';
            showToast('✅ Localização capturada com sucesso!');
        },
        (error) => {
            gpsDisplay.className = 'p-4 bg-red-50 border-2 border-red-500 rounded-lg';
            gpsDisplay.innerHTML = `
                <div class="flex items-center justify-center">
                    <i class="fas fa-exclamation-circle text-red-600 text-2xl mr-2"></i>
                    <p class="text-red-800 font-bold">Erro ao capturar</p>
                </div>
                <p class="text-sm text-red-700 mt-2 text-center">${error.message}</p>
            `;
            getGpsBtn.disabled = false;
            getGpsBtn.innerHTML = '<i class="fas fa-redo mr-2"></i>Tentar Novamente';
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
        getGpsBtn.scrollIntoView({ behavior: 'smooth', block: 'center' });
        getGpsBtn.classList.add('ring-4', 'ring-red-500');
        setTimeout(() => getGpsBtn.classList.remove('ring-4', 'ring-red-500'), 2000);
        return;
    }
    
    // Salvar localmente
    pendingSubmissions.push(submission);
    savePendingSubmissions();
    
    // Limpar formulário
    carForm.reset();
    currentGPS = null;
    gpsDisplay.className = 'p-4 bg-gray-50 border-2 border-dashed border-gray-300 rounded-lg text-gray-500 text-center';
    gpsDisplay.innerHTML = `
        <i class="fas fa-map-marker-alt text-2xl mb-2"></i>
        <p class="text-sm">Clique no botão acima para capturar</p>
    `;
    photoPreview.innerHTML = '';
    
    // Feedback visual de sucesso
    submitBtn.classList.add('pulse-success');
    setTimeout(() => submitBtn.classList.remove('pulse-success'), 600);
    
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

// Atualizar progresso de sincronização
function updateSyncProgress(current, total, statusText) {
    const percentage = Math.round((current / total) * 100);
    syncBar.style.width = `${percentage}%`;
    syncPercentage.textContent = `${percentage}%`;
    syncStatusText.textContent = statusText || `Sincronizando ${current}/${total}...`;
    syncStatus.classList.remove('hidden');
}

// Sincronizar com backend
async function syncSubmissions() {
    const unsynced = pendingSubmissions.filter(s => !s.synced);
    
    if (unsynced.length === 0) {
        showToast('✅ Todos os cadastros já estão sincronizados');
        return;
    }
    
    showToast(`🔄 Iniciando sincronização de ${unsynced.length} cadastros...`);
    
    let successCount = 0;
    
    for (let i = 0; i < unsynced.length; i++) {
        const submission = unsynced[i];
        updateSyncProgress(i + 1, unsynced.length, `Enviando ${submission.farmer_id}...`);
        
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
                successCount++;
            } else {
                throw new Error(`HTTP ${response.status}`);
            }
        } catch (error) {
            console.error('Erro ao sincronizar:', error);
        }
    }
    
    savePendingSubmissions();
    
    if (successCount === unsynced.length) {
        updateSyncProgress(unsynced.length, unsynced.length, 'Concluído!');
        showToast(`✅ ${successCount} cadastro(s) sincronizado(s) com sucesso!`);
        setTimeout(() => syncStatus.classList.add('hidden'), 2000);
    } else {
        showToast(`⚠️ ${successCount} de ${unsynced.length} sincronizados. Tente novamente.`);
        setTimeout(() => syncStatus.classList.add('hidden'), 3000);
    }
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
            .then(() => console.log('✅ Service Worker registrado'))
            .catch(err => console.log('❌ Erro ao registrar Service Worker:', err));
    }
}