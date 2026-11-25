# ---------------------------------------------------------------------------
# [BLK-L-003] Alocação Proporcional de Sainte-Laguë com Pisos e Tetos
# ---------------------------------------------------------------------------
"""Algoritmo de Sainte-Laguë (Webster) com restrições de pisos e tetos.

Implementa a alocação proporcional unidimensional de cadeiras parlamentares
sujeita a restrições de canal (pisos f_c e tetos u_c), conforme o teorema de
equivalência de Balinski & Young e Gaffke & Pukelsheim (2008).

O método garante:
1. Fechamento exato da soma das cadeiras (conservação de vagas).
2. Respeito irrestrito aos pisos f_c e tetos u_c de cada categoria.
3. Monotonicidade de casa (ausência comprovada do Paradoxo do Alabama).
4. Desempate determinístico: maior quociente Q_c, maior voto bruto V_c, ordem alfabética.
5. Cálculo de divisor de equilíbrio D > 0 para auditoria e transparência.
"""

import math
from typing import Mapping


def alocar_sainte_lague(
    votos: Mapping[str, int],
    total_cadeiras: int,
    pisos: Mapping[str, int] | None = None,
    tetos: Mapping[str, int] | None = None,
) -> dict[str, int]:
    """Aloca cadeiras proporcionalmente pelo método de Sainte-Laguë com pisos e tetos.

    Inicializa cada entidade c com seu piso f_c e distribui as cadeiras restantes
    uma a uma pelo maior quociente Q_c = V_c / (2 * h_c + 1), respeitando os
    tetos u_c e aplicando desempate estritamente determinístico.

    Args:
        votos: Mapeamento {chave: contagem de votos}. Votos devem ser >= 0.
        total_cadeiras: Total exato de cadeiras a distribuir.
        pisos: Mapeamento opcional {chave: piso mínimo de cadeiras}. Padrão 0.
        tetos: Mapeamento opcional {chave: teto máximo de cadeiras}. Padrão total_cadeiras.

    Returns:
        Dicionário {chave: cadeiras_alocadas} com soma igual a total_cadeiras.

    Raises:
        ValueError: Se total_cadeiras for negativo, se houver votos/pisos/tetos negativos,
            se teto < piso, se soma_pisos > total_cadeiras, se soma_tetos < total_cadeiras,
            ou se faltarem votos em categorias elegíveis para preencher as cadeiras.
    """
    if total_cadeiras < 0:
        raise ValueError(f"Total de cadeiras não pode ser negativo: {total_cadeiras}")

    pisos_efetivos: dict[str, int] = {}
    tetos_efetivos: dict[str, int] = {}

    for c, v in votos.items():
        if v < 0:
            raise ValueError(f"Contagem de votos não pode ser negativa: '{c}' tem {v} votos.")
        pisos_efetivos[c] = 0
        tetos_efetivos[c] = total_cadeiras

    if pisos:
        for k, p in pisos.items():
            if k not in votos:
                raise ValueError(f"Chave '{k}' em pisos não existe no mapeamento de votos.")
            if p < 0:
                raise ValueError(f"Piso para '{k}' não pode ser negativo: {p}")
            pisos_efetivos[k] = p

    if tetos:
        for k, t in tetos.items():
            if k not in votos:
                raise ValueError(f"Chave '{k}' em tetos não existe no mapeamento de votos.")
            if t < 0:
                raise ValueError(f"Teto para '{k}' não pode ser negativo: {t}")
            tetos_efetivos[k] = t

    for c in votos:
        if tetos_efetivos[c] < pisos_efetivos[c]:
            raise ValueError(
                f"Teto ({tetos_efetivos[c]}) menor que piso ({pisos_efetivos[c]}) para '{c}'."
            )

    soma_pisos = sum(pisos_efetivos.values())
    soma_tetos = sum(tetos_efetivos.values())

    if soma_pisos > total_cadeiras:
        raise ValueError(
            f"Soma dos pisos ({soma_pisos}) excede o total de cadeiras ({total_cadeiras})."
        )
    if soma_tetos < total_cadeiras:
        raise ValueError(
            f"Soma dos tetos ({soma_tetos}) é menor que o total de cadeiras ({total_cadeiras})."
        )

    # 1. Inicializa cada categoria com seu piso
    alocacao: dict[str, int] = {c: pisos_efetivos[c] for c in votos}
    cadeiras_restantes = total_cadeiras - soma_pisos

    # 2. Aloca cadeiras restantes passo a passo
    while cadeiras_restantes > 0:
        elegiveis = [
            c for c in votos
            if alocacao[c] < tetos_efetivos[c] and votos[c] > 0
        ]

        if not elegiveis:
            raise ValueError(
                "Não há categorias com votos suficientes para preencher as cadeiras restantes "
                "respeitando os tetos definidos."
            )

        # Desempate determinístico:
        # 1) Maior quociente Q_c = V_c / (2 * h_c + 1)
        # 2) Maior voto bruto V_c
        # 3) Menor chave em ordem alfabética
        vencedor = min(
            elegiveis,
            key=lambda c: (
                -(votos[c] / (2 * alocacao[c] + 1)),
                -votos[c],
                c,
            ),
        )

        alocacao[vencedor] += 1
        cadeiras_restantes -= 1

    return alocacao


def calcular_divisor_equilibrio(
    votos: Mapping[str, int],
    alocacao: Mapping[str, int],
    pisos: Mapping[str, int] | None = None,
    tetos: Mapping[str, int] | None = None,
) -> float:
    """Calcula um divisor D > 0 de equilíbrio compatível com a alocação de Sainte-Laguë.

    Determina o ponto médio entre:
      - O menor limiar superior de quem recebeu cadeira acima do piso:
        D_max = min_{h_c > f_c} (V_c / (h_c - 0.5))
      - O maior limiar inferior de quem poderia receber a próxima cadeira abaixo do teto:
        D_min = max_{h_c < u_c} (V_c / (h_c + 0.5))

    Útil para auditoria, relatórios de transparência e verificação direta
    pela fórmula h_c = clamp(floor(V_c / D + 0.5), f_c, u_c).

    Args:
        votos: Mapeamento {chave: contagem de votos}.
        alocacao: Mapeamento {chave: cadeiras_alocadas}.
        pisos: Mapeamento opcional {chave: piso}. Padrão 0.
        tetos: Mapeamento opcional {chave: teto}. Padrão total de cadeiras.

    Returns:
        Divisor float D > 0 que reproduz a alocação.
    """
    total_alocada = sum(alocacao.values())
    limiares_max: list[float] = []
    limiares_min: list[float] = []

    for c, v in votos.items():
        h_c = alocacao.get(c, 0)
        f_c = pisos.get(c, 0) if pisos else 0
        u_c = tetos.get(c, total_alocada) if tetos else total_alocada

        # Quem ganhou cadeira acima do piso impõe limite superior ao divisor D
        if h_c > f_c and h_c > 0 and v > 0:
            limiares_max.append(v / (h_c - 0.5))

        # Quem não atingiu o teto impõe limite inferior ao divisor D
        if h_c < u_c and v > 0:
            limiares_min.append(v / (h_c + 0.5))

    if limiares_max and limiares_min:
        d_max = min(limiares_max)
        d_min = max(limiares_min)
        divisor = (d_min + d_max) / 2.0
    elif limiares_max:
        d_max = min(limiares_max)
        divisor = d_max / 2.0 if d_max > 0 else 1.0
    elif limiares_min:
        d_min = max(limiares_min)
        divisor = d_min * 2.0 if d_min > 0 else 1.0
    else:
        divisor = 1.0

    return max(divisor, 1e-9)
