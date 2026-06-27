/**
 * TerraPilot PWA — app principal e handlers de views.
 */

// Verifica se está rodando em GitHub Pages (sem backend)
const isGitHubPages = window.location.hostname.includes('github.io');

const TerraPilotApp = (() => {
  let gpsCoords = null;
  let lastTranslation = null;

  const BENEFICIOS = {
    app_fixed: 'Facilita acesso a crédito rural e programas de incentivo',
    rl_fixed: 'Acelera a análise do seu CAR pelo órgão ambiental',
    consolidated_fixed: 'Garante seus direitos de área consolidada (Lei 12.651)',
    pra_adhesion: 'Suspende multas antigas e mantém acesso a crédito durante regularização',
  };

  const ISSUE_BENEFICIO_KEY = {
    APP_RIVER_WIDTH: 'app_fixed',
    APP_OVERLAP: 'app_fixed',
    RL_PERIMETER_DIVERGENCE: 'rl_fixed',
    RL_MISSING: 'rl_fixed',
    GEOMETRY_INVALID: 'consolidated_fixed',
    AREA_OUTSIDE_BOUNDARY: 'consolidated_fixed',
  };

  function getBeneficioMessage(issueCode) {
    const key = ISSUE_BENEFICIO_KEY[issueCode];
    return key ? BENEFICIOS[key] : 'Menos risco de multas e embargos';
  }

  function renderProgressBenefits() {
    return `
      <div class="benefit-card">✅ APP corrigida → Facilita acesso a crédito rural e linhas especiais</div>
      <div class="benefit-card">✅ RL ajustada → Acelera a análise do seu CAR pelo órgão ambiental</div>
      <div class="benefit-card">✅ Pendências resolvidas → Menos risco de multas e embargos</div>`;
  }

  function showToast(msg) {
    const t = document.getElementById('toast');
    t.textContent = msg;
    t.classList.remove('hidden');
    setTimeout(() => t.classList.add('hidden'), 3500);
  }

  function renderizarSugestoes(data, mode) {
    const out = document.getElementById('prefill-results');
    const modeMsg = mode === 'offline'
      ? '📱 Sugestões carregadas do seu celular (modo offline). Confira os dados e confirme no SICAR.'
      : '🌐 Sugestões atualizadas. Confira e confirme no SICAR.';
    const suggestions = data.suggestions || [];

    if (!suggestions.length) {
      out.innerHTML = `<div class="alert alert-info">${modeMsg}</div><div class="card"><p>${data.human_message || 'Nenhuma área encontrada perto de você nos mapas salvos.'}</p></div>`;
      return;
    }

    out.innerHTML = `<div class="alert alert-info">${modeMsg}</div>` +
      suggestions.map((s, i) => {
        const label = s.label || (s.type === 'APP' ? 'Área de Preservação' : s.type === 'RL' ? 'Reserva Legal' : s.type);
        const detail = s.note
          ? `${s.area_ha} ha — ${s.note}`
          : `${s.source} · ${s.distance_km} km`;
        const sourceLine = s.note && s.source ? `<p class="text-muted">Fonte: ${s.source}</p>` : '';
        return `
          <div class="suggestion-item">
            <strong>${label}</strong>
            <p class="text-muted">${detail}</p>
            ${sourceLine}
            <div class="suggestion-item__actions">
              <button type="button" class="btn btn--primary" data-confirm="${i}">Confirmar</button>
              <button type="button" class="btn btn--ghost" data-ignore="${i}">Ignorar</button>
            </div>
          </div>`;
      }).join('');

    out.querySelectorAll('[data-confirm]').forEach((btn) => {
      btn.addEventListener('click', () => showToast('Sugestão confirmada — desenhe no SICAR'));
    });
  }

  async function sendWhatsAppNotification(phone, notification) {
    const result = await TerraPilotAPI.sendWhatsApp(phone, {
      text: notification.text,
      buttons: notification.buttons || [],
    });

    if (result.status === 'link_generated') {
      window.open(result.link, '_blank');
      showToast('WhatsApp aberto! Envie a mensagem para o produtor.');
    }

    return result;
  }

  function atualizarStatusConexao() {
    const badge = document.getElementById('connection-status');
    const homeBadge = document.getElementById('offline-badge');
    if (isGitHubPages) {
      if (badge) {
        badge.className = 'status-badge online';
        badge.innerHTML = '🌐 Modo demonstração — dados simulados (GitHub Pages)';
      }
      if (homeBadge) homeBadge.textContent = '🌐 Modo demonstração';
      return;
    }
    if (navigator.onLine) {
      if (badge) {
        badge.className = 'status-badge online';
        badge.innerHTML = '🟢 Internet conectada — pronto para enviar quando você quiser';
      }
      if (homeBadge) homeBadge.textContent = '🟢 Internet conectada';
    } else {
      if (badge) {
        badge.className = 'status-badge offline';
        badge.innerHTML = '🟡 Sem internet — tudo salvo no seu celular. Envia assim que conectar.';
      }
      if (homeBadge) homeBadge.textContent = '🟡 Sem internet — tudo salvo no celular';
    }
    if (navigator.onLine) TerraPilotDB.flushSyncQueue();
  }

  function renderProgressBar(labelEl, fillEl, trackEl, resolved, total) {
    const pct = total ? Math.round((resolved / total) * 100) : 0;
    if (labelEl) labelEl.textContent = total
      ? `${resolved} de ${total} etapas resolvidas`
      : 'Nenhuma etapa registrada ainda';
    if (fillEl) fillEl.style.width = `${pct}%`;
    if (trackEl) {
      trackEl.setAttribute('aria-valuenow', String(pct));
      trackEl.setAttribute('aria-valuemax', '100');
    }
  }

  async function getPropertyId() {
    const p = await TerraPilotDB.getProducer();
    return p?.property_id || 'produtor_local';
  }

  // --- HOME ---
  TerraPilotRouter.register('home', async () => {
    const pid = await getPropertyId();
    const notifs = await TerraPilotDB.listNotifications();
    const resolved = notifs.filter((n) => n.resolved).length;
    const total = notifs.length;
    const wrap = document.getElementById('global-progress');
    if (total > 0 && wrap) {
      wrap.classList.remove('hidden');
      renderProgressBar(
        document.getElementById('global-progress-label'),
        document.getElementById('global-progress-fill'),
        wrap.querySelector('[role=progressbar]'),
        resolved,
        total
      );
    }
    atualizarStatusConexao();
  });

  // --- CALCULATOR ---
  TerraPilotRouter.register('learn/calculator', () => {
    document.getElementById('btn-calc-app')?.addEventListener('click', async () => {
      const w = document.getElementById('river-width').value;
      const box = document.getElementById('calc-result');
      try {
        const r = await TerraPilotAPI.validateAPP(w);
        box.classList.remove('hidden');
        box.innerHTML = `
          <p><strong>Deixe ${r.min_width_m} metros</strong> de cada lado do rio.</p>
          <span class="legal-badge">${r.legal_ref}</span>
          <p class="mt-2">${r.human_explanation}</p>`;
      } catch (e) {
        showToast(e.message);
      }
    });
    document.getElementById('btn-calc-rl')?.addEventListener('click', async () => {
      const area = document.getElementById('property-area').value;
      const pct = document.getElementById('rl-percent').value;
      const declared = document.getElementById('declared-rl').value;
      const box = document.getElementById('rl-result');
      const r = await TerraPilotAPI.validateRL(area, declared, pct);
      box.classList.remove('hidden');
      if (r) {
        box.innerHTML = `<div class="card"><p>${r.human_explanation}</p><span class="legal-badge">${r.legal_ref}</span></div>`;
      } else {
        const needed = (parseFloat(area) * parseFloat(pct) / 100).toFixed(1);
        box.innerHTML = `<p>RL legal estimada: <strong>${needed} ha</strong> (${pct}% de ${area} ha)</p>`;
      }
    });
    document.getElementById('btn-calc-consolidated')?.addEventListener('click', async () => {
      const dateVal = document.getElementById('consolidated-date').value.trim();
      const modulos = document.getElementById('consolidated-modulos').value;
      const riverW = document.getElementById('river-width').value || '10';
      const box = document.getElementById('consolidated-result');
      try {
        const r = await TerraPilotAPI.validateConsolidated({
          deforestation_date: dateVal,
          property_size_modulos: Number(modulos),
          river_width_m: Number(riverW),
          feature_type: 'river',
        });
        if (!r) throw new Error('Sem conexão');
        box.classList.remove('hidden');
        box.innerHTML = `
          <div class="card">
            <p>${r.human_explanation}</p>
            <p class="mt-2"><strong>Padrão (Art. 4º):</strong> ${r.standard_rule.min_width_m}m</p>
            <p><strong>Consolidada (Art. 61-A):</strong> ${r.consolidated_rule.min_width_m}m</p>
            ${r.savings_m > 0 ? `<p class="benefit-card">Economia de ${r.savings_m}m na faixa de APP</p>` : ''}
            <span class="legal-badge">${r.consolidated_rule.legal_ref}</span>
          </div>`;
      } catch (e) {
        showToast(e.message || 'Preencha data e módulos fiscais');
      }
    });
  });

  // --- PREFILL ---
  TerraPilotRouter.register('declare/prefill', () => {
    document.getElementById('btn-gps')?.addEventListener('click', () => {
      if (!navigator.geolocation) return showToast('GPS não disponível');
      navigator.geolocation.getCurrentPosition(
        (pos) => {
          gpsCoords = { lat: pos.coords.latitude, lon: pos.coords.longitude };
          const el = document.getElementById('gps-coords');
          el.classList.remove('hidden');
          el.textContent = `GPS: ${gpsCoords.lat.toFixed(4)}, ${gpsCoords.lon.toFixed(4)}`;
        },
        () => showToast('Não foi possível obter GPS')
      );
    });
    document.getElementById('btn-prefill')?.addEventListener('click', async () => {
      const mun = document.getElementById('prefill-municipality').value.trim();
      if (!mun || !gpsCoords) return showToast('Informe município e GPS');
      const btn = document.getElementById('btn-prefill');
      const out = document.getElementById('prefill-results');
      btn.textContent = 'Buscando...';
      btn.disabled = true;
      out.innerHTML = '<p class="text-muted">Buscando...</p>';
      try {
        const data = await TerraPilotAPI.prefillSuggest(mun, gpsCoords.lat, gpsCoords.lon);
        renderizarSugestoes(data, 'online');
        if (data.suggestions?.length) {
          await TerraPilotDB.saveProducer({ property_id: mun.replace(/\s/g, '_').toLowerCase(), municipality: mun, ...gpsCoords });
        }
      } catch {
        console.log('Modo offline ativado — usando dados locais');
        renderizarSugestoes(window.PREFILL_MOCK || { suggestions: [], mode: 'offline' }, 'offline');
        try {
          await TerraPilotDB.saveProducer({ property_id: mun.replace(/\s/g, '_').toLowerCase(), municipality: mun, ...gpsCoords });
        } catch { /* IndexedDB indisponível — segue com sugestões locais */ }
      } finally {
        btn.textContent = 'Buscar sugestões';
        btn.disabled = false;
      }
    });
  });

  // --- VALIDATE LOCAL ---
  TerraPilotRouter.register('declare/validate-local', () => {
    document.getElementById('btn-validate-app')?.addEventListener('click', async () => {
      const w = document.getElementById('validate-river').value;
      const box = document.getElementById('validate-result');
      const r = await TerraPilotAPI.validateAPP(w);
      box.classList.remove('hidden');
      box.innerHTML = `
        <p>${r.human_explanation}</p>
        <span class="legal-badge">${r.legal_ref}</span>
        <ol style="margin:12px 0 0 20px">${r.fix_steps.map((s) => `<li>${s}</li>`).join('')}</ol>`;
    });
  });

  // --- NOTIFICATIONS LIST ---
  TerraPilotRouter.register('notifications/list', async () => {
    const list = document.getElementById('notifications-list');
    const items = await TerraPilotDB.listNotifications();
    if (!items.length) {
      list.innerHTML = '<div class="card"><p>Nenhuma notificação salva. Cole o texto do SICAR para começar.</p></div>';
      return;
    }
    list.innerHTML = items.map((n) => `
      <div class="card ${n.resolved ? 'text-muted' : ''}">
        <p>${n.simple_text || n.original_text}</p>
        <p class="text-muted mt-2">${n.resolved ? '✅ Resolvido' : '⏳ Pendente'}</p>
        ${!n.resolved ? `<a href="#/notifications/fix-guide?id=${n.id}" class="btn btn--secondary mt-2">Ver guia</a>` : ''}
      </div>`).join('');
  });

  // --- NOTIFICATION DETAIL ---
  TerraPilotRouter.register('notifications/detail', () => {
    document.getElementById('send-whatsapp-btn')?.addEventListener('click', async () => {
      const phone = document.getElementById('producer-phone')?.value?.trim();
      if (!phone) return showToast('Informe o WhatsApp do produtor');

      const translated = lastTranslation?.simple_text;
      const notification = {
        text: translated || 'Sua Reserva Legal está 2 hectares menor que o necessário. Responda 1 pra ver como corrigir.',
        buttons: [
          { id: '1', text: 'Ver como corrigir' },
          { id: '2', text: 'Falar com analista' },
          { id: '3', text: 'Agora não' },
        ],
      };

      try {
        await sendWhatsAppNotification(phone, notification);
      } catch (e) {
        showToast(e.message || 'Não foi possível gerar o link do WhatsApp');
      }
    });

    document.getElementById('btn-translate')?.addEventListener('click', async () => {
      const text = document.getElementById('notification-text').value.trim();
      if (!text) return showToast('Cole o texto da notificação');
      const box = document.getElementById('translation-result');
      box.classList.remove('hidden');
      box.innerHTML = '<p class="text-muted">Traduzindo...</p>';
      const r = await TerraPilotAPI.translateNotification(text);
      lastTranslation = r;
      sessionStorage.setItem('last_translation', JSON.stringify(r));
      const id = await TerraPilotDB.addNotification({
        original_text: r.original_text,
        simple_text: r.simple_text,
        issue_code: r.issue_code,
      });
      let stepsHtml = '';
      if (r.issue_code) {
        try {
          const guide = await TerraPilotAPI.getGuide(r.issue_code);
          stepsHtml = guide.steps.map((s, i) => `
            <div class="step-card">
              <div class="step-card__num">Passo ${i + 1}</div>
              <p>${s.instruction}</p>
              ${s.illustration ? `<img src="${s.illustration.replace('assets/guides/', 'assets/screenshots-sicar/')}" alt="" class="step-card__img">` : ''}
            </div>`).join('');
        } catch { /* no guide */ }
      }
      box.innerHTML = `
        <div class="card">
          <h3>Em português simples:</h3>
          <p style="font-size:1.15rem;margin:12px 0">${r.simple_text}</p>
          ${r.legal_ref ? `<span class="legal-badge">${r.legal_ref}</span>` : ''}
        </div>
        ${stepsHtml}
        <a href="#/notifications/fix-guide?id=${id}" class="btn btn--primary">Ver guia completo</a>
        <button type="button" id="btn-resolved" class="btn btn--secondary">Já fiz! Marcar como resolvido</button>`;
      document.getElementById('btn-resolved')?.addEventListener('click', async () => {
        await TerraPilotDB.resolveNotification(id);
        const msg = r.issue_code ? getBeneficioMessage(r.issue_code) : 'Etapa marcada como resolvida';
        showToast(`Parabéns! ${msg}`);
      });
      if (!navigator.onLine) await TerraPilotDB.enqueueSync('translate', { text });
    });
  });

  // --- FIX GUIDE ---
  TerraPilotRouter.register('notifications/fix-guide', async () => {
    const raw = sessionStorage.getItem('last_translation');
    const box = document.getElementById('fix-guide-content');
    if (!raw) return;
    const r = JSON.parse(raw);
    if (!r.issue_code) return;
    const guide = await TerraPilotAPI.getGuide(r.issue_code);
    const beneficio = getBeneficioMessage(r.issue_code);
    box.innerHTML = `
      <p class="view-subtitle">${guide.title}</p>
      <p class="benefit-card">${beneficio}</p>
      ${guide.steps.map((s, i) => `
        <div class="step-card">
          <div class="step-card__num">Passo ${i + 1}</div>
          <p>${s.instruction}</p>
          <img src="${(s.illustration || '').replace('assets/guides/', 'assets/screenshots-sicar/')}" alt="Screenshot passo ${i + 1}" class="step-card__img">
        </div>`).join('')}
      <button type="button" id="btn-mark-done" class="btn btn--primary">Já fiz! Marcar como resolvido</button>`;
    document.getElementById('btn-mark-done')?.addEventListener('click', () => {
      showToast('Ótimo! Continue no SICAR oficial para enviar.');
      location.hash = '#/progress/dashboard';
    });
  });

  // --- PROGRESS ---
  TerraPilotRouter.register('progress/dashboard', async () => {
    const pid = await getPropertyId();
    const notifs = await TerraPilotDB.listNotifications();
    const resolved = notifs.filter((n) => n.resolved).length;
    const total = notifs.length || 5;
    const displayResolved = resolved;
    const displayTotal = Math.max(total, resolved || 1);
    renderProgressBar(
      document.getElementById('progress-label'),
      document.getElementById('progress-fill'),
      document.getElementById('progress-track'),
      displayResolved,
      displayTotal
    );
    const benefits = document.getElementById('benefit-cards');
    benefits.innerHTML = renderProgressBenefits();
    try {
      const api = await TerraPilotAPI.getProgress(pid);
      if (api?.progress?.bar_message) {
        document.getElementById('progress-label').textContent = api.progress.bar_message;
      }
    } catch { /* local only */ }
  });

  TerraPilotRouter.register('progress/history', async () => {
    const list = document.getElementById('history-list');
    const items = await TerraPilotDB.listNotifications();
    if (!items.length) {
      list.innerHTML = '<div class="card"><p>Nenhuma ação registrada ainda.</p></div>';
      return;
    }
    list.innerHTML = items.map((n) => `
      <div class="card">
        <p>${n.simple_text || n.original_text}</p>
        <p class="text-muted">${n.created_at?.slice(0, 10)} — ${n.resolved ? 'Resolvido' : 'Pendente'}</p>
      </div>`).join('');
  });

  // --- FIRST DECLARATION ---
  TerraPilotRouter.register('declare/first-time', () => {
    let firstGps = null;
    document.getElementById('btn-first-gps')?.addEventListener('click', () => {
      if (!navigator.geolocation) return showToast('GPS não disponível');
      navigator.geolocation.getCurrentPosition(
        (pos) => {
          firstGps = { latitude: pos.coords.latitude, longitude: pos.coords.longitude };
          const el = document.getElementById('first-gps-coords');
          el.classList.remove('hidden');
          el.textContent = `GPS: ${firstGps.latitude.toFixed(4)}, ${firstGps.longitude.toFixed(4)}`;
        },
        () => showToast('Não foi possível obter GPS')
      );
    });
    document.getElementById('btn-first-guide')?.addEventListener('click', async () => {
      const name = document.getElementById('first-name').value.trim() || 'produtor';
      const municipality = document.getElementById('first-municipality').value.trim();
      const profile = { name, municipality, ...firstGps };
      const out = document.getElementById('first-declaration-content');
      out.innerHTML = '<p class="text-muted">Carregando guia...</p>';
      const guide = await TerraPilotAPI.guideFirstDeclaration(profile);
      out.innerHTML = `
        <p class="mb-2">${guide.human_message}</p>
        ${guide.steps.map((s) => `
          <div class="step-card">
            <div class="step-card__num">Passo ${s.step_number}</div>
            <h3>${s.title}</h3>
            <span class="legal-badge">${s.legal_ref}</span>
            <p class="mt-2">${s.instruction}</p>
            ${s.visual ? `<img src="${s.visual}" alt="" class="step-card__img">` : ''}
          </div>`).join('')}
        ${guide.pre_identified_features?.length ? `
          <div class="card mt-2">
            <h3>Áreas pré-identificadas (confirme no SICAR)</h3>
            ${guide.pre_identified_features.map((f) => `
              <p><strong>${f.label}</strong> — ${f.source} (${f.distance_km} km)</p>`).join('')}
          </div>` : ''}
        <a href="#/declare/draw-guide" class="btn btn--primary mt-2">Ver como desenhar no SICAR</a>`;
    });
  });

  // --- CAPABILITY (conteúdo estático em views/help/capability.html) ---

  // --- TRUST NETWORK ---
  TerraPilotRouter.register('network/community', () => {
    document.getElementById('btn-network-load')?.addEventListener('click', async () => {
      const code = document.getElementById('network-municipality-code').value.trim() || '2914703';
      const biome = document.getElementById('network-biome').value.trim();
      const out = document.getElementById('network-results');
      out.innerHTML = '<p class="text-muted">Carregando...</p>';
      try {
        const data = await TerraPilotAPI.getRegionalProgress(code, biome);
        out.innerHTML = `
          <div class="card">
            <h3>${data.municipality}</h3>
            <p class="benefit-card">${data.peer_message}</p>
            <p>${Math.round(data.percentage_complete * 100)}% dos produtores da região já regularizaram</p>
            <p class="text-muted">Cooperativas ativas: ${data.cooperatives_active.join(', ')}</p>
          </div>`;
      } catch {
        out.innerHTML = '<div class="card"><p>Sem conexão. Tente novamente quando tiver internet.</p></div>';
      }
    });
    document.querySelectorAll('[data-leader]').forEach((btn) => {
      btn.addEventListener('click', async () => {
        const type = btn.dataset.leader;
        const box = document.getElementById('leader-template');
        const tpl = await TerraPilotAPI.getLeaderTemplate(type);
        box.innerHTML = `
          <div class="card">
            <h3>${tpl.title}</h3>
            <p><em>${tpl.opening}</em></p>
            <ul>${(tpl.talking_points || []).map((p) => `<li>${p}</li>`).join('')}</ul>
            <p><strong>${tpl.closing}</strong></p>
          </div>`;
      });
    });
  });

  // --- PRA BENEFITS ---
  TerraPilotRouter.register('benefits/pra', () => {
    document.getElementById('btn-pra-check')?.addEventListener('click', async () => {
      const out = document.getElementById('pra-results');
      out.innerHTML = '<p class="text-muted">Verificando...</p>';
      const data = await TerraPilotAPI.checkPraEligibility({
        has_environmental_passive: document.getElementById('pra-has-passive').checked,
        notification_received: document.getElementById('pra-notification').checked,
        car_status: 'notified',
        deforestation_date: document.getElementById('pra-deforestation-date').value.trim() || null,
        surplus_vegetation_ha: Number(document.getElementById('pra-surplus').value) || null,
      });
      const benefitsHtml = data.benefits?.length
        ? `<ul>${data.benefits.map((b) => `<li>${b}</li>`).join('')}</ul>`
        : '<p>Nenhum benefício PRA aplicável no momento.</p>';
      const stepsHtml = data.adhesion_steps?.length
        ? `<ol>${data.adhesion_steps.map((s) => `<li>${s}</li>`).join('')}</ol>`
        : '';
      out.innerHTML = `
        <div class="card mt-2">
          <p>${data.human_explanation}</p>
          <span class="legal-badge">${data.legal_ref}</span>
          <p class="mt-2"><strong>Prazo:</strong> ${data.deadline}</p>
          <h3 class="mt-2">${data.eligible ? '✅ Elegível ao PRA' : '❌ Não elegível'}</h3>
          ${benefitsHtml}
          ${data.cra_note ? `<div class="benefit-card mt-2">${data.cra_note}</div>` : ''}
          ${stepsHtml}
        </div>`;
    });
  });

  // --- COLLECTIVE IMPACT ---
  TerraPilotRouter.register('benefits/collective-impact', async () => {
    const pid = await getPropertyId();
    const out = document.getElementById('collective-impact-content');
    const data = await TerraPilotAPI.getCollectiveImpact(pid);
    out.innerHTML = `
      <div class="card">
        <p class="benefit-card">${data.narrative}</p>
        <p class="mt-2">🌊 ${data.watershed_contribution}</p>
        <p>📊 ${data.municipal_goal_progress}</p>
        <p>🌱 ${data.carbon_sequestered}</p>
      </div>
      <div class="card mt-2">
        <h3>Benefícios coletivos</h3>
        <ul>${(data.collective_benefits || []).map((b) => `<li>${b}</li>`).join('')}</ul>
      </div>`;
  });

  // --- FAQ ---
  TerraPilotRouter.register('help/faq', async () => {
    const filters = { small: false, cerrado: false, livestock: false };
    const list = document.getElementById('faq-list');
    async function render() {
      const profile = {};
      if (filters.small) profile.property_size_ha = 10;
      if (filters.cerrado) profile.biome = 'Cerrado';
      if (filters.livestock) profile.production_type = 'livestock';
      const data = await TerraPilotAPI.getFAQ(profile);
      list.innerHTML = (data.entries || []).map((e) => `
        <div class="card faq-item">
          <strong>${e.question}</strong>
          <p class="mt-2 faq-answer">${e.answer}</p>
          <button type="button" class="btn btn--audio btn-audio mt-2" aria-label="Ouvir explicação sobre ${e.question.replace(/"/g, '&quot;')}">${'🔊 Ouvir explicação'}</button>
        </div>`).join('');
    }
    document.querySelectorAll('.chip[data-filter]').forEach((chip) => {
      chip.addEventListener('click', () => {
        const f = chip.dataset.filter;
        filters[f] = !filters[f];
        chip.setAttribute('aria-pressed', filters[f]);
        render();
      });
    });
    await render();
  });

  // --- AUDIO HELP ---
  TerraPilotRouter.register('help/audio-help', async () => {
    const faq = await TerraPilotAPI.loadJSON('data/faq-contextual.json');
    const list = document.getElementById('audio-list');
    list.innerHTML = faq.entries
      .map((e) => `
        <div class="faq-item card" style="margin-bottom:12px">
          <p class="faq-answer hidden" aria-hidden="true">${e.answer}</p>
          <button type="button" class="btn btn--audio btn-audio">
            🔊 ${e.question}
          </button>
        </div>`).join('');
  });

  function registerServiceWorker() {
    if (isGitHubPages) return;
    if ('serviceWorker' in navigator) {
      navigator.serviceWorker.register(terrapilotUrl('service-worker.js')).catch(console.warn);
    }
  }

  function init() {
    TerraPilotA11y.init();
    TerraPilotDB.open();
    atualizarStatusConexao();
    window.addEventListener('online', atualizarStatusConexao);
    window.addEventListener('offline', atualizarStatusConexao);
    TerraPilotRouter.start();
    registerServiceWorker();
  }

  return { init, showToast };
})();

document.addEventListener('DOMContentLoaded', () => TerraPilotApp.init());
