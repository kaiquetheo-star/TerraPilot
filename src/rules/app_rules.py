"""
Regras de APP para cursos d'água naturais — Art. 4º, I da Lei 12.651/2012.

As faixas marginais são medidas a partir da borda da calha do leito regular,
para cursos d'água perenes e intermitentes (excluídos os efêmeros).
"""

from __future__ import annotations

from typing import TypedDict


class AppWidthResult(TypedDict):
    issue_code: str
    min_width_m: int
    legal_ref: str
    human_explanation: str
    fix_steps: list[str]
    visual_example: str


# (limite_superior_largura_rio_m, largura_app_m, alínea, descrição_faixa)
_RIVER_APP_BRACKETS: tuple[tuple[float, int, str, str], ...] = (
    (10, 30, "a", "menos de 10 metros de largura"),
    (50, 50, "b", "de 10 a 50 metros de largura"),
    (200, 100, "c", "de 50 a 200 metros de largura"),
    (600, 200, "d", "de 200 a 600 metros de largura"),
)


def _resolve_bracket(river_width_m: float) -> tuple[int, str, str]:
    if river_width_m <= 0:
        raise ValueError("A largura do rio deve ser maior que zero.")

    for upper_bound, app_width, alinea, river_description in _RIVER_APP_BRACKETS:
        if river_width_m <= upper_bound:
            return app_width, alinea, river_description

    return 500, "e", "largura superior a 600 metros"


def calculate_app_width(river_width_m: float) -> AppWidthResult:
    """
    Calcula a largura mínima da APP marginal para um curso d'água natural.

    Args:
        river_width_m: Largura do curso d'água em metros (calha do leito regular).

    Returns:
        Dicionário com issue_code, min_width_m, legal_ref, human_explanation,
        fix_steps e visual_example em linguagem acessível.
    """
    app_width, alinea, river_description = _resolve_bracket(river_width_m)
    legal_ref = f"Art. 4º, I, '{alinea}' da Lei 12.651/2012"

    if app_width == 30:
        river_label = "pequeno"
    elif app_width == 50:
        river_label = "médio"
    elif app_width == 100:
        river_label = "grande"
    elif app_width == 200:
        river_label = "muito grande"
    else:
        river_label = "de grande porte"

    human_explanation = (
        f"Seu rio tem cerca de {river_width_m:g} metros de largura. "
        f"Pela lei, você precisa deixar pelo menos {app_width} metros livres "
        f"de cada lado do rio ({river_label}), contando a partir da beira da água. "
        f"Essa faixa protege a água e evita multas no CAR."
    )

    fix_steps = [
        "Abra o SICAR Offline e localize o trecho do rio na sua propriedade.",
        "Clique em Desenhar (ou Editar) na área de APP do rio.",
        (
            f"Marque uma faixa de pelo menos {app_width} metros para cada lado, "
            "medindo a partir da borda da calha do rio (beira da água)."
        ),
        "Confira se não há construção, pasto intenso ou desmatamento dentro dessa faixa.",
        "Salve o desenho e sincronize quando tiver internet.",
    ]

    visual_example = (
        f"Imagine o rio no centro: de cada lado, uma faixa verde de {app_width} metros "
        f"sem plantio ou construção — como uma margem protegida ao longo da água."
    )

    return AppWidthResult(
        issue_code="APP_RIVER_WIDTH",
        min_width_m=app_width,
        legal_ref=legal_ref,
        human_explanation=human_explanation,
        fix_steps=fix_steps,
        visual_example=visual_example,
    )
