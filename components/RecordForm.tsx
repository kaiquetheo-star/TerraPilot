"use client";

import { Camera, Check, Loader2, MapPin, Save } from "lucide-react";
import { FormEvent, useState } from "react";
import { GeoPoint, savePendingRecord } from "@/lib/offlineRecords";

type RecordFormProps = {
  isOnline: boolean;
  onSaved: () => void;
};

function fileToDataUrl(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(String(reader.result));
    reader.onerror = reject;
    reader.readAsDataURL(file);
  });
}

export function RecordForm({ isOnline, onSaved }: RecordFormProps) {
  const [propertyName, setPropertyName] = useState("");
  const [observation, setObservation] = useState("");
  const [location, setLocation] = useState<GeoPoint | null>(null);
  const [photo, setPhoto] = useState<File | null>(null);
  const [isLocating, setIsLocating] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [message, setMessage] = useState("");

  const captureLocation = () => {
    if (!navigator.geolocation) {
      setMessage("GPS indisponivel neste aparelho.");
      return;
    }

    setIsLocating(true);
    setMessage("");

    navigator.geolocation.getCurrentPosition(
      (position) => {
        setLocation({
          latitude: position.coords.latitude,
          longitude: position.coords.longitude,
          accuracy: position.coords.accuracy
        });
        setIsLocating(false);
      },
      () => {
        setMessage("Nao foi possivel capturar a localizacao.");
        setIsLocating(false);
      },
      {
        enableHighAccuracy: true,
        timeout: 12000,
        maximumAge: 30000
      }
    );
  };

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    if (!propertyName.trim()) {
      setMessage("Informe o nome da propriedade.");
      return;
    }

    setIsSaving(true);
    setMessage("");

    try {
      const photoDataUrl = photo ? await fileToDataUrl(photo) : null;

      savePendingRecord({
        id: crypto.randomUUID(),
        propertyName: propertyName.trim(),
        observation: observation.trim(),
        location,
        photoName: photo?.name ?? null,
        photoDataUrl,
        createdAt: new Date().toISOString()
      });

      setPropertyName("");
      setObservation("");
      setLocation(null);
      setPhoto(null);
      setMessage(
        isOnline
          ? "Registro salvo. Use sincronizar para enviar ao backend."
          : "Registro salvo offline neste aparelho."
      );
      onSaved();
    } catch {
      setMessage("Falha ao salvar o registro localmente.");
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="rounded-[2rem] border border-soil-900/10 bg-white/90 p-5 shadow-sober backdrop-blur sm:p-7"
    >
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="text-sm font-bold uppercase tracking-[0.22em] text-soil-400">
            Nova submissao
          </p>
          <h2 className="mt-2 text-2xl font-black tracking-tight text-soil-900">
            Registrar Area/Documento
          </h2>
        </div>
        <span className="rounded-full bg-soil-100 px-3 py-1 text-xs font-bold uppercase tracking-widest text-soil-700">
          Local-first
        </span>
      </div>

      <div className="mt-6 space-y-5">
        <label className="block">
          <span className="text-sm font-bold text-soil-700">
            Nome da propriedade
          </span>
          <input
            value={propertyName}
            onChange={(event) => setPropertyName(event.target.value)}
            placeholder="Ex: Sitio Boa Esperanca"
            className="mt-2 w-full rounded-2xl border border-soil-900/10 bg-soil-50 px-4 py-4 text-lg font-semibold outline-none transition focus:border-leaf-600 focus:ring-4 focus:ring-leaf-400/20"
          />
        </label>

        <label className="block">
          <span className="text-sm font-bold text-soil-700">Observacao</span>
          <textarea
            value={observation}
            onChange={(event) => setObservation(event.target.value)}
            placeholder="Solo, agua, documento, ocorrencia..."
            rows={4}
            className="mt-2 w-full resize-none rounded-2xl border border-soil-900/10 bg-soil-50 px-4 py-4 text-base outline-none transition focus:border-leaf-600 focus:ring-4 focus:ring-leaf-400/20"
          />
        </label>

        <div className="grid gap-3 sm:grid-cols-2">
          <button
            type="button"
            onClick={captureLocation}
            disabled={isLocating}
            className="flex min-h-16 items-center justify-center gap-3 rounded-2xl bg-soil-900 px-5 py-4 text-base font-black text-white transition active:scale-[0.99] disabled:cursor-not-allowed disabled:opacity-60"
          >
            {isLocating ? <Loader2 className="animate-spin" /> : <MapPin />}
            {location ? "GPS Capturado" : "Capturar GPS"}
          </button>

          <label className="flex min-h-16 cursor-pointer items-center justify-center gap-3 rounded-2xl border border-soil-900/10 bg-soil-100 px-5 py-4 text-base font-black text-soil-900 transition active:scale-[0.99]">
            <Camera />
            {photo ? "Foto Selecionada" : "Tirar Foto"}
            <input
              type="file"
              accept="image/*"
              capture="environment"
              onChange={(event) => setPhoto(event.target.files?.[0] ?? null)}
              className="sr-only"
            />
          </label>
        </div>

        {(location || photo) && (
          <div className="rounded-2xl bg-soil-50 p-4 text-sm font-semibold text-soil-700">
            {location && (
              <p>
                GPS: {location.latitude.toFixed(5)},{" "}
                {location.longitude.toFixed(5)}
              </p>
            )}
            {photo && <p>Foto: {photo.name}</p>}
          </div>
        )}
      </div>

      {message && (
        <p className="mt-5 rounded-2xl bg-leaf-400/10 px-4 py-3 text-sm font-bold text-leaf-800">
          {message}
        </p>
      )}

      <button
        type="submit"
        disabled={isSaving}
        className="mt-6 flex min-h-16 w-full items-center justify-center gap-3 rounded-2xl bg-leaf-600 px-6 py-4 text-lg font-black text-white shadow-lg shadow-leaf-800/20 transition active:scale-[0.99] disabled:cursor-not-allowed disabled:opacity-70"
      >
        {isSaving ? <Loader2 className="animate-spin" /> : <Save />}
        Salvar Registro
        {!isSaving && <Check size={20} />}
      </button>
    </form>
  );
}
