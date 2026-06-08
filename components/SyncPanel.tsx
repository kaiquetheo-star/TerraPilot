"use client";

import { CheckCircle2, Clock3, Loader2, RefreshCw } from "lucide-react";
import {
  FieldRecord,
  SyncedRecord,
  clearPendingRecords,
  saveSyncedRecords
} from "@/lib/offlineRecords";

type SyncPanelProps = {
  isOnline: boolean;
  pendingRecords: FieldRecord[];
  syncedRecords: SyncedRecord[];
  isSyncing: boolean;
  setIsSyncing: (value: boolean) => void;
  onSynced: () => void;
};

function formatDate(value: string) {
  return new Intl.DateTimeFormat("pt-BR", {
    day: "2-digit",
    month: "2-digit",
    hour: "2-digit",
    minute: "2-digit"
  }).format(new Date(value));
}

export function SyncPanel({
  isOnline,
  pendingRecords,
  syncedRecords,
  isSyncing,
  setIsSyncing,
  onSynced
}: SyncPanelProps) {
  const canSync = isOnline && pendingRecords.length > 0 && !isSyncing;

  const syncAll = async () => {
    if (!canSync) return;

    setIsSyncing(true);

    try {
      const response = await fetch("/api/sync", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ records: pendingRecords })
      });

      if (!response.ok) {
        throw new Error("Sync failed");
      }

      saveSyncedRecords(pendingRecords);
      clearPendingRecords();
      onSynced();
    } finally {
      setIsSyncing(false);
    }
  };

  return (
    <section className="rounded-[2rem] border border-soil-900/10 bg-white/85 p-5 shadow-sober sm:p-7">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <p className="text-sm font-bold uppercase tracking-[0.22em] text-soil-400">
            Sincronizacao
          </p>
          <h2 className="mt-2 text-2xl font-black tracking-tight text-soil-900">
            Registros Pendentes
          </h2>
        </div>

        <button
          type="button"
          onClick={syncAll}
          disabled={!canSync}
          className="flex min-h-14 items-center justify-center gap-3 rounded-2xl bg-soil-900 px-5 py-3 text-base font-black text-white transition active:scale-[0.99] disabled:cursor-not-allowed disabled:bg-soil-100 disabled:text-soil-400"
        >
          {isSyncing ? <Loader2 className="animate-spin" /> : <RefreshCw />}
          Sincronizar Todos
        </button>
      </div>

      <div className="mt-6 space-y-3">
        {pendingRecords.length === 0 ? (
          <div className="rounded-2xl border border-dashed border-soil-900/20 bg-soil-50 p-5 text-sm font-semibold text-soil-700">
            Nenhum registro pendente neste aparelho.
          </div>
        ) : (
          pendingRecords.map((record) => (
            <article
              key={record.id}
              className="rounded-2xl border border-amber-900/10 bg-amber-50 p-4"
            >
              <div className="flex items-start gap-3">
                <Clock3 className="mt-1 shrink-0 text-amber-700" size={20} />
                <div>
                  <h3 className="font-black text-soil-900">
                    {record.propertyName}
                  </h3>
                  <p className="mt-1 text-sm font-semibold text-soil-700">
                    Criado em {formatDate(record.createdAt)}
                    {record.location ? " com GPS" : ""}
                    {record.photoName ? " e foto" : ""}
                  </p>
                </div>
              </div>
            </article>
          ))
        )}
      </div>

      {syncedRecords.length > 0 && (
        <div className="mt-8">
          <h3 className="text-sm font-black uppercase tracking-[0.22em] text-leaf-800">
            Sincronizados
          </h3>
          <div className="mt-3 space-y-3">
            {syncedRecords.slice(0, 4).map((record) => (
              <article
                key={`${record.id}-${record.syncedAt}`}
                className="flex items-center gap-3 rounded-2xl bg-leaf-400/10 p-4"
              >
                <CheckCircle2 className="shrink-0 text-leaf-600" size={20} />
                <div>
                  <p className="font-black text-soil-900">
                    {record.propertyName}
                  </p>
                  <p className="text-sm font-semibold text-soil-700">
                    Enviado em {formatDate(record.syncedAt)}
                  </p>
                </div>
              </article>
            ))}
          </div>
        </div>
      )}
    </section>
  );
}
