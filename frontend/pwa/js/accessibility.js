/**
 * Acessibilidade: fonte grande, alto contraste, TTS offline, teclado.
 */
const TerraPilotA11y = (() => {
  const STORAGE_KEY = 'terrapilot_a11y';
  const AUDIO_BTN_LABEL = '🔊 Ouvir explicação';

  function loadPrefs() {
    try {
      return JSON.parse(localStorage.getItem(STORAGE_KEY) || '{}');
    } catch {
      return {};
    }
  }

  function savePrefs(prefs) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(prefs));
  }

  function apply(prefs = loadPrefs()) {
    const html = document.documentElement;
    html.classList.remove('font-large', 'font-xlarge', 'high-contrast', 'reduce-motion');
    if (prefs.fontSize === 'large') html.classList.add('font-large');
    if (prefs.fontSize === 'xlarge') html.classList.add('font-xlarge');
    if (prefs.highContrast) html.classList.add('high-contrast');
    if (prefs.reduceMotion) html.classList.add('reduce-motion');
  }

  function toggleFont() {
    const prefs = loadPrefs();
    const cycle = { normal: 'large', large: 'xlarge', xlarge: 'normal' };
    prefs.fontSize = cycle[prefs.fontSize || 'normal'];
    savePrefs(prefs);
    apply(prefs);
    announce(`Fonte: ${prefs.fontSize === 'normal' ? 'normal' : prefs.fontSize}`);
  }

  function toggleContrast() {
    const prefs = loadPrefs();
    prefs.highContrast = !prefs.highContrast;
    savePrefs(prefs);
    apply(prefs);
    announce(prefs.highContrast ? 'Alto contraste ligado' : 'Alto contraste desligado');
  }

  function pickBrazilianVoice() {
    if (!('speechSynthesis' in window)) return null;
    const voices = window.speechSynthesis.getVoices();
    return voices.find((v) => v.lang.includes('pt-BR'))
      || voices.find((v) => v.lang.startsWith('pt'))
      || voices[0]
      || null;
  }

  function preloadVoices() {
    if ('speechSynthesis' in window) {
      window.speechSynthesis.getVoices();
    }
  }

  function falarTexto(texto, btn) {
    const text = (texto || '').trim();
    if (!text) {
      TerraPilotApp.showToast('Nada para ler em voz alta.');
      return;
    }
    if (!('speechSynthesis' in window)) {
      alert('Seu navegador não suporta áudio. Leia o texto abaixo.');
      return;
    }

    window.speechSynthesis.cancel();

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = 'pt-BR';
    utterance.rate = 0.9;
    utterance.pitch = 1;

    const vozBR = pickBrazilianVoice();
    if (vozBR) utterance.voice = vozBR;

    let btnReset = null;
    if (btn) {
      const defaultLabel = btn.dataset.defaultLabel || btn.textContent.trim() || AUDIO_BTN_LABEL;
      btn.dataset.defaultLabel = defaultLabel;
      btn.textContent = '🔊 Tocando...';
      btn.disabled = true;
      btnReset = () => {
        btn.textContent = defaultLabel;
        btn.disabled = false;
      };
      utterance.onend = btnReset;
      utterance.onerror = btnReset;
      setTimeout(btnReset, Math.max(4000, text.length * 90));
    }

    const start = () => {
      const voice = pickBrazilianVoice();
      if (voice) utterance.voice = voice;
      window.speechSynthesis.speak(utterance);
    };

    if (window.speechSynthesis.getVoices().length === 0) {
      window.speechSynthesis.onvoiceschanged = () => {
        window.speechSynthesis.onvoiceschanged = null;
        start();
      };
      preloadVoices();
    } else {
      start();
    }
  }

  function speak(text, lang = 'pt-BR') {
    falarTexto(text);
  }

  async function speakFromFile(scriptPath, fallbackText) {
    const path = scriptPath.startsWith('./') ? scriptPath : `./${scriptPath.replace(/^\//, '')}`;
    try {
      let text = '';
      if ('caches' in window) {
        const cached = await caches.match(path) || await caches.match(new URL(path, location.href).href);
        if (cached) text = (await cached.text()).trim();
      }
      if (!text) {
        const res = await fetch(path);
        if (!res.ok) throw new Error('script not found');
        text = (await res.text()).trim();
      }
      if (!text) throw new Error('empty script');
      falarTexto(text);
    } catch {
      if (fallbackText) {
        falarTexto(fallbackText);
        return;
      }
      TerraPilotApp.showToast('Não deu para carregar o áudio. Leia a resposta acima.');
    }
  }

  function resolveAudioText(btn) {
    return btn.dataset.texto
      || btn.getAttribute('data-speak')
      || btn.closest('.faq-item')?.querySelector('.faq-answer')?.textContent
      || '';
  }

  function handleAudioClick(btn) {
    const text = resolveAudioText(btn);
    if (text) {
      falarTexto(text, btn);
      return;
    }
    const file = btn.getAttribute('data-speak-file');
    if (file) {
      speakFromFile(file, resolveAudioText(btn));
    }
  }

  function announce(msg) {
    let live = document.getElementById('a11y-live');
    if (!live) {
      live = document.createElement('div');
      live.id = 'a11y-live';
      live.setAttribute('role', 'status');
      live.setAttribute('aria-live', 'polite');
      live.className = 'sr-only';
      live.style.cssText = 'position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0,0,0,0);';
      document.body.appendChild(live);
    }
    live.textContent = msg;
  }

  function bindToolbar() {
    document.getElementById('btn-font-size')?.addEventListener('click', toggleFont);
    document.getElementById('btn-contrast')?.addEventListener('click', toggleContrast);
  }

  function init() {
    apply();
    bindToolbar();
    preloadVoices();
    if ('speechSynthesis' in window) {
      window.speechSynthesis.onvoiceschanged = preloadVoices;
    }
    document.addEventListener('click', (e) => {
      const btn = e.target.closest('.btn-audio, .btn--audio, [data-speak], [data-speak-file]');
      if (!btn) return;
      handleAudioClick(btn);
    });
  }

  return {
    init,
    speak,
    falarTexto,
    speakFromFile,
    toggleFont,
    toggleContrast,
    announce,
  };
})();
