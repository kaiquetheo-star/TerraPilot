export type GeoPoint = {
  latitude: number;
  longitude: number;
  accuracy?: number;
};

export type FieldRecord = {
  id: string;
  propertyName: string;
  observation: string;
  location: GeoPoint | null;
  photoName: string | null;
  photoDataUrl: string | null;
  createdAt: string;
};

export type SyncedRecord = FieldRecord & {
  syncedAt: string;
};

const PENDING_KEY = "raiz.car.pending.records";
const SYNCED_KEY = "raiz.car.synced.records";

function readJson<T>(key: string, fallback: T): T {
  if (typeof window === "undefined") return fallback;

  try {
    const raw = window.localStorage.getItem(key);
    return raw ? (JSON.parse(raw) as T) : fallback;
  } catch {
    return fallback;
  }
}

function writeJson<T>(key: string, value: T) {
  window.localStorage.setItem(key, JSON.stringify(value));
  window.dispatchEvent(new CustomEvent("raiz-car-storage"));
}

export function getPendingRecords() {
  return readJson<FieldRecord[]>(PENDING_KEY, []);
}

export function getSyncedRecords() {
  return readJson<SyncedRecord[]>(SYNCED_KEY, []);
}

export function savePendingRecord(record: FieldRecord) {
  writeJson(PENDING_KEY, [record, ...getPendingRecords()]);
}

export function clearPendingRecords() {
  writeJson(PENDING_KEY, []);
}

export function saveSyncedRecords(records: FieldRecord[]) {
  const synced = records.map((record) => ({
    ...record,
    syncedAt: new Date().toISOString()
  }));

  writeJson(SYNCED_KEY, [...synced, ...getSyncedRecords()]);
}
