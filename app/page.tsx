"use client";

import { Plus, Sprout } from "lucide-react";
import { useEffect, useState } from "react";
import { NetworkStatus } from "@/components/NetworkStatus";
import { RecordForm } from "@/components/RecordForm";
import { SyncPanel } from "@/components/SyncPanel";
import { useNetworkStatus } from "@/hooks/useNetworkStatus";
import {
  FieldRecord,
  SyncedRecord,
  getPendingRecords,
  getSyncedRecords
} from "@/lib/offlineRecords";

export default function Home() {
  const { isOnline } = useNetworkStatus();
  const [showForm, setShowForm] = useState(false);
  const [isSyncing, setIsSyncing] = useState(false);
  const [pendingRecords, setPendingRecords] = useState<FieldRecord[]>([]);
  const [syncedRecords, setSyncedRecords] = useState<SyncedRecord[]>([]);

  const refreshRecords = () => {
    setPendingRecords(getPendingRecords());
    setSyncedRecords(getSyncedRecords());
  };

  useEffect(() => {
    refreshRecords();
    window.addEventListener("storage", refreshRecords);
    window.addEventListener("raiz-car-storage", refreshRecords);

    return () => {
      window.removeEventListener("storage", refreshRecords);
      window.removeEventListener("raiz-car-storage", refreshRecords);
    };
  }, []);

  return (
    <main className="mx-auto flex min-h-screen w-full max-w-5xl flex-col gap-6 px-4 py-5 sm:px-6 lg:px-8">
      <header className="flex items-center justify-between py-2">
        <div className="flex items-center gap-3">
          <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-soil-900 text-white shadow-lg">
            <Sprout size={26} />
          </div>
          <div>
            <p className="text-xs font-black uppercase tracking-[0.32em] text-soil-400">
              Raiz.CAR
            </p>
            <p className="text-sm font-bold text-soil-700">
              Coleta ambiental offline
            </p>
          </div>
        </div>

        <div
          className={[
            "rounded-full px-4 py-2 text-sm font-black",
            isOnline
              ? "bg-leaf-400/15 text-leaf-800"
              : "bg-red-500/10 text-red-800"
          ].join(" ")}
        >
          {isOnline ? "Online" : "Offline"}
        </div>
      </header>

      <NetworkStatus />

      <section className="grid gap-4 rounded-[2rem] border border-soil-900/10 bg-soil-900 p-5 text-white shadow-sober sm:grid-cols-[1fr_auto] sm:items-center sm:p-7">
        <div>
          <p className="text-sm font-bold uppercase tracking-[0.22em] text-white/50">
            Acao central
          </p>
          <h2 className="mt-2 text-2xl font-black tracking-tight">
            Registrar area ou documento
          </h2>
          <p className="mt-2 max-w-xl text-sm font-semibold leading-6 text-white/65">
            Capture nome, observacao, GPS e foto mesmo sem sinal de internet.
          </p>
        </div>

        <button
          type="button"
          onClick={() => setShowForm((value) => !value)}
          className="flex min-h-16 items-center justify-center gap-3 rounded-2xl bg-white px-6 py-4 text-lg font-black text-soil-900 transition active:scale-[0.99]"
        >
          <Plus />
          {showForm ? "Fechar coleta" : "Registrar Area/Documento"}
        </button>
      </section>

      {showForm && <RecordForm isOnline={isOnline} onSaved={refreshRecords} />}

      <SyncPanel
        isOnline={isOnline}
        pendingRecords={pendingRecords}
        syncedRecords={syncedRecords}
        isSyncing={isSyncing}
        setIsSyncing={setIsSyncing}
        onSynced={refreshRecords}
      />
    </main>
  );
}
