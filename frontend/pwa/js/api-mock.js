/**
 * API Mock para GitHub Pages
 * Simula as respostas do backend FastAPI diretamente no navegador
 */

const MockAPI = {
  // Motor de Regras
  async calculateAppWidth(riverWidthM) {
    // Simula src/rules/app_rules.py
    if (riverWidthM <= 10) {
      return {
        min_width_m: 30,
        legal_ref: "Art. 4º, I, 'a' da Lei 12.651/2012",
        human_explanation: "Para rios com menos de 10 metros de largura, a lei exige 30 metros livres das margens.",
        fix_steps: ["Abra o SICAR", "Clique em Desenhar", "Arraste 30m pra longe do rio"]
      };
    } else if (riverWidthM <= 50) {
      return {
        min_width_m: 50,
        legal_ref: "Art. 4º, I, 'b' da Lei 12.651/2012",
        human_explanation: "Para rios entre 10 e 50 metros de largura, a lei exige 50 metros livres.",
        fix_steps: ["Abra o SICAR", "Clique em Desenhar", "Arraste 50m pra longe do rio"]
      };
    } else if (riverWidthM <= 200) {
      return {
        min_width_m: 100,
        legal_ref: "Art. 4º, I, 'c' da Lei 12.651/2012",
        human_explanation: "Para rios entre 50 e 200 metros de largura, a lei exige 100 metros livres.",
        fix_steps: ["Abra o SICAR", "Clique em Desenhar", "Arraste 100m pra longe do rio"]
      };
    }
    return { min_width_m: 200, legal_ref: "Art. 4º, I, 'd'" };
  },

  // Tradutor de Notificações
  async translateNotification(technicalText) {
    // Simula src/translator/notification_translator.py
    const translations = {
      "Inconsistência no perímetro da RL": {
        issue_code: "RL_PERIMETER_DIVERGENCE",
        human_explanation: "A área de Reserva Legal que você marcou está 2 hectares menor que o necessário. Vamos corrigir juntos em 3 passos.",
        legal_ref: "Art. 12 da Lei 12.651/2012",
        fix_steps: [
          "Abra o SICAR Offline",
          "Clique em 'Desenhar Reserva Legal'",
          "Expanda a área em 2 hectares"
        ]
      },
      "APP do curso d'água": {
        issue_code: "APP_RIVER_WIDTH",
        human_explanation: "A faixa de proteção perto do rio está menor do que a lei pede.",
        legal_ref: "Art. 4º, I da Lei 12.651/2012",
        fix_steps: [
          "Abra o SICAR",
          "Clique em 'Desenhar APP'",
          "Arraste a linha para longe do rio"
        ]
      }
    };

    for (const [key, value] of Object.entries(translations)) {
      if (technicalText.includes(key)) {
        return value;
      }
    }

    return {
      issue_code: "UNKNOWN",
      human_explanation: "Não entendemos essa notificação. Entre em contato com o órgão ambiental.",
      legal_ref: "",
      fix_steps: []
    };
  },

  // Guia Passo-a-Passo
  async getRetificationGuide(issueCode, areaHa) {
    // Simula src/guides/retification_guide.py
    const guides = {
      "RL_PERIMETER_DIVERGENCE": {
        title: "Como corrigir a Reserva Legal",
        steps: [
          {
            step: 1,
            title: "Abra o SICAR Offline",
            description: "No seu computador, abra o programa 'SICAR Offline'",
            illustration: "images/guides/sicar-open.png"
          },
          {
            step: 2,
            title: "Clique em Desenhar",
            description: "No menu, clique em 'Desenhar Reserva Legal'",
            illustration: "images/guides/draw-button.png"
          },
          {
            step: 3,
            title: "Expanda a área",
            description: `Sua Reserva Legal está ${areaHa} hectares menor. Arraste os pontos para expandir.`,
            illustration: "images/guides/expand-rl.png"
          }
        ],
        legal_explanation: "A Reserva Legal é a área da sua propriedade que precisa ter vegetação nativa. O tamanho depende do bioma.",
        audio_script: "Para corrigir a Reserva Legal, abra o SICAR Offline, clique em Desenhar Reserva Legal e expanda a área."
      },
      "APP_RIVER_WIDTH": {
        title: "Como corrigir a APP do rio",
        steps: [
          {
            step: 1,
            title: "Abra o SICAR",
            description: "Abra o programa SICAR no seu computador",
            illustration: "images/guides/sicar-open.png"
          },
          {
            step: 2,
            title: "Clique em Desenhar APP",
            description: "No menu lateral, clique em 'Desenhar APP'",
            illustration: "images/guides/draw-app.png"
          },
          {
            step: 3,
            title: "Ajuste a faixa",
            description: "Arraste a linha vermelha para longe do rio até atingir a distância correta",
            illustration: "images/guides/adjust-app.png"
          }
        ],
        legal_explanation: "APP é a faixa de terra perto de rios que protege a água. A largura depende do tamanho do rio.",
        audio_script: "Para corrigir a APP, abra o SICAR, clique em Desenhar APP e ajuste a faixa perto do rio."
      }
    };

    return guides[issueCode] || {
      title: "Guia não disponível",
      steps: [],
      legal_explanation: "",
      audio_script: ""
    };
  },

  // Progresso
  async getProgress(producerId) {
    // Simula src/progress/progress_service.py
    return {
      total_issues: 7,
      resolved_issues: 3,
      pending_issues: [
        {
          issue_code: "RL_PERIMETER_DIVERGENCE",
          description: "Reserva Legal 2ha menor",
          benefit: "Crédito rural libera em ~30 dias"
        },
        {
          issue_code: "APP_RIVER_WIDTH",
          description: "APP do rio insuficiente",
          benefit: "Evita multa de R$ 5.000"
        }
      ],
      completed_issues: [
        {
          issue_code: "DOC_MISSING",
          description: "Documento de propriedade",
          completed_at: "2026-06-20"
        }
      ]
    };
  },

  // FAQ Contextual
  async getContextualFaq(profile) {
    // Simula src/knowledge/knowledge_service.py
    const entries = [
      {
        question: "O que é Reserva Legal?",
        answer: "É a área da sua propriedade que precisa ter vegetação nativa. O tamanho depende do bioma onde você está.",
        audio_script: "Reserva Legal é a área da propriedade que precisa ter vegetação nativa.",
        legal_ref: "Art. 12 da Lei 12.651/2012"
      },
      {
        question: "O que é APP?",
        answer: "APP é Área de Preservação Permanente. É a faixa de terra perto de rios, nascentes e lagos que você não pode desmatar.",
        audio_script: "APP é a faixa de terra perto de rios e nascentes que protege a água.",
        legal_ref: "Art. 4º da Lei 12.651/2012"
      },
      {
        question: "Posso plantar na APP?",
        answer: "Não. Na APP você não pode plantar culturas. Pode apenas manter a vegetação nativa ou fazer recuperação.",
        audio_script: "Na APP não pode plantar. Só pode ter vegetação nativa.",
        legal_ref: "Art. 8º da Lei 12.651/2012"
      }
    ];

    if (profile.property_size_ha <= 30) {
      entries.push({
        question: "Tenho propriedade pequena. Tenho regras diferentes?",
        answer: "Sim! Propriedades com até 4 módulos fiscais têm regras simplificadas para Reserva Legal.",
        audio_script: "Propriedades pequenas têm regras mais simples.",
        legal_ref: "Art. 67 da Lei 12.651/2012"
      });
    }

    return {
      profile_summary: `Propriedade de ${profile.property_size_ha} hectares no bioma ${profile.biome}`,
      entries: entries
    };
  },

  // Canais (WhatsApp/SMS)
  async sendWhatsApp(phone, message) {
    // Simula src/channels/whatsapp_bot.py
    const whatsappLink = `https://api.whatsapp.com/send?phone=${phone}&text=${encodeURIComponent(message.text)}`;
    return {
      status: "link_generated",
      link: whatsappLink,
      message: "Clique no link para abrir o WhatsApp com a mensagem pronta"
    };
  },

  // Módulo Analista
  async prioritizeCases(cases) {
    // Simula src/analyst/priority_queue.py
    return cases.map(c => ({
      ...c,
      priority_score: Math.floor(Math.random() * 100),
      priority_level: "high",
      reasons: ["Erro de alto impacto", "Produtor engajado"],
      recommended_action: "Enviar notificação traduzida via WhatsApp"
    }));
  }
};

// Expor globalmente
window.MockAPI = MockAPI;
