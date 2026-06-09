// Estado
let currentGPS = null;
let pendingSubmissions = [];
let selectedPhotos = [];
let selectedVegetations = [];

// Elementos
const els = {
    statusBar: document.getElementById('status-bar'),
    form: document.getElementById('car-form'),
    gpsBtn: document.getElementById('get-gps-btn'),
    gpsDisplay: document.getElementById('gps-display'),
    pendingCount: document.getElementById('pending-count'),
    countNumber: document.getElementById('count-number'),
    syncBtn: document.getElementById('sync-btn'),
    toast: document.getElementById('toast'),
    syncStatus: document.getElementById('sync-status'),
    syncBar: document.getElementById('sync-bar'),
    syncPct: document.getElementById('sync-percentage'),
    syncText: document.getElementById('sync-status-text'),
    photoInput: document.getElementById('photos'),
    photoPreview: document.getElementById('photo-preview'),
    photoCount: document.getElementById('photo-count'),
    areaInput: document.getElementById('area-ha'),
    vegChips: document.querySelectorAll('.veg-chip')
};

// Inicialização
document.addEventListener('DOMContentLoaded', () => {
    loadPending();
    updateStatus();
    setupEvents();
});

function setupEvents() {
    window.addEventListener('online', updateStatus);
    window.addEventListener('offline', updateStatus);
    els.gpsBtn.addEventListener('click', captureGPS);
    els.form.addEventListener('submit', handleSubmit);
    els.syncBtn.addEventListener('click', syncData);
    els.photoInput.addEventListener('change', handlePhotos);
    els.areaInput.addEventListener('input', validateArea);
    els.areaInput.addEventListener('keydown', filterNumbers);
    els.vegChips.forEach(chip => chip.addEventListener('click', () => toggleVeg(chip)));
}

// Filtrar apenas números no campo área
function filterNumbers(e) {
    const allowed = ['Backspace','Delete','Tab','Escape','Enter','ArrowLeft','ArrowRight','ArrowUp','ArrowDown'];
    if (allowed.includes(e.key)) return;
    if ((e.ctrlKey || e.metaKey) && ['a','c','v','x'].includes(e.key.toLowerCase())) return;
    if (!/^[0-9.,]$/.test(e.key)) e.preventDefault();
    if ((e.key === '.' || e.key === ',') && els.areaInput.value.includes('.')) e.preventDefault();
}

function validateArea() {
    const val = els.areaInput.value.replace(',','.').replace(/[^0-9.]/g,'');
    els.areaInput.value = val;
}

// Chips de vegetação
function toggleVeg(chip) {
    const v = chip.dataset.value;
    const idx = selectedVegetations.indexOf(v);
    if (idx === -1) { selectedVegetations.push(v); chip.classList.add('selected'); }
    else { selectedVegetations.splice(idx,1); chip.classList.remove('selected'); }
    document.getElementById('vegetation-type').value = selectedVegetations.join(', ');
}

// Fotos
function handlePhotos(e) {
    selectedPhotos = selectedPhotos.concat(Array.from(e.target.files));
    renderPhotos();
    showToast(`📸 ${e.target.files.length} foto(s) adicionada(s)`);
}

function renderPhotos() {
    els.photoPreview.innerHTML = '';
    els.photoCount.textContent = `${selectedPhotos.length} foto${selectedPhotos.length!==1?'s':''}`;
    selectedPhotos.forEach((file, i) => {
        const reader = new FileReader();
        reader.onload = ev => {
            const div = document.createElement('div');
            div.className = 'photo-item';
            div.style.backgroundImage = `url(${ev.target.result})`;
            div.innerHTML = `<div class="photo-remove" onclick="removePhoto(${i})">✕</div>`;
            els.photoPreview.appendChild(div);
        };
        reader.readAsDataURL(file);
    });
}

function removePhoto(i) {
    selectedPhotos.splice(i,1);
    renderPhotos();
    showToast('🗑️ Foto removida');
}
window.removePhoto = removePhoto;

// Status online/offline
function updateStatus() {
    if (navigator.onLine) {
        els.statusBar.textContent = '🟢 ONLINE - Pronto para sincronizar';
        els.statusBar.className = 'status-bar status-online';
    } else {
        els.statusBar.textContent = '🔴 OFFLINE - Dados salvos localmente';
        els.statusBar.className = 'status-bar status-offline';
    }
}

