"use client";

import {
  AlertTriangle,
  CheckCircle2,
  ChevronRight,
  CircleUserRound,
  ClipboardCheck,
  Loader2,
  MapPin,
  RefreshCw,
  Send,
  Sprout,
  X,
  XCircle
} from "lucide-react";
import { useEffect, useMemo, useState } from "react";

type FlagStatus = "Aprovado" | "Revisão Manual" | "Inconsistente";

type Registro = {
  id: string;
  nome_propriedade: string;
  observacao: string;
  latitude: number | null;
  longitude: number | null;
  area_hectares: number | null;
  data_coleta: string;
  confidence_score: number;
  flag_status: FlagStatus;
  criado_em: string;
  justificativa_ia?: string | null;
};

const API_URL = "http://localhost:8000/api/registros";

const statusStyles: Record<
  FlagStatus,
  {
    icon: typeof CheckCircle2;
    badge: string;
    dot: string;
    label: string;
  }
> = {
  Aprovado: {
    icon: CheckCircle2,
    badge: "border-emerald-400/20 bg-emerald-400/10 text-emerald-300",
    dot: "bg-emerald-300",
    label: "Aprovado"
  },
  "Revisão Manual": {
    icon: AlertTriangle,
    badge: "border-amber-400/20 bg-amber-400/10 text-amber-300",
    dot: "bg-amber-300",
    label: "Revisão Manual"
  },
  Inconsistente: {
    icon: XCircle,
    badge: "border-red-400/20 bg-red-400/10 text-red-300",
    dot: "bg-red-300",
    label: "Inconsistente"
  }
};

function formatHectares(value: number | null) {
  if (value === null || Number.isNaN(value)) return "Nao informado";
  return `${new Intl.NumberFormat("pt-BR", {
    maximumFractionDigits: 2
  }).format(value)} ha`;
}

function formatDate(value: string) {
  return new Intl.DateTimeFormat("pt-BR", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit"
  }).format(new Date(value));
}

function StatusBadge({ status }: { status: FlagStatus }) {
  const style = statusStyles[status];
  const Icon = style.icon;

  return (
    <span
      className={`inline-flex items-center gap-2 rounded-full border px-3 py-1.5 text-xs font-semibold ${style.badge}`}
    >
      <Icon size={14} />
      {style.label}
    </span>
  );
}

function DetailItem({
  label,
  value
}: {
  label: string;
  value: string | number | null | undefined;
}) {
  return (
    <div className="rounded-2xl border border-white/8 bg-white/[0.03] p-4">
      <p className="text-xs font-semibold uppercase tracking-[0.18em] text-zinc-500">
        {label}
      </p>
      <p className="mt-2 break-words text-sm font-medium text-zinc-100">
        {value ?? "Nao informado"}
      </p>
    </div>
  );
}

