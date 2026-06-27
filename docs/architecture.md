# TerraPilot — Arquitetura (haCARthon 2026)

O TerraPilot é um assistente **offline-first** para retificações do CAR. Não usa IA paga em nuvem: validações são **determinísticas** e rastreáveis pela Lei 12.651/2012.

## Visão geral

```text
┌─────────────────┐
│  Produtor (PWA) │
│  frontend/pwa/  │
└────────┬────────┘
         │ cache offline (Service Worker + IndexedDB)
         ▼
┌─────────────────────────────────────┐
│         src/api/main.py             │
│  ┌───────────────────────────────┐  │
│  │ rules/      — APP, RL         │  │
│  │ translator/ — notificações    │  │
│  │ guides/     — passo-a-passo   │  │
│  │ prefill/    — bases abertas    │  │
│  │ progress/   — barra de avanço  │  │
│  │ knowledge/  — FAQ contextual  │  │
│  │ export/     — GeoJSON, XML     │  │
│  └───────────────────────────────┘  │
└────────┬────────────────────────────┘
         │ (sync quando online)
         ▼
┌─────────────────┐
│  SICAR oficial  │
│  (car.gov.br)   │
└─────────────────┘
```

## Módulos

| Módulo | Caminho | Responsabilidade |
|--------|---------|------------------|
| API REST | `src/api/main.py` | Endpoints FastAPI |
| Regras | `src/rules/` | APP (Art. 4º) e RL (Art. 12) |
| Tradutor | `src/translator/` | OEMA → linguagem do produtor |
| Guias | `src/guides/` | Ilustrações e passos SICAR |
| Pré-preenchimento | `src/prefill/` | IBGE, MapBiomas, SNIRH (amostras offline) |
| Progresso | `src/progress/` | SQLite local, benefícios tangíveis |
| Conhecimento | `src/knowledge/` | FAQ por perfil do produtor |
| Exportação | `src/export/` | GeoJSON, XML SICAR simplificado |

## Dados e configuração

- `config/country_rules.json` — regras parametrizáveis por país
- `dictionaries/technical_to_simple.json` — padrões de tradução
- `guides/retification_guides.json` — guias visuais
- `knowledge/faq_content.json` — base de conhecimento
- `data/` — SQLite e GeoJSON de demonstração

## Princípios de design

1. **Offline-first** — PWA com Service Worker; regras rodam localmente
2. **Custo zero** — sem APIs de IA paga nem cloud provider obrigatório
3. **Rastreabilidade legal** — cada resposta cita artigo da Lei 12.651/2012
4. **Bem Público Digital** — Apache 2.0, dados exportáveis, LGPD por design
5. **Não substitui o SICAR** — camada de orientação; decisão final é da OEMA

## Execução local

```bash
uvicorn src.api.main:app --host 0.0.0.0 --port 8001
cd frontend/pwa && python3 -m http.server 8080
```

Documentação da API: [`openapi.yaml`](openapi.yaml).

## Versão histórica

Código da versão anterior (hackathon internacional, agente com IA em nuvem) está em [`_archive/legacy-alibaba-version/`](../_archive/legacy-alibaba-version/README.md).