// GPS
function captureGPS() {
    if (!navigator.geolocation) return showToast('❌ Geolocalização não suportada');
    els.gpsBtn.disabled = true;
    els.gpsBtn.textContent = '⏳ Capturando...';
    
    navigator.geolocation.getCurrentPosition(
        pos => {
            currentGPS = { lat: pos.coords.latitude, lng: pos.coords.longitude, acc: pos.coords.accuracy };
            document.getElementById('gps-lat').value = currentGPS.lat;
            document.getElementById('gps-lng').value = currentGPS.lng;
            els.gpsDisplay.className = 'gps-display gps-success';
            els.gpsDisplay.innerHTML = `
                <div style="font-weight:600; margin-bottom:8px;">✅ Localizado!</div>
                <div style="font-size:13px;">Lat: ${currentGPS.lat.toFixed(5)}<br>Lng: ${currentGPS.lng.toFixed(5)}</div>
            `;
            els.gpsBtn.disabled = false;
            els.gpsBtn.textContent = '🗺️ Capturar Novamente';
            showToast('✅ Localização capturada!');
        },
        err => {
            els.gpsDisplay.className = 'gps-display';
            els.gpsDisplay.innerHTML = `<div style="color:#f87171">❌ ${err.message}</div>`;
            els.gpsBtn.disabled = false;
            els.gpsBtn.textContent = '🗺️ Tentar Novamente';
            showToast('❌ Erro ao capturar GPS');
        },
        { enableHighAccuracy: true, timeout: 10000 }
    );
}

// Submit
async function handleSubmit(e) {
    e.preventDefault();
    
    const area = parseFloat(els.areaInput.value);
    if (isNaN(area) || area < 0.1) return showToast('❌ Área inválida (mín. 0.1 ha)');
    if (selectedVegetations.length === 0) return showToast('❌ Selecione ao menos 1 vegetação');
    if (!currentGPS) return showToast('❌ Capture o GPS antes de salvar');
    
    const sub = {
        id: Date.now().toString(),
        farmer_id: document.getElementById('farmer-id').value,
        area_ha: area,
        vegetation_types: selectedVegetations,
        gps_coords: [currentGPS.lat, currentGPS.lng],
        notes: document.getElementById('notes').value,
        photos_count: selectedPhotos.length,
        timestamp: new Date().toISOString(),
        synced: false
    };
    
    pendingSubmissions.push(sub);
    savePending();
    
    // Reset form
    els.form.reset();
    currentGPS = null;
    selectedPhotos = [];
    selectedVegetations = [];
    document.querySelectorAll('.veg-chip').forEach(c => c.classList.remove('selected'));
    els.gpsDisplay.className = 'gps-display';
    els.gpsDisplay.textContent = 'Clique acima para capturar';
    els.photoPreview.innerHTML = '';
    els.photoCount.textContent = '0 fotos';
    
    showToast(`✅ Salvo! ${sub.photos_count} foto(s)`);
    if (navigator.onLine) await syncData();
}

// Persistência
function savePending() {
    localStorage.setItem('terrapilot_submissions', JSON.stringify(pendingSubmissions));
    updatePending();
}
function loadPending() {
    const s = localStorage.getItem('terrapilot_submissions');
    if (s) { pendingSubmissions = JSON.parse(s); updatePending(); }
}
function updatePending() {
    const n = pendingSubmissions.filter(x => !x.synced).length;
    els.countNumber.textContent = n;
    els.pendingCount.classList.toggle('hidden', n === 0);
}

// Sync
async function syncData() {
    const unsynced = pendingSubmissions.filter(x => !x.synced);
    if (!unsynced.length) return showToast('✅ Tudo sincronizado');
    
    showToast(`🔄 Sincronizando ${unsynced.length}...`);
    let ok = 0;
    
    for (let i = 0; i < unsynced.length; i++) {
        const sub = unsynced[i];
        els.syncText.textContent = `Enviando ${sub.farmer_id}...`;
        els.syncPct.textContent = `${Math.round((i+1)/unsynced.length*100)}%`;
        els.syncBar.style.width = `${Math.round((i+1)/unsynced.length*100)}%`;
        els.syncStatus.classList.remove('hidden');
        
        try {
            const r = await fetch('http://localhost:8000/api/validate', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(sub)
            });
            if (r.ok) { sub.synced = true; ok++; }
        } catch(e) { console.error(e); }
    }
    
    savePending();
    els.syncStatus.classList.add('hidden');
    showToast(ok === unsynced.length ? `✅ ${ok} sincronizado(s)!` : `⚠️ ${ok}/${unsynced.length} sincronizados`);
}

// Toast
function showToast(msg) {
    els.toast.textContent = msg;
    els.toast.classList.remove('hidden');
    setTimeout(() => els.toast.classList.add('hidden'), 3000);
}