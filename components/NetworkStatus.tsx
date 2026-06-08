"use client";

import { Cloud, CloudOff } from "lucide-react";
import { useNetworkStatus } from "@/hooks/useNetworkStatus";

export function NetworkStatus() {
  const { isOnline, label } = useNetworkStatus();

  return (
    <section
      className={[
        "rounded-[2rem] border p-6 shadow-sober transition-colors duration-300 sm:p-8",
        isOnline
          ? "border-leaf-400/30 bg-leaf-800 text-white"
          : "border-red-900/20 bg-soil-900 text-white"
      ].join(" ")}
      aria-live="polite"
    >
      <div className="flex items-center justify-between gap-4">
        <div>
          <p className="text-sm font-bold uppercase tracking-[0.28em] text-white/60">
            Estado da rede
          </p>
          <h1 className="mt-3 text-4xl font-black tracking-tight sm:text-6xl">
            {isOnline ? "Conectado" : "Offline"}
          </h1>
        </div>

        <div
          className={[
            "flex h-16 w-16 items-center justify-center rounded-2xl border",
            isOnline
              ? "border-white/20 bg-white/10"
              : "border-red-200/20 bg-red-500/15"
          ].join(" ")}
        >
          {isOnline ? <Cloud size={34} /> : <CloudOff size={34} />}
        </div>
      </div>

      <p className="mt-5 max-w-xl text-base leading-7 text-white/75">
        {isOnline
          ? "Rede ativa. Registros pendentes podem ser sincronizados agora."
          : "Sem sinal. Continue coletando; os dados ficam guardados neste aparelho."}
      </p>

      <div className="mt-6 inline-flex items-center gap-2 rounded-full bg-white/10 px-4 py-2 text-sm font-bold">
        <span
          className={[
            "h-3 w-3 rounded-full",
            isOnline ? "bg-emerald-300" : "bg-red-400"
          ].join(" ")}
        />
        {label}
      </div>
    </section>
  );
}
