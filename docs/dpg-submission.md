# Submissão ao DPG Indicator Framework (UNDP/DPGA)

Documento de autoavaliação do **TerraPilot** contra os [9 indicadores do DPG Standard](https://digitalpublicgoods.net/standard) (versão 2024 da Digital Public Goods Alliance).

**Repositório:** [github.com/kaiquetheodoro/TerraPilot](https://github.com/kaiquetheodoro/TerraPilot)  
**Licença:** Apache 2.0 · **Formulário oficial:** [app.digitalpublicgoods.net/form](https://app.digitalpublicgoods.net/form)

---

## 1. Resumo Executivo

O **TerraPilot** é um assistente offline que ajuda produtores rurais brasileiros a concluir retificações do Cadastro Ambiental Rural (CAR), traduzindo notificações técnicas, guiando correções passo a passo e validando regras do Código Florestal localmente. O gargalo hoje não é cadastrar — são **~4,9 milhões de imóveis com retificação paralisada** porque o produtor tem medo, não entende o processo e não consegue executar sozinho. O TerraPilot foi construído como **Bem Público Digital**: código aberto sob Apache 2.0, dados de referência em formatos abertos (JSON, GeoJSON), padrões web abertos (PWA, REST) e arquitetura que roda em qualquer SO sem lock-in de nuvem — pronto para adoção por OEMAs, ENAP/MGI e governos parceiros, não apenas como protótipo de hackathon.

---

## 2. Mapeamento dos 9 Indicadores DPG

![DPG Indicator 1](https://img.shields.io/badge/DPG-1.Relevance-✅-green)
![DPG Indicator 2](https://img.shields.io/badge/DPG-2.License-✅-green)
![DPG Indicator 3](https://img.shields.io/badge/DPG-3.Ownership-✅-green)
![DPG Indicator 4](https://img.shields.io/badge/DPG-4.Platform-✅-green)
![DPG Indicator 5](https://img.shields.io/badge/DPG-5.Documentation-✅-green)
![DPG Indicator 6](https://img.shields.io/badge/DPG-6.Data_Export-✅-green)
![DPG Indicator 7](https://img.shields.io/badge/DPG-7.Privacy-✅-green)
![DPG Indicator 8](https://img.shields.io/badge/DPG-8.Standards-✅-green)
![DPG Indicator 9](https://img.shields.io/badge/DPG-9.Adaptability-🟡-yellow)

### Indicador 1: Relevance to Sustainable Development Goals

**Status**: ✅ Atendido

**Evidência**: [README.md — Impacto Estimado](https://github.com/kaiquetheodoro/TerraPilot/blob/main/README.md#-impacto-estimado) · módulos em [`src/rules/`](https://github.com/kaiquetheodoro/TerraPilot/tree/main/src/rules), [`src/progress/`](https://github.com/kaiquetheodoro/TerraPilot/tree/main/src/progress)

**Como atende**: O TerraPilot acelera a regularização ambiental rural, conectando produtores ao cumprimento do Código Florestal. Contribui diretamente para **ODS 15** (conservação e gestão sustentável de ecossistemas terrestres via APP e RL), **ODS 2** (destrava crédito rural ao completar retificações), **ODS 16** (transparência Estado ↔ produtor, redução de retrabalho nas OEMAs) e **ODS 13** (regularização ambiental como mitigação de desmatamento irregular).

**Próximos passos**: Medir impacto real em piloto com OEMAs parceiras do haCARthon (estimativas atuais baseadas no Painel SFB).

---

### Indicador 2: Open Source License

**Status**: ✅ Atendido

**Evidência**: [`LICENSE`](https://github.com/kaiquetheodoro/TerraPilot/blob/main/LICENSE) (Apache License 2.0, aprovada pela OSI)

**Como atende**: Todo o código-fonte, dicionários, guias e FAQ são distribuídos sob Apache 2.0, permitindo uso, modificação e redistribuição por qualquer governo ou organização sem royalties. A licença está na raiz do repositório e referenciada no README.

**Próximos passos**: Nenhum — requisito plenamente atendido.

---

### Indicador 3: Clear Ownership

**Status**: ✅ Atendido

**Evidência**: [`LICENSE`](https://github.com/kaiquetheodoro/TerraPilot/blob/main/LICENSE) (Copyright 2026 TerraPilot Contributors) · [`CONTRIBUTOR_LICENSE_AGREEMENT.md`](https://github.com/kaiquetheodoro/TerraPilot/blob/main/CONTRIBUTOR_LICENSE_AGREEMENT.md) · [Repositório GitHub](https://github.com/kaiquetheodoro/TerraPilot)

**Como atende**: Copyright definido como **TerraPilot Contributors** (Kaique Theodoro, Maicon Jean e demais contribuidores). Repositório público com histórico Git auditável, CLA para contribuições externas e licença Apache 2.0 sem dependência de ativos proprietários no fluxo core.

**Próximos passos**: Formalizar entidade mantenedora institucional (parceria ENAP/MGI/FBDS) no formulário DPGA, se aplicável.

---

### Indicador 4: Platform Independence

**Status**: ✅ Atendido

**Evidência**: [README — Quick Start](https://github.com/kaiquetheodoro/TerraPilot/blob/main/README.md#-quick-start) · [`requirements.txt`](https://github.com/kaiquetheodoro/TerraPilot/blob/main/requirements.txt) · [`frontend/pwa/`](https://github.com/kaiquetheodoro/TerraPilot/tree/main/frontend/pwa)

**Como atende**: O TerraPilot roda em Linux, macOS e Windows com Python 3.12+ e navegador moderno. Backend FastAPI + SQLite local; frontend PWA estático com Service Workers. Docker é opcional (`Dockerfile` existe), não obrigatório. O fluxo core (regras, tradução, guias, progresso) funciona **sem cloud, sem APIs pagas e sem lock-in de fornecedor**.

**Próximos passos**: Documentar guia de deploy self-hosted para órgãos públicos (`docs/deployment.md`).

---

### Indicador 5: Documentation

**Status**: ✅ Atendido

**Evidência**: [`README.md`](https://github.com/kaiquetheodoro/TerraPilot/blob/main/README.md) · [`docs/architecture.md`](https://github.com/kaiquetheodoro/TerraPilot/blob/main/docs/architecture.md) · [`docs/dpg-submission.md`](https://github.com/kaiquetheodoro/TerraPilot/blob/main/docs/dpg-submission.md) · [`docs/openapi.yaml`](https://github.com/kaiquetheodoro/TerraPilot/blob/main/docs/openapi.yaml) · [`tests/`](https://github.com/kaiquetheodoro/TerraPilot/tree/main/tests) (56 testes passando)

**Como atende**: Um técnico independente pode clonar o repositório, instalar dependências, rodar API e PWA seguindo o Quick Start, e validar comportamento com testes automatizados (`pytest`). Há documentação de arquitetura, OpenAPI 3.0 com os 6 módulos, personas, integração com SICAR e este documento de submissão DPG.

**Próximos passos**: Traduzir README para inglês (`README.en.md`) para revisores internacionais da DPGA.

---

### Indicador 6: Mechanism for Extracting/Importing Data

**Status**: ✅ Atendido

**Evidência**: [`src/export/exporter.py`](https://github.com/kaiquetheodoro/TerraPilot/blob/main/src/export/exporter.py) · endpoints `/api/export/*` em [`src/api/main.py`](https://github.com/kaiquetheodoro/TerraPilot/blob/main/src/api/main.py) · [`tests/test_export.py`](https://github.com/kaiquetheodoro/TerraPilot/blob/main/tests/test_export.py)

**Como atende**: Módulo `src/export/` implementa exportação em **GeoJSON** (RFC 7946), **XML SICAR** simplificado e **relatório de progresso** (SQLite). Dados de referência permanecem em JSON/GeoJSON versionados no Git. API REST expõe `/api/export/geojson`, `/api/export/sicar` e `/api/export/progress/{property_id}`.

**Próximos passos**: Adicionar import reverso (bundle JSON → SQLite) no roadmap pós-piloto.

---

### Indicador 7: Adherence to Privacy and Other Applicable Laws

**Status**: ✅ Atendido

**Evidência**: [`docs/privacy.md`](https://github.com/kaiquetheodoro/TerraPilot/blob/main/docs/privacy.md) · design local-first · seção "Dados nunca saem do dispositivo sem consentimento explícito"

**Como atende**: Política de privacidade completa em conformidade com **LGPD** (Lei 13.709/2018): controlador é o próprio produtor (dados locais), DPO via canal oficial haCARthon (`desafios.car@enap.gov.br`), base legal Art. 7º, IX (legítimo interesse). Offline-first por design; sem coleta de PII em servidor.

**Próximos passos**: Obter declaração assinada pelo mantenedor autorizado para o formulário DPGA.

---

### Indicador 8: Adherence to Standards and Best Practices

**Status**: ✅ Atendido

**Evidência**: [`docs/openapi.yaml`](https://github.com/kaiquetheodoro/TerraPilot/blob/main/docs/openapi.yaml) · PWA [`frontend/pwa/manifest.json`](https://github.com/kaiquetheodoro/TerraPilot/blob/main/frontend/pwa/manifest.json) · GeoJSON em `data/prefill/samples/` · [`tests/`](https://github.com/kaiquetheodoro/TerraPilot/tree/main/tests)

**Como atende**: Segue padrões W3C PWA, GeoJSON (RFC 7946), REST com OpenAPI 3.0 documentando os 6 módulos e exportação, Python tipado (PEP 8), interface com botões ≥48px e linguagem de 5ª série.

**Próximos passos**: Integrar testes axe-core no CI para auditoria WCAG 2.1 AA automatizada.

---

### Indicador 9: Demonstrated Ability to be Used and Adapted

**Status**: 🟡 Parcial (estrutura pronta, países além do BR em estágio inicial)

**Evidência**: [`config/country_rules.json`](https://github.com/kaiquetheodoro/TerraPilot/blob/main/config/country_rules.json) · [README — Replicabilidade](https://github.com/kaiquetheodoro/TerraPilot/blob/main/README.md#-replicabilidade-internacional-car-como-dpg) · Quick Start funcional · API com 11 endpoints

**Como atende**: O TerraPilot roda localmente com dois comandos (`uvicorn` + `http.server`). `config/country_rules.json` documenta **BR implementado** e templates honestos para CO (template), PE/ID (research), MX (planned). Módulos desacoplados permitem fork por país sem reescrever o core.

**Próximos passos**: Codificar regras colombianas após validação jurídica; piloto com OEMA brasileira; documentar processo de fork internacional.

---

## 3. Matriz de Evidências

| Indicador | Arquivo de Evidência | Commit/Tag | Responsável |
|-----------|---------------------|------------|-------------|
| 1 — Relevância ODS | `README.md#impacto-estimado`, `src/rules/`, `src/progress/` | `677cae0` | Equipe TerraPilot |
| 2 — Licença aberta | `LICENSE` | `677cae0` | Equipe TerraPilot |
| 3 — Propriedade clara | `LICENSE`, `CONTRIBUTOR_LICENSE_AGREEMENT.md` | `main` | Kaique Theodoro, Maicon Jean |
| 4 — Independência de plataforma | `README.md#quick-start`, `requirements.txt`, `frontend/pwa/` | `main` | Equipe TerraPilot |
| 5 — Documentação | `README.md`, `docs/architecture.md`, `docs/openapi.yaml`, `tests/` | `main` | Equipe TerraPilot |
| 6 — Extração de dados | `src/export/exporter.py`, `src/api/main.py`, `tests/test_export.py` | `main` | Equipe TerraPilot |
| 7 — Privacidade / LGPD | `docs/privacy.md` | `main` | desafios.car@enap.gov.br |
| 8 — Padrões e boas práticas | `docs/openapi.yaml`, `frontend/pwa/`, `tests/` | `main` | Equipe TerraPilot |
| 9 — Uso e adaptação | `config/country_rules.json`, `README.md#replicabilidade` | `main` | Equipe TerraPilot |

---

## 4. Gap Analysis

**Itens fechados nesta preparação:**

- [x] Copyright no `LICENSE` — `Copyright 2026 TerraPilot Contributors`
- [x] `docs/privacy.md` — controlador, DPO e base legal LGPD
- [x] `src/export/` — GeoJSON, SICAR XML, relatório de progresso
- [x] `config/country_rules.json` — BR + templates internacionais honestos
- [x] `docs/openapi.yaml` — 11 endpoints dos 6 módulos + exportação
- [x] `CONTRIBUTOR_LICENSE_AGREEMENT.md`

**Gaps remanescentes antes da submissão formal:**

- [ ] **Testes de acessibilidade automatizados** — integrar axe-core no CI (Indicador 8, melhoria)
- [ ] **README em inglês** — `README.en.md` para revisores internacionais da DPGA
- [ ] **Guia de deploy self-hosted** — `docs/deployment.md` para OEMAs e governos
- [ ] **Piloto com OEMA** — demonstração de uso em produção (Indicador 9)
- [ ] **Regras internacionais codificadas** — CO/PE/ID/MX ainda em template/pesquisa
- [ ] **Declaração assinada** — mantenedor autorizado no formulário DPGA

---

## 5. Plano de Submissão

| Período | Atividade |
|---------|-----------|
| **Semana 1** | Revisão final (axe-core, README.en.md, deployment guide) |
| **Semana 2** | Revisão por pares — mentores haCARthon (ENAP/MGI/FBDS/Noruega) |
| **Semana 3** | Submissão formal em [digitalpublicgoods.net](https://app.digitalpublicgoods.net/form) |
| **Semana 4–8** | Responder feedback da equipe de revisão DPGA |
| **Mês 3** | Certificação oficial como DPG reconhecido (se aprovado) |

**Nota**: A revisão DPGA costuma levar 4–8 semanas após submissão completa. Indicadores 7–9 exigem declaração assinada pelo mantenedor autorizado — não prometemos certificação antes de fechar os gaps acima.

---

## 6. Contato para DPGA

| Campo | Valor |
|-------|-------|
| **Focal point** | Kaique Theodoro e Maicon Jean |
| **E-mail** | desafios.car@enap.gov.br |
| **GitHub** | [@kaiquetheodoro](https://github.com/kaiquetheodoro) |
| **Organização** | TerraPilot Collective (candidata a parceria ENAP/MGI/FBDS) |
| **Repositório** | https://github.com/kaiquetheodoro/TerraPilot |
| **Licença** | Apache 2.0 |

---

## Referências

- [DPG Standard](https://digitalpublicgoods.net/standard)
- [DPG Registry](https://digitalpublicgoods.net/registry)
- [Formulário de nomeação](https://app.digitalpublicgoods.net/form)
- [Principles for Digital Development](https://digitalprinciples.org/)
- [Lei 12.651/2012 — Código Florestal](https://www.planalto.gov.br/ccivil_03/_ato2011-2014/2012/lei/l12651.htm)
- [LGPD — Lei 13.709/2018](https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/l13709.htm)

---

**Última atualização:** junho/2026 · **Projeto:** TerraPilot / haCARthon 2026 (ENAP · MGI · FBDS · Embaixada da Noruega)
