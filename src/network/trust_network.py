"""
Rede de confiança — dados agregados de regularização regional.

Baseado em dados públicos do Painel SFB (demonstração). Sem PII.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any, TypedDict

_DATA_PATH = Path(__file__).resolve().parents[2] / "data" / "network" / "regional_progress.json"

_LEADER_TEMPLATES: dict[str, dict[str, Any]] = {
    "union": {
        "title": "Reunião do sindicato — regularização do CAR",
        "opening": (
            "Colegas produtores, o CAR é o cadastro ambiental da nossa terra. "
            "Com ele em dia, liberamos crédito e evitamos multa."
        ),
        "talking_points": [
            "3 produtores da região regularizaram este mês",
            "O TerraPilot traduz as notificações do órgão para português simples",
            "Funciona offline — não precisa de internet no campo",
            "Quem precisar de ajuda, falem comigo depois da reunião",
        ],
        "closing": "Vamos juntos — ninguém fica para trás.",
    },
    "cooperative": {
        "title": "Assembleia da cooperativa — CAR e crédito rural",
        "opening": (
            "Membros da cooperativa, o banco pede CAR em dia para liberar financiamento. "
            "A regularização beneficia todos nós."
        ),
        "talking_points": [
            "Produtores regularizados têm prioridade no crédito da cooperativa",
            "O TerraPilot explica passo a passo como corrigir no SICAR",
            "Áudio disponível para quem prefere ouvir em vez de ler",
            "A cooperativa pode agendar mutirão com técnico parceiro",
        ],
        "closing": "Regularizar é investir no futuro da cooperativa.",
    },
    "agronomist": {
        "title": "Orientação técnica — retificação do CAR",
        "opening": (
            "Produtor, recebi sua notificação de retificação. "
            "Vou explicar o que precisa ser feito e onde clicar no SICAR."
        ),
        "talking_points": [
            "A notificação fala de Reserva Legal — vou mostrar no mapa",
            "O TerraPilot já validou a regra: Art. 12 da Lei 12.651",
            "Você confirma cada área no SICAR — eu reviso antes de enviar",
            "Georreferenciamento final precisa de ART do CREA",
        ],
        "closing": "Qualquer dúvida, me chame no WhatsApp.",
    },
    "bank_manager": {
        "title": "Conversa sobre crédito rural — CAR em dia",
        "opening": (
            "Seu Raimundo, para liberar o financiamento, o CAR precisa estar regularizado. "
            "Não é burocracia — é proteção da sua terra e do crédito."
        ),
        "talking_points": [
            "CAR aprovado destrava linhas de crédito rural",
            "O TerraPilot ajuda a entender a notificação do órgão ambiental",
            "Muitos produtores da região já regularizaram este mês",
            "Posso indicar técnico parceiro se precisar",
        ],
        "closing": "Regularize e voltamos a conversar sobre o financiamento.",
    },
}


class RegionalProgress(TypedDict):
    municipality: str
    municipality_code: str
    biome: str
    producers_regularized_this_month: int
    percentage_complete: float
    peer_message: str
    cooperatives_active: list[str]


@lru_cache(maxsize=1)
def _load_regional_data() -> dict[str, Any]:
    if not _DATA_PATH.exists():
        return {"municipalities": {}}
    with _DATA_PATH.open(encoding="utf-8") as handle:
        return json.load(handle)


def get_regional_progress(municipality_code: str, biome: str) -> RegionalProgress:
    """
    Dados agregados (sem PII) sobre regularização na região.

    Baseado em dados públicos do Painel SFB (amostra offline).
    """
    data = _load_regional_data()
    municipalities = data.get("municipalities", {})
    key = municipality_code.strip()

    entry = municipalities.get(key)
    if not entry:
        entry = {
            "name": f"Município {key}",
            "producers_regularized_this_month": 8,
            "percentage_complete": 0.28,
            "cooperatives_active": ["Cooperativa Regional", "Sindicato Rural"],
        }

    count = entry["producers_regularized_this_month"]
    peer_message = (
        f"{count} produtor{'es' if count != 1 else ''} da sua região "
        f"regularizaram este mês"
    )

    return RegionalProgress(
        municipality=entry["name"],
        municipality_code=key,
        biome=biome,
        producers_regularized_this_month=count,
        percentage_complete=entry["percentage_complete"],
        peer_message=peer_message,
        cooperatives_active=entry.get("cooperatives_active", []),
    )


def generate_leader_template(leader_type: str) -> dict[str, Any]:
    """
    Templates para líderes comunitários e técnicos usarem em reuniões.

    leader_type: union, cooperative, agronomist, bank_manager
    """
    if leader_type not in _LEADER_TEMPLATES:
        valid = ", ".join(_LEADER_TEMPLATES)
        raise KeyError(f"leader_type inválido: {leader_type}. Use: {valid}")

    return {
        "leader_type": leader_type,
        **_LEADER_TEMPLATES[leader_type],
    }
