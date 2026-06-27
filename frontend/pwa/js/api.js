/**
 * Cliente API TerraPilot — online com fallback offline local.
 * Em GitHub Pages usa MockAPI (sem backend FastAPI).
 */
const TerraPilotAPI = (() => {
  const isGitHubPages = window.location.hostname.includes('github.io');
  const API_BASE = localStorage.getItem('terrapilot_api') || 'http://localhost:8001';

  function useMock() {
    return isGitHubPages && window.MockAPI;
  }

  async function request(path, options = {}) {
    const url = `${API_BASE}${path}`;
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 5000);
    try {
      const res = await fetch(url, { ...options, signal: controller.signal });
      clearTimeout(timeout);
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || `HTTP ${res.status}`);
      }
      return await res.json();
    } catch (e) {
      clearTimeout(timeout);
      throw e;
    }
  }

  async function validateAPP(riverWidthM) {
    if (useMock()) {
      return window.MockAPI.calculateAppWidth(Number(riverWidthM));
    }
    try {
      return await request('/api/rules/app', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ river_width_m: Number(riverWidthM) }),
      });
    } catch {
      return validateAPPOffline(riverWidthM);
    }
  }

  async function validateRL(propertyAreaHa, declaredRlHa, rlPercentLegal, biome = '') {
    try {
      return await request('/api/rules/rl', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          property_area_ha: Number(propertyAreaHa),
          declared_rl_ha: Number(declaredRlHa),
          rl_percent_legal: Number(rlPercentLegal),
          biome,
        }),
      });
    } catch {
      return null;
    }
  }

  async function validateAPPOffline(riverWidthM) {
    const w = Number(riverWidthM);
    if (!w || w <= 0) throw new Error('Largura do rio inválida');
    const brackets = [
      [10, 30, 'a'],
      [50, 50, 'b'],
      [200, 100, 'c'],
      [600, 200, 'd'],
    ];
    let minWidth = 500;
    let alinea = 'e';
    for (const [upper, width, al] of brackets) {
      if (w <= upper) {
        minWidth = width;
        alinea = al;
        break;
      }
    }
    const legalRef = `Art. 4º, I, '${alinea}' da Lei 12.651/2012`;
    return {
      min_width_m: minWidth,
      legal_ref: legalRef,
      human_explanation: `Seu rio tem cerca de ${w} metros. Pela lei, deixe pelo menos ${minWidth} metros livres de cada lado.`,
      fix_steps: [
        'Abra o SICAR Offline e localize o rio.',
        'Clique em Desenhar na área de APP.',
        `Marque ${minWidth} metros de cada lado da beira da água.`,
        'Salve e sincronize quando tiver internet.',
      ],
      issue_code: 'APP_RIVER_WIDTH',
    };
  }

  async function translateNotification(technicalText) {
    if (useMock()) {
      const r = await window.MockAPI.translateNotification(technicalText);
      return {
        simple_text: r.human_explanation,
        issue_code: r.issue_code === 'UNKNOWN' ? null : r.issue_code,
        original_text: technicalText,
        legal_ref: r.legal_ref || null,
        fix_step_count: r.fix_steps?.length || null,
      };
    }
    try {
      return await request('/api/translate/notification', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ technical_text: technicalText }),
      });
    } catch {
      return translateOffline(technicalText);
    }
  }

  async function translateOffline(text) {
    const dict = await loadJSON('data/dictionary.json');
    let simple = text;
    for (const [term, plain] of Object.entries(dict.glossary || {})) {
      simple = simple.replace(new RegExp(term, 'gi'), plain);
    }
    for (const p of dict.patterns || []) {
      const re = new RegExp(p.regex);
      const m = text.match(re);
      if (m) {
        let tpl = p.template;
        if (p.extract?.area_ha && m[p.extract.area_ha.group]) {
          const ha = parseFloat(m[p.extract.area_ha.group].replace(',', '.'));
          tpl = tpl.replace('{area_ha}', Math.round(ha));
        }
        tpl = tpl.replace('{steps}', p.defaults?.steps || 3);
        return {
          simple_text: tpl,
          issue_code: p.issue_code,
          original_text: text,
          pattern_id: p.id,
          fix_step_count: p.defaults?.steps || 3,
        };
      }
    }
    return {
      simple_text: 'Recebemos sua notificação. Vamos analisar juntos — procure um técnico se tiver dúvida.',
      issue_code: null,
      original_text: text,
      pattern_id: null,
      fix_step_count: null,
    };
  }

  async function getGuide(issueCode, params = {}) {
    if (useMock()) {
      const g = await window.MockAPI.getRetificationGuide(issueCode, params.area_ha || 2);
      return {
        title: g.title,
        benefit: g.legal_explanation || '',
        steps: (g.steps || []).map((s) => ({
          step_number: s.step,
          instruction: s.description,
          illustration: s.illustration,
        })),
      };
    }
    const qs = new URLSearchParams(params).toString();
    try {
      return await request(`/api/guide/${issueCode}${qs ? '?' + qs : ''}`);
    } catch {
      const guides = await loadJSON('data/guides.json');
      const g = guides[issueCode];
      if (!g) throw new Error('Guia não encontrado');
      return g;
    }
  }

  async function prefillSuggest(municipality, lat, lon, radiusKm = 2) {
    if (useMock()) {
      const mock = window.PREFILL_MOCK || { suggestions: [], mode: 'offline' };
      return {
        human_message: 'Sugestões de demonstração (modo GitHub Pages).',
        suggestions: (mock.suggestions || []).map((s) => ({
          label: s.type === 'APP' ? 'Área de Preservação' : s.type === 'RL' ? 'Reserva Legal' : s.type,
          type: s.type,
          area_ha: s.area_ha,
          source: s.source,
          note: s.note,
          distance_km: 0.5,
        })),
      };
    }
    return await request('/api/prefill/suggest', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        municipality,
        latitude: lat,
        longitude: lon,
        radius_km: radiusKm,
      }),
    });
  }

  async function getProgress(propertyId) {
    if (useMock()) {
      const p = await window.MockAPI.getProgress(propertyId);
      const total = p.total_issues || 1;
      const resolved = p.resolved_issues || 0;
      return {
        progress: {
          resolved_count: resolved,
          total_count: total,
          percent: Math.round((resolved / total) * 100),
          bar_message: `${resolved} de ${total} etapas resolvidas`,
        },
        history: p.completed_issues || [],
      };
    }
    try {
      return await request(`/api/progress/${propertyId}`);
    } catch {
      const local = await TerraPilotDB.getProgress(propertyId);
      return local || { progress: { resolved_count: 0, total_count: 0, percent: 0, bar_message: 'Sem dados ainda.' }, history: [] };
    }
  }

  async function getFAQ(profile = {}) {
    if (useMock()) {
      return window.MockAPI.getContextualFaq({
        property_size_ha: Number(profile.property_size_ha) || 50,
        biome: profile.biome || 'Cerrado',
      });
    }
    const qs = new URLSearchParams(profile).toString();
    try {
      return await request(`/api/knowledge/faq${qs ? '?' + qs : ''}`);
    } catch {
      const faq = await loadJSON('data/faq-contextual.json');
      return { entries: faq.entries.slice(0, 10), profile_summary: 'Perfil geral' };
    }
  }

  async function getCapabilityMatrix() {
    try {
      return await request('/api/capability/matrix');
    } catch {
      return loadJSON('data/capability.json');
    }
  }

  async function getRegionalProgress(municipalityCode, biome = '') {
    const qs = new URLSearchParams({ municipality_code: municipalityCode, biome }).toString();
    return await request(`/api/network/regional-progress?${qs}`);
  }

  async function getLeaderTemplate(leaderType) {
    try {
      return await request(`/api/network/leader-template/${leaderType}`);
    } catch {
      const data = await loadJSON('data/leader-templates.json');
      return data[leaderType] || data.union;
    }
  }

  async function guideFirstDeclaration(profile = {}) {
    try {
      return await request('/api/declare/first-time', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(profile),
      });
    } catch {
      return guideFirstDeclarationOffline(profile);
    }
  }

  async function validateConsolidated(payload) {
    try {
      return await request('/api/rules/consolidated', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
    } catch {
      return null;
    }
  }

  async function checkPraEligibility(propertyData = {}) {
    try {
      return await request('/api/benefits/pra', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(propertyData),
      });
    } catch {
      return loadJSON('data/pra-eligibility.json');
    }
  }

  async function getCollectiveImpact(propertyId) {
    try {
      return await request(`/api/collective/impact/${encodeURIComponent(propertyId)}`);
    } catch {
      const data = await loadJSON('data/collective-impact.json');
      return { ...data, property_id: propertyId };
    }
  }

  async function sendWhatsApp(phone, message) {
    if (useMock()) {
      return window.MockAPI.sendWhatsApp(phone, message);
    }
    return await request('/api/channels/whatsapp/send', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ phone, message }),
    });
  }

  function guideFirstDeclarationOffline(profile) {
    return {
      title: 'Primeira declaração do CAR',
      profile_summary: `Guia para ${profile.name || 'produtor'}`,
      human_message: 'Siga os passos na ordem. Confirme cada área no SICAR.',
      requires_confirmation: true,
      steps: [
        { step_number: 1, title: 'O que é o CAR?', legal_ref: 'Lei 12.651/2012', instruction: 'Cadastro ambiental da sua propriedade.', visual: 'assets/illustrations/app-river.svg' },
        { step_number: 2, title: 'O que é APP?', legal_ref: 'Art. 3º, II', instruction: 'Área de proteção perto de rios.', visual: 'assets/illustrations/app-river.svg' },
        { step_number: 3, title: 'O que é Reserva Legal?', legal_ref: 'Art. 3º, III', instruction: 'Parte da terra com vegetação nativa.', visual: 'assets/illustrations/rl-forest.svg' },
      ],
      pre_identified_features: [],
    };
  }

  async function loadJSON(path) {
    const res = await fetch(terrapilotUrl(path));
    if (!res.ok) throw new Error(`Falha ao carregar ${path}`);
    return res.json();
  }

  return {
    API_BASE,
    isGitHubPages,
    validateAPP,
    validateRL,
    translateNotification,
    getGuide,
    prefillSuggest,
    getProgress,
    getFAQ,
    getCapabilityMatrix,
    getRegionalProgress,
    getLeaderTemplate,
    guideFirstDeclaration,
    validateConsolidated,
    checkPraEligibility,
    getCollectiveImpact,
    sendWhatsApp,
    loadJSON,
  };
})();