export default function DashboardPage() {
  const [registros, setRegistros] = useState<Registro[]>([]);
  const [selected, setSelected] = useState<Registro | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");

  const fetchRegistros = async () => {
    setIsLoading(true);
    setError("");

    try {
      const response = await fetch(API_URL, { cache: "no-store" });
      if (!response.ok) {
        throw new Error("Falha ao carregar registros");
      }
      setRegistros(await response.json());
    } catch {
      setError("Nao foi possivel conectar na API local.");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchRegistros();
  }, []);

  const summary = useMemo(() => {
    return registros.reduce(
      (acc, registro) => {
        acc.total += 1;
        acc[registro.flag_status] += 1;
        return acc;
      },
      {
        total: 0,
        Aprovado: 0,
        "Revisão Manual": 0,
        Inconsistente: 0
      } as Record<FlagStatus | "total", number>
    );
  }, [registros]);

  return (
    <main className="min-h-screen bg-[#070807] text-zinc-100">
      <header className="sticky top-0 z-30 border-b border-white/8 bg-[#070807]/90 backdrop-blur-xl">
        <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-5 lg:px-8">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-white text-[#070807]">
              <Sprout size={22} />
            </div>
            <div>
              <p className="text-sm font-black tracking-tight">Raiz.CAR</p>
              <p className="text-xs font-medium text-zinc-500">
                Revisao ambiental
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3 rounded-full border border-white/10 bg-white/[0.03] px-3 py-2">
            <div className="hidden text-right sm:block">
              <p className="text-xs font-semibold text-zinc-200">
                Analista Ambiental
              </p>
              <p className="text-[11px] text-zinc-500">Mesa de validacao</p>
            </div>
            <CircleUserRound className="text-zinc-300" size={28} />
          </div>
        </div>
      </header>

      <section className="mx-auto max-w-7xl px-5 py-8 lg:px-8">
        <div className="grid gap-6 lg:grid-cols-[1.1fr_0.9fr] lg:items-end">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.26em] text-zinc-500">
              Dashboard
            </p>
            <h1 className="mt-3 text-4xl font-black tracking-[-0.04em] text-white sm:text-5xl">
              Registros para auditoria
            </h1>
            <p className="mt-4 max-w-2xl text-sm leading-6 text-zinc-400">
              Dados sincronizados pelo PWA de campo, priorizados por risco e
              necessidade de revisao humana.
            </p>
          </div>

          <button
            type="button"
            onClick={fetchRegistros}
            className="inline-flex h-12 items-center justify-center gap-2 rounded-full border border-white/10 bg-white px-5 text-sm font-bold text-[#070807] transition hover:bg-zinc-200"
          >
            <RefreshCw size={16} />
            Atualizar registros
          </button>
        </div>

        <div className="mt-8 grid gap-3 sm:grid-cols-4">
          <div className="rounded-3xl border border-white/8 bg-white/[0.03] p-5">
            <p className="text-xs font-semibold uppercase tracking-[0.18em] text-zinc-500">
              Total
            </p>
            <p className="mt-3 text-3xl font-black">{summary.total}</p>
          </div>
          {(["Revisão Manual", "Inconsistente", "Aprovado"] as FlagStatus[]).map(
            (status) => (
              <div
                key={status}
                className="rounded-3xl border border-white/8 bg-white/[0.03] p-5"
              >
                <div className="flex items-center gap-2">
                  <span
                    className={`h-2.5 w-2.5 rounded-full ${statusStyles[status].dot}`}
                  />
                  <p className="text-xs font-semibold uppercase tracking-[0.18em] text-zinc-500">
                    {status}
                  </p>
                </div>
                <p className="mt-3 text-3xl font-black">{summary[status]}</p>
              </div>
            )
          )}
        </div>

        <div className="mt-8 overflow-hidden rounded-[2rem] border border-white/8 bg-[#0c0d0c] shadow-2xl shadow-black/30">
          <div className="flex items-center justify-between border-b border-white/8 px-5 py-4">
            <div className="flex items-center gap-3">
              <ClipboardCheck className="text-zinc-400" size={20} />
              <h2 className="font-bold text-white">Fila de analise</h2>
            </div>
            {isLoading && (
              <span className="inline-flex items-center gap-2 text-sm font-medium text-zinc-500">
                <Loader2 className="animate-spin" size={16} />
                Carregando
              </span>
            )}
          </div>

          {error ? (
            <div className="p-8 text-sm font-medium text-red-300">{error}</div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full min-w-[820px] border-collapse text-left">
                <thead>
                  <tr className="border-b border-white/8 text-xs uppercase tracking-[0.18em] text-zinc-500">
                    <th className="px-5 py-4 font-semibold">ID</th>
                    <th className="px-5 py-4 font-semibold">Propriedade</th>
                    <th className="px-5 py-4 font-semibold">Hectares</th>
                    <th className="px-5 py-4 font-semibold">Status IA</th>
                    <th className="px-5 py-4 font-semibold">
                      Score de Confianca
                    </th>
                    <th className="px-5 py-4" />
                  </tr>
                </thead>
                <tbody>
                  {registros.map((registro) => (
                    <tr
                      key={registro.id}
                      onClick={() => setSelected(registro)}
                      className="cursor-pointer border-b border-white/6 transition hover:bg-white/[0.04]"
                    >
                      <td className="px-5 py-5 font-mono text-xs text-zinc-500">
                        {registro.id.slice(0, 10)}
                      </td>
                      <td className="px-5 py-5">
                        <p className="font-semibold text-zinc-100">
                          {registro.nome_propriedade}
                        </p>
                        <p className="mt-1 text-xs text-zinc-500">
                          {formatDate(registro.data_coleta)}
                        </p>
                      </td>
                      <td className="px-5 py-5 text-sm font-medium text-zinc-300">
                        {formatHectares(registro.area_hectares)}
                      </td>
                      <td className="px-5 py-5">
                        <StatusBadge status={registro.flag_status} />
                      </td>
                      <td className="px-5 py-5">
                        <div className="flex items-center gap-3">
                          <div className="h-2 w-28 overflow-hidden rounded-full bg-white/10">
                            <div
                              className="h-full rounded-full bg-zinc-100"
                              style={{
                                width: `${registro.confidence_score}%`
                              }}
                            />
                          </div>
                          <span className="text-sm font-bold text-zinc-100">
                            {registro.confidence_score}%
                          </span>
                        </div>
                      </td>
                      <td className="px-5 py-5 text-right text-zinc-500">
                        <ChevronRight size={18} />
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>

              {!isLoading && registros.length === 0 && (
                <div className="p-8 text-center text-sm font-medium text-zinc-500">
                  Nenhum registro encontrado.
                </div>
              )}
            </div>
          )}
        </div>
      </section>

      {selected && (
        <div className="fixed inset-0 z-40">
          <button
            type="button"
            aria-label="Fechar detalhes"
            onClick={() => setSelected(null)}
            className="absolute inset-0 bg-black/70 backdrop-blur-sm"
          />

          <aside className="absolute right-0 top-0 flex h-full w-full max-w-xl flex-col border-l border-white/10 bg-[#0b0c0b] shadow-2xl shadow-black">
            <div className="flex items-center justify-between border-b border-white/8 p-5">
              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.22em] text-zinc-500">
                  Detalhes
                </p>
                <h2 className="mt-1 text-2xl font-black tracking-tight text-white">
                  {selected.nome_propriedade}
                </h2>
              </div>
              <button
                type="button"
                onClick={() => setSelected(null)}
                className="flex h-11 w-11 items-center justify-center rounded-full border border-white/10 text-zinc-300 transition hover:bg-white/5"
              >
                <X size={20} />
              </button>
            </div>

            <div className="flex-1 overflow-y-auto p-5">
              <div className="flex items-center justify-between rounded-3xl border border-white/8 bg-white/[0.03] p-4">
                <StatusBadge status={selected.flag_status} />
                <p className="text-3xl font-black text-white">
                  {selected.confidence_score}%
                </p>
              </div>

              <div className="mt-5 grid gap-3 sm:grid-cols-2">
                <DetailItem label="ID" value={selected.id} />
                <DetailItem
                  label="Area"
                  value={formatHectares(selected.area_hectares)}
                />
                <DetailItem label="Latitude" value={selected.latitude} />
                <DetailItem label="Longitude" value={selected.longitude} />
                <DetailItem
                  label="Data da coleta"
                  value={formatDate(selected.data_coleta)}
                />
                <DetailItem
                  label="Criado no backend"
                  value={formatDate(selected.criado_em)}
                />
              </div>

              <div className="mt-5 rounded-3xl border border-white/8 bg-white/[0.03] p-5">
                <div className="flex items-center gap-2 text-zinc-400">
                  <MapPin size={18} />
                  <p className="text-xs font-semibold uppercase tracking-[0.18em]">
                    Observacao do produtor
                  </p>
                </div>
                <p className="mt-4 whitespace-pre-wrap text-sm leading-6 text-zinc-200">
                  {selected.observacao || "Sem observacao informada."}
                </p>
              </div>

              <div className="mt-5 rounded-3xl border border-white/8 bg-white/[0.03] p-5">
                <p className="text-xs font-semibold uppercase tracking-[0.18em] text-zinc-500">
                  Justificativa da IA
                </p>
                <p className="mt-4 text-sm leading-6 text-zinc-200">
                  {selected.justificativa_ia ||
                    "A API atual retornou score e status, mas nao enviou uma justificativa textual."}
                </p>
              </div>
            </div>

            <div className="grid gap-3 border-t border-white/8 p-5 sm:grid-cols-2">
              <button
                type="button"
                className="inline-flex min-h-14 items-center justify-center gap-2 rounded-2xl bg-white px-5 py-4 text-sm font-black text-[#070807] transition hover:bg-zinc-200"
              >
                <CheckCircle2 size={18} />
                Confirmar Validacao
              </button>
              <button
                type="button"
                className="inline-flex min-h-14 items-center justify-center gap-2 rounded-2xl border border-white/10 bg-white/[0.04] px-5 py-4 text-sm font-black text-white transition hover:bg-white/[0.08]"
              >
                <Send size={18} />
                Solicitar Correcao
              </button>
            </div>
          </aside>
        </div>
      )}
    </main>
  );
}
