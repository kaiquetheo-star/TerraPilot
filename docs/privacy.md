# Política de Privacidade — TerraPilot

**Versão:** 1.1 · **Data:** junho/2026 · **Aplicável a:** TerraPilot PWA e API (Bem Público Digital)

## 1. Quem somos

O **TerraPilot** é um assistente open source (Apache 2.0) para simplificar retificações do Cadastro Ambiental Rural (CAR) no Brasil. Este documento atende ao **Indicador 7** do [DPG Standard](https://digitalpublicgoods.net/standard) (privacidade e leis aplicáveis). Ver também a [submissão DPG completa](dpg-submission.md).

**Controlador dos dados:** O próprio produtor rural (dados em dispositivo local)

**Contato para privacidade (DPO):** desafios.car@enap.gov.br (canal oficial haCARthon)

**Mantenedores do projeto:** Kaique Theodoro e Maicon Jean · [github.com/kaiquetheodoro/TerraPilot](https://github.com/kaiquetheodoro/TerraPilot)

## 2. Quais dados tratamos

| Dado | Finalidade | Onde fica | Obrigatório? |
|------|------------|-----------|--------------|
| Identificador local do produtor (`producer_id`) | Acompanhar progresso de retificações | SQLite/IndexedDB no dispositivo | Não — pode ser anônimo |
| Município e coordenada aproximada | Pré-preenchimento com bases abertas | Dispositivo local | Não |
| `issue_codes` de retificação | Guias e barra de progresso | Dispositivo local | Sim, para usar o app |
| Perfil (tamanho propriedade, bioma, produção) | FAQ contextual | Dispositivo local | Não |

**Não coletamos por padrão:** CPF, nome completo, endereço, telefone, biometria ou dados bancários.

## 3. Bases legais (LGPD — Lei 13.709/2018)

- **Legítimo interesse** (art. 7º, IX) — orientação voluntária ao produtor rural para adequação ambiental do imóvel
- **Execução de políticas públicas** (art. 7º, III) — quando implantado por órgão ambiental parceiro
- **Consentimento** (art. 7º, I) — para qualquer sync opcional com servidor externo
- **Cumprimento de obrigação legal** (art. 7º, II) — adequação ao Código Florestal via orientação CAR

## 4. Princípios de design

1. **Local-first** — dados do produtor permanecem no aparelho por padrão
2. **Minimização** — só o necessário para orientar retificações
3. **Transparência** — regras e traduções são código aberto auditável
4. **Sem monetização de dados** — não vendemos nem compartilhamos dados com terceiros comerciais
5. **Decisão humana** — o TerraPilot orienta; a OEMA decide no SICAR oficial

## 5. Dados nunca saem do dispositivo sem consentimento explícito

Por padrão, **nenhum dado pessoal ou da propriedade é enviado a servidores externos**. O PWA funciona offline após a primeira carga.

Sync com backend (quando o produtor ou a OEMA optar por isso) só ocorre mediante **ação explícita** do usuário — por exemplo, ao tocar em "Sincronizar" com internet disponível. Não há coleta passiva, rastreamento ou analytics de terceiros no fluxo core.

Exportações (GeoJSON, XML SICAR, relatório de progresso) são geradas **localmente** e ficam sob controle do produtor.

## 6. Bases de dados públicas utilizadas

O pré-preenchimento usa exclusivamente dados abertos:

- IBGE (módulo fiscal municipal)
- MapBiomas (cobertura do solo — amostras)
- SNIRH/ANA (hidrografia — amostras)
- Portal de Consulta Pública do CAR (referência)

Esses dados **não contêm informações pessoais** do produtor.

## 7. Compartilhamento e transferência internacional

- **Sync opcional** com backend self-hosted da instituição implementadora — apenas com consentimento
- **Sem transferência internacional obrigatória** no modo offline
- Se houver sync em nuvem, deve seguir política da instituição hospedeira (ex.: datacenter no Brasil)

## 8. Segurança

- Recomenda-se **HTTPS** em produção
- SQLite e IndexedDB protegidos pelo sistema operacional do dispositivo
- Sem armazenamento de credenciais governamentais no PWA

## 9. Direitos do titular (LGPD)

O produtor pode, mediante solicitação ao controlador ou diretamente no app:

- Confirmar existência de tratamento
- Acessar dados locais (exportação JSON, GeoJSON, SQLite via `src/export/`)
- Eliminar dados (limpar armazenamento do app/navegador)
- Revogar consentimento desinstalando o PWA ou apagando dados locais

Contato: desafios.car@enap.gov.br

## 10. Retenção

- Dados locais: enquanto o produtor mantiver o app instalado
- Backend (se houver): conforme política da OEMA implementadora
- Logs de servidor: mínimo necessário, sem PII quando possível

## 11. Crianças e vulneráveis

O TerraPilot é destinado a **produtores rurais adultos** e técnicos de apoio. Não é direcionado a menores de 18 anos.

## 12. Alterações

Alterações desta política serão publicadas neste repositório com data de versão. Mudanças relevantes serão comunicadas nos canais oficiais do projeto.

## 13. Legislação aplicável

- Lei nº 13.709/2018 (LGPD)
- Lei nº 12.651/2012 (Código Florestal)
- Lei nº 12.527/2011 (Lei de Acesso à Informação)
- Decreto nº 7.830/2012 (regulamentação do CAR)

---

*Documento preparado para submissão ao DPG Indicator Framework (UNDP/DPGA).*
