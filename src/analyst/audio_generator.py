"""
Gerador de áudio para notificações explicativas.

Converte texto em arquivo .mp3 para envio via WhatsApp/SMS.
Usa gTTS (online, gratuito) com fallback para pyttsx3 (offline).
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path


_AUDIO_DIR = Path(__file__).resolve().parents[2] / "data" / "audio" / "notifications"


def text_to_speech(text: str, voice: str = "pt-BR") -> str:
    """
    Converte texto em áudio e retorna o path do arquivo .mp3.

    Args:
        text: Texto a ser convertido em fala.
        voice: Código de idioma (padrão pt-BR).

    Returns:
        Caminho absoluto do arquivo .mp3 gerado.
    """
    if not text.strip():
        raise ValueError("O texto para TTS não pode ser vazio.")

    _AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_%f")
    output_path = _AUDIO_DIR / f"{timestamp}.mp3"

    try:
        from gtts import gTTS

        tts = gTTS(text=text, lang=voice)
        tts.save(str(output_path))
        return str(output_path)
    except ImportError:
        pass

    try:
        import pyttsx3

        engine = pyttsx3.init()
        wav_path = output_path.with_suffix(".wav")
        engine.save_to_file(text, str(wav_path))
        engine.runAndWait()

        if wav_path.exists():
            return str(wav_path)
    except ImportError:
        pass

    raise RuntimeError(
        "Nenhum engine TTS disponível. Instale gTTS (pip install gTTS) "
        "ou pyttsx3 (pip install pyttsx3)."
    )
