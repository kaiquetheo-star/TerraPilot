"""
Guia para primeira declaração do CAR.

Fluxo passo a passo para quem nunca declarou, com pré-identificação
de APP/RL via bases abertas.
"""

from __future__ import annotations

from typing import Any, TypedDict

from prefill.prefill_validator import suggest_polygons


class DeclarationStep(TypedDict):
    step_number: int
    title: str
    visual: str
    legal_ref: str
    instruction: str


class FirstDeclarationResult(TypedDict):
    title: str
    profile_summary: str
    steps: list[DeclarationStep]
    pre_identified_features: list[dict[str, Any]]
    requires_confirmation: bool
    human_message: str


_STEPS: list[dict[str, str]] = [
    {
        "title": "O que é o CAR?",
        "visual": "assets/illustrations/app-river.svg",
        "legal_ref": "Lei 12.651/2012",
        "instruction": (
            "O CAR é o cadastro da sua propriedade no meio ambiente. "
            "Com ele em dia, você pode vender, financiar e trabalhar tranquilo."
        ),
    },
    {
        "title": "O que é APP?",
        "visual": "assets/illustrations/app-river.svg",
        "legal_ref": "Art. 3º, II",
        "instruction": (
            "APP é a área de proteção perto de rios, nascentes e topos de morro. "
            "É a parte que você não pode desmatar nem construir."
        ),
    },
    {
        "title": "O que é Reserva Legal?",
        "visual": "assets/illustrations/rl-forest.svg",
        "legal_ref": "Art. 3º, III",
        "instruction": (
            "Reserva Legal é a parte da terra que a lei pede para manter com mata "
            "ou vegetação nativa — geralmente 20% a 80%, dependendo do bioma."
        ),
    },
    {
        "title": "Onde fica sua propriedade?",
        "visual": "assets/guides/sicar-open.svg",
        "legal_ref": "—",
        "instruction": (
            "Abra o SICAR Offline, informe município e desenhe o perímetro da propriedade. "
            "Use o GPS do celular para ajudar."
        ),
    },
    {
        "title": "Confira as sugestões do mapa",
        "visual": "assets/guides/draw-button.svg",
        "legal_ref": "Art. 4º e Art. 12",
        "instruction": (
            "O SICAR e o TerraPilot podem sugerir APP e RL com bases públicas. "
            "Confira cada área no mapa antes de confirmar — você decide."
        ),
    },
    {
        "title": "Salve e envie quando tiver internet",
        "visual": "assets/guides/save-sync.svg",
        "legal_ref": "—",
        "instruction": (
            "Salve o cadastro no SICAR Offline. Quando tiver sinal, sincronize. "
            "A OEMA analisa e pode pedir ajustes — o TerraPilot ajuda a entender."
        ),
    },
]


def _profile_summary(profile: dict[str, Any]) -> str:
    name = profile.get("name", "produtor")
    biome = profile.get("biome", "")
    size = profile.get("property_size_ha")
    parts = [f"Guia para {name}"]
    if size:
        parts.append(f"propriedade de {size:g} ha")
    if biome:
        parts.append(f"no bioma {biome}")
    return " — ".join(parts)


def guide_first_declaration(profile: dict[str, Any]) -> FirstDeclarationResult:
    """
    Fluxo guiado para quem nunca declarou.

    Pré-identifica APP/RL via bases abertas quando município e coordenadas
    estão no perfil. Sempre exige confirmação do produtor.
    """
    steps: list[DeclarationStep] = [
        DeclarationStep(
            step_number=i + 1,
            title=s["title"],
            visual=s["visual"],
            legal_ref=s["legal_ref"],
            instruction=s["instruction"],
        )
        for i, s in enumerate(_STEPS)
    ]

    pre_identified: list[dict[str, Any]] = []
    human_message = (
        "Siga os passos abaixo na ordem. O TerraPilot explica cada conceito "
        "antes de você abrir o SICAR."
    )

    municipality = profile.get("municipality")
    latitude = profile.get("latitude")
    longitude = profile.get("longitude")

    if municipality and latitude is not None and longitude is not None:
        try:
            prefill = suggest_polygons(municipality, float(latitude), float(longitude))
            pre_identified = [
                {
                    "id": s["id"],
                    "type": s["suggestion_type"],
                    "label": s["label"],
                    "source": s["source"],
                    "area_ha": s["area_ha"],
                    "distance_km": s["distance_km"],
                    "confidence": s["confidence"],
                }
                for s in prefill["suggestions"]
            ]
            if pre_identified:
                human_message = (
                    f"Encontramos {len(pre_identified)} área(s) perto da sua propriedade "
                    "com dados públicos. Confira cada uma antes de confirmar no SICAR."
                )
        except (KeyError, ValueError):
            pass

    return FirstDeclarationResult(
        title="Primeira declaração do CAR",
        profile_summary=_profile_summary(profile),
        steps=steps,
        pre_identified_features=pre_identified,
        requires_confirmation=True,
        human_message=human_message,
    )
