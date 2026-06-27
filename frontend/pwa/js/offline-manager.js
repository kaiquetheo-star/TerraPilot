/**
 * IndexedDB + fila de sincronização offline.
 */
const TerraPilotDB = (() => {
  const DB_NAME = 'terrapilot';
  const DB_VERSION = 1;

  let db = null;

  function open() {
    if (db) return Promise.resolve(db);
    return new Promise((resolve, reject) => {
      const req = indexedDB.open(DB_NAME, DB_VERSION);
      req.onupgradeneeded = (e) => {
        const database = e.target.result;
        if (!database.objectStoreNames.contains('producer')) {
          database.createObjectStore('producer', { keyPath: 'id' });
        }
        if (!database.objectStoreNames.contains('notifications')) {
          const ns = database.createObjectStore('notifications', { keyPath: 'id', autoIncrement: true });
          ns.createIndex('resolved', 'resolved', { unique: false });
        }
        if (!database.objectStoreNames.contains('progress')) {
          database.createObjectStore('progress', { keyPath: 'property_id' });
        }
        if (!database.objectStoreNames.contains('sync_queue')) {
          database.createObjectStore('sync_queue', { keyPath: 'id', autoIncrement: true });
        }
      };
      req.onsuccess = () => { db = req.result; resolve(db); };
      req.onerror = () => reject(req.error);
    });
  }

  async function tx(store, mode) {
    const database = await open();
    return database.transaction(store, mode).objectStore(store);
  }

  async function getProducer() {
    const store = await tx('producer', 'readonly');
    return new Promise((res, rej) => {
      const r = store.get('default');
      r.onsuccess = () => res(r.result || null);
      r.onerror = () => rej(r.error);
    });
  }

  async function saveProducer(data) {
    const store = await tx('producer', 'readwrite');
    return new Promise((res, rej) => {
      const r = store.put({ ...data, id: 'default' });
      r.onsuccess = () => res(r.result);
      r.onerror = () => rej(r.error);
    });
  }

  async function addNotification(item) {
    const store = await tx('notifications', 'readwrite');
    return new Promise((res, rej) => {
      const r = store.add({ ...item, created_at: new Date().toISOString(), resolved: false });
      r.onsuccess = () => res(r.result);
      r.onerror = () => rej(r.error);
    });
  }

  async function listNotifications() {
    const store = await tx('notifications', 'readonly');
    return new Promise((res, rej) => {
      const r = store.getAll();
      r.onsuccess = () => res(r.result || []);
      r.onerror = () => rej(r.error);
    });
  }

  async function resolveNotification(id) {
    const store = await tx('notifications', 'readwrite');
    return new Promise((res, rej) => {
      const get = store.get(id);
      get.onsuccess = () => {
        const item = get.result;
        if (!item) { res(false); return; }
        item.resolved = true;
        item.resolved_at = new Date().toISOString();
        const put = store.put(item);
        put.onsuccess = () => res(true);
        put.onerror = () => rej(put.error);
      };
      get.onerror = () => rej(get.error);
    });
  }

  async function getProgress(propertyId) {
    const store = await tx('progress', 'readonly');
    return new Promise((res, rej) => {
      const r = store.get(propertyId);
      r.onsuccess = () => res(r.result || null);
      r.onerror = () => rej(r.error);
    });
  }

  async function saveProgress(propertyId, data) {
    const store = await tx('progress', 'readwrite');
    return new Promise((res, rej) => {
      const r = store.put({ property_id: propertyId, ...data, updated_at: new Date().toISOString() });
      r.onsuccess = () => res(true);
      r.onerror = () => rej(r.error);
    });
  }

  async function enqueueSync(action, payload) {
    const store = await tx('sync_queue', 'readwrite');
    return new Promise((res, rej) => {
      const r = store.add({ action, payload, created_at: new Date().toISOString() });
      r.onsuccess = () => res(r.result);
      r.onerror = () => rej(r.error);
    });
  }

  async function flushSyncQueue() {
    if (!navigator.onLine) return 0;
    const store = await tx('sync_queue', 'readwrite');
    const all = await new Promise((res, rej) => {
      const r = store.getAll();
      r.onsuccess = () => res(r.result || []);
      r.onerror = () => rej(r.error);
    });
    let flushed = 0;
    for (const item of all) {
      try {
        if (item.action === 'translate') {
          await TerraPilotAPI.translateNotification(item.payload.text);
        }
        store.delete(item.id);
        flushed++;
      } catch { /* retry later */ }
    }
    return flushed;
  }

  return {
    open,
    getProducer,
    saveProducer,
    addNotification,
    listNotifications,
    resolveNotification,
    getProgress,
    saveProgress,
    enqueueSync,
    flushSyncQueue,
  };
})();
