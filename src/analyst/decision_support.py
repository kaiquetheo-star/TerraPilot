"""
Assistente de decisão para casos complexos.
Resolve: "Casos complexos exigem consulta a múltiplas bases"
Não decide — apresenta opções legais para a Luana decidir.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class ComplexCaseInput(BaseModel):
    case_id: str
    producer_name: str
    property_size_ha: float
    municipality: str
    state: str
    biome: str
    issue_code: str
    overlaps_uc: bool  # sobrepõe Unidade de Conservação
    uc_type: str | None  # "protecao_integral", "uso_sustentavel"
    overlaps_ti: bool  # sobrepõe Terra Indígena
    overlaps_quilombo: bool
    overlaps_border: bool  # sobrepõe fronteira com outra propriedade
    has_pending_fines: bool
    fine_count: int
    consolidated_before_2008: bool
    property_size_modulos: float
    legal_issues: list[str]  # lista de artigos aplicáveis


class LegalOption(BaseModel):
    option_id: str
    description: str
    legal_basis: str
    pros: list[str]
    cons: list[str]
    required_documents: list[str]
    estimated_time_days: int
    applicable_articles: list[str]


class DecisionSupport(BaseModel):
    case_id: str
    case_summary: str
    legal_references: list[dict[str, str]]
    risk_assessment: dict[str, str]  # legal_risk, environmental_risk, social_risk
    options: list[LegalOption]
    precedents: list[dict[str, str]]
    recommended_consultation: list[str]  # órgãos a consultar


def build_case_summary(case: ComplexCaseInput) -> str:
    """Resumo legível do caso complexo."""
    parts = [
        f"{case.producer_name} — {case.property_size_ha}ha em {case.municipality}-{case.state}"
    ]

    if case.overlaps_uc:
        parts.append(f"Sobrepõe UC ({case.uc_type})")
    if case.overlaps_ti:
        parts.append("Sobrepõe Terra Indígena")
    if case.overlaps_quilombo:
        parts.append("Sobrepõe território quilombola")
    if case.has_pending_fines:
        parts.append(f"{case.fine_count} multa(s) pendente(s)")
    if case.consolidated_before_2008:
        parts.append("Área consolidada antes de 22/07/2008")

    return " | ".join(parts)


def get_legal_references(case: ComplexCaseInput) -> list[dict[str, str]]:
    """Lista artigos relevantes da Lei 12.651 e leis relacionadas."""
    refs = [
        {"law": "Lei 12.651/2012", "article": "Art. 29", "relevance": "Obrigatoriedade do CAR"},
    ]

    if case.overlaps_uc:
        refs.append(
            {
                "law": "Lei 9.985/2000 (SNUC)",
                "article": "Art. 24",
                "relevance": "UC de Proteção Integral — uso restrito",
            }
        )
        refs.append(
            {
                "law": "Lei 12.651/2012",
                "article": "Art. 61-A §16",
                "relevance": "APP em UC não tem direito a área consolidada",
            }
        )

    if case.overlaps_ti:
        refs.append(
            {
                "law": "Constituição Federal",
                "article": "Art. 231",
                "relevance": "Direitos originários dos povos indígenas",
            }
        )

    if case.consolidated_before_2008:
        refs.append(
            {
                "law": "Lei 12.651/2012",
                "article": "Art. 61-A",
                "relevance": "Direito adquirido em APP consolidada",
            }
        )
        refs.append(
            {
                "law": "Lei 12.651/2012",
                "article": "Art. 67",
                "relevance": "Pequenas propriedades — regras simplificadas",
            }
        )

    if case.has_pending_fines:
        refs.append(
            {
                "law": "Lei 12.651/2012",
                "article": "Art. 59 §4º e §5º",
                "relevance": "Suspensão de multas via PRA",
            }
        )

    return refs


def assess_risks(case: ComplexCaseInput) -> dict[str, str]:
    """Avaliação qualitativa de riscos."""
    if case.overlaps_uc and case.uc_type == "protecao_integral":
        legal_risk = "high"
    elif case.has_pending_fines and case.fine_count > 3:
        legal_risk = "high"
    elif case.overlaps_ti or case.overlaps_quilombo:
        legal_risk = "high"
    elif case.has_pending_fines:
        legal_risk = "medium"
    else:
        legal_risk = "low"

    if case.overlaps_uc:
        environmental_risk = "high"
    elif case.property_size_ha > 100 and case.biome in ["Amazonia", "Pantanal"]:
        environmental_risk = "medium"
    else:
        environmental_risk = "low"

    if case.overlaps_ti or case.overlaps_quilombo:
        social_risk = "high"
    elif case.property_size_ha < 30:
        social_risk = "medium"
    else:
        social_risk = "low"

    return {
        "legal_risk": legal_risk,
        "environmental_risk": environmental_risk,
        "social_risk": social_risk,
    }


def generate_options(case: ComplexCaseInput) -> list[LegalOption]:
    """Gera opções legais para a analista escolher."""
    options = []

    if case.has_pending_fines or case.issue_code in ["RL_PERCENTAGE", "APP_RIVER_WIDTH"]:
        options.append(
            LegalOption(
                option_id="pra_adhesion",
                description="Adesão ao Programa de Regularização Ambiental (PRA)",
                legal_basis="Art. 59 da Lei 12.651/2012",
                pros=[
                    "Suspende multas anteriores a 22/07/2008",
                    "Mantém acesso ao crédito rural durante cumprimento",
                    "Prazos diferenciados de recomposição",
                ],
                cons=[
                    "Exige assinatura de termo de compromisso",
                    "Obrigações de longo prazo (até 20 anos)",
                ],
                required_documents=[
                    "CAR aprovado",
                    "Proposta de recomposição/compensação",
                    "Comprovante de propriedade/posse",
                ],
                estimated_time_days=180,
                applicable_articles=["Art. 59", "Art. 60"],
            )
        )

    if case.property_size_ha > 50 and not case.overlaps_uc:
        options.append(
            LegalOption(
                option_id="cra_emission",
                description="Emissão de Cota de Reserva Ambiental (ativo financeiro)",
                legal_basis="Art. 44 da Lei 12.651/2012",
                pros=[
                    "Gera ativo financeiro negociável",
                    "Pode ser usado para compensar RL de outros imóveis",
                    "Valoriza a propriedade",
                ],
                cons=[
                    "Exige laudo técnico",
                    "Vínculo permanente na matrícula",
                ],
                required_documents=[
                    "CAR aprovado",
                    "Laudo do órgão ambiental",
                    "Certidão de matrícula",
                ],
                estimated_time_days=90,
                applicable_articles=["Art. 44", "Art. 45", "Art. 46"],
            )
        )

    if case.issue_code == "RL_PERCENTAGE":
        options.append(
            LegalOption(
                option_id="rl_compensation",
                description="Compensação da RL em outra área do mesmo bioma",
                legal_basis="Art. 66 da Lei 12.651/2012",
                pros=[
                    "Alternativa à recomposição no próprio imóvel",
                    "Pode usar CRA, arrendamento ou doação",
                ],
                cons=[
                    "Área compensada deve estar no mesmo bioma",
                    "Exige inscrição no CAR",
                ],
                required_documents=[
                    "CAR do imóvel",
                    "Contrato de compensação",
                    "Comprovação de área equivalente",
                ],
                estimated_time_days=120,
                applicable_articles=["Art. 66"],
            )
        )

    if case.consolidated_before_2008 and case.issue_code in [
        "APP_RIVER_WIDTH",
        "CONSOLIDATED_APP",
    ]:
        options.append(
            LegalOption(
                option_id="consolidated_rights",
                description="Reconhecimento de direitos adquiridos (área consolidada)",
                legal_basis="Art. 61-A da Lei 12.651/2012",
                pros=[
                    "Recomposição muito menor (5m, 8m ou 15m em vez de 30-500m)",
                    "Pode manter atividades agrossilvipastoris",
                ],
                cons=[
                    "Exige comprovação de uso antes de 22/07/2008",
                    "Vedada nova supressão",
                ],
                required_documents=[
                    "Comprovação de uso anterior a 22/07/2008 (fotos, contratos, etc)",
                    "Declaração no CAR",
                ],
                estimated_time_days=60,
                applicable_articles=["Art. 61-A", "Art. 61-B"],
            )
        )

    if case.property_size_modulos <= 4 and case.issue_code == "RL_PERCENTAGE":
        options.append(
            LegalOption(
                option_id="small_property_rules",
                description="Regras simplificadas para pequena propriedade",
                legal_basis="Art. 67 da Lei 12.651/2012",
                pros=[
                    "RL = vegetação nativa existente em 22/07/2008",
                    "Sem necessidade de recomposição adicional",
                    "Cadastro simplificado",
                ],
                cons=[
                    "Vedadas novas conversões",
                    "Manutenção obrigatória da vegetação",
                ],
                required_documents=[
                    "Comprovação de área até 4 módulos fiscais",
                    "Croqui simplificado",
                ],
                estimated_time_days=30,
                applicable_articles=["Art. 67", "Art. 55"],
            )
        )

    return options


def suggest_consultations(case: ComplexCaseInput) -> list[str]:
    """Órgãos/entidades que a Luana deve consultar."""
    consultations = []

    if case.overlaps_uc:
        consultations.append("ICMBio (se UC federal) ou órgão estadual de UC")
    if case.overlaps_ti:
        consultations.append("FUNAI")
    if case.overlaps_quilombo:
        consultations.append("Fundação Palmares / INCRA")
    if case.has_pending_fines and case.fine_count > 5:
        consultations.append("Procuradoria do órgão ambiental")
    if case.property_size_ha > 1000:
        consultations.append("Equipe técnica de georreferenciamento")

    if not consultations:
        consultations.append("Nenhuma consulta externa necessária")

    return consultations


def get_precedents(case: ComplexCaseInput) -> list[dict[str, str]]:
    """Precedentes relevantes (fictícios para demo — em produção viriam de base)."""
    precedents = []

    if case.overlaps_uc:
        precedents.append(
            {
                "case": "Processo SFB 12345/2024",
                "decision": "Produtor em UC de proteção integral teve que recompor 100% da APP",
                "date": "2024-03-15",
            }
        )

    if case.consolidated_before_2008:
        precedents.append(
            {
                "case": "Processo SFB 67890/2024",
                "decision": "Direito adquirido reconhecido com comprovação fotográfica",
                "date": "2024-07-22",
            }
        )

    return precedents


def support_decision(case: ComplexCaseInput) -> DecisionSupport:
    """Gera suporte completo de decisão para a Luana."""
    return DecisionSupport(
        case_id=case.case_id,
        case_summary=build_case_summary(case),
        legal_references=get_legal_references(case),
        risk_assessment=assess_risks(case),
        options=generate_options(case),
        precedents=get_precedents(case),
        recommended_consultation=suggest_consultations(case),
    )
