# ---------------------------------------------------------------------------
# [BLK-L-002] Cálculo do Teto de Missão e Arredondamento de Sainte-Laguë
# ---------------------------------------------------------------------------
"""Cálculo do teto de bancada de missão (Bloco 3) por Unidade Federativa.

Implementa as regras de arredondamento determinístico de Sainte-Laguë (RT-01),
o dimensionamento do teto nominal tau_e e o cálculo do teto efetivo u_e
com base na taxa de votos válidos no Voto 4 (RT-04 e D-15).
"""

import math
from typing import Mapping

try:
    from simulador.src.constantes import RHO_TETO_MISSAO
except ImportError:  # pragma: no cover - fallback para execução direta/relativa
    from constantes import RHO_TETO_MISSAO


def arredondar_sainte_lague(valor: float) -> int:
    """Arredonda deterministamente conforme Sainte-Laguë (metade ou mais sobe).

    Diferente da função nativa round() do Python (round-half-to-even),
    onde 0.5 arredonda para 0, a regra de Sainte-Laguë aprovada em RT-01
    define que qualquer fração igual ou superior a 0.5 arredonda para cima.

    Args:
        valor: Número float não-negativo a arredondar.

    Returns:
        Inteiro arredondado pelo critério do inteiro mais próximo (tie-break para cima).

    Raises:
        ValueError: Se valor for estritamente menor que zero.
    """
    if valor < 0.0:
        raise ValueError(f"Valor para arredondamento não pode ser negativo: {valor}")
    return math.floor(valor + 0.5)


def calcular_tau_uf(cadeiras_uf: int, rho: float = RHO_TETO_MISSAO) -> int:
    """Calcula o teto nominal tau_e de cadeiras de missão para a bancada de uma UF.

    Aplica o percentual rho (padrão 20%) sobre a bancada total da UF com piso
    aritmético (math.floor com correção infinitesimal para estabilidade float).

    Args:
        cadeiras_uf: Bancada total de deputados da UF (ex: 8 para RR, 70 para SP).
        rho: Proporção máxima de cadeiras destinadas a missões (padrão 0.20).

    Returns:
        Teto nominal inteiro tau_e da UF.

    Raises:
        ValueError: Se cadeiras_uf for negativo ou rho fora do intervalo [0.0, 1.0].
    """
    if cadeiras_uf < 0:
        raise ValueError(f"O número de cadeiras da UF não pode ser negativo: {cadeiras_uf}")
    if not (0.0 <= rho <= 1.0):
        raise ValueError(f"O parâmetro rho deve estar contido em [0.0, 1.0]: {rho}")

    return math.floor(cadeiras_uf * rho + 1e-12)


def calcular_teto_efetivo_uf(
    cadeiras_uf: int,
    taxa_validos_voto4: float,
    rho: float = RHO_TETO_MISSAO,
) -> int:
    """Calcula o teto efetivo u_e de cadeiras de missão para uma UF (Decisão RT-01).

    Fórmula aprovada: u_e = [[ tau_e * a_e ]], onde:
      - tau_e = floor(cadeiras_uf * rho);
      - a_e = taxa_validos_voto4;
      - [[ . ]] é o arredondamento de Sainte-Laguë (fração >= 0.5 sobe).

    Args:
        cadeiras_uf: Bancada total de deputados da UF.
        taxa_validos_voto4: Proporção a_e de votos válidos no Voto 4 [0.0, 1.0].
        rho: Proporção máxima destinada a missões (padrão 0.20).

    Returns:
        Teto efetivo inteiro u_e de cadeiras de missão da UF.

    Raises:
        ValueError: Se a taxa não estiver no intervalo [0.0, 1.0] ou cadeiras < 0.
    """
    if not (0.0 <= taxa_validos_voto4 <= 1.0):
        raise ValueError(
            f"Taxa de votos válidos deve estar no intervalo [0.0, 1.0]. "
            f"Recebido: {taxa_validos_voto4}"
        )

    tau_e = calcular_tau_uf(cadeiras_uf=cadeiras_uf, rho=rho)
    return arredondar_sainte_lague(tau_e * taxa_validos_voto4)


def calcular_taxa_validos_voto4(
    votos_tema_validos: int,
    votos_protesto_branco_nulo: int,
) -> float:
    """Calcula a taxa a_e de votos válidos no Voto 4 sob a regra de 2 telas (RT-04 e D-15).

    Na urna eletrônica:
      - Tela 1: O eleitor escolhe apoiar uma das missões em disputa ou manifestar
        voto em branco/nulo de protesto contra o bloco. Se escolhe branco/nulo na Tela 1,
        esse sufrágio entra em `votos_protesto_branco_nulo` e encolhe o teto u_e.
      - Tela 2: O eleitor que escolheu apoiar um tema digita o número do candidato,
        a legenda partidária de 2 dígitos dentro do tema, ou vota em branco/nulo.
        Se votar em branco ou nulo na Tela 2 (sem candidato nem legenda partidária),
        este ato opera como voto de confiança temática neutro, computado dentro de
        `votos_tema_validos` (não encolhe u_e) e rateado proporcionalmente na célula
        daquela coluna; se digitar legenda partidária de 2 dígitos, soma ao partido
        dentro do tema.

    Args:
        votos_tema_validos: Total de votos nominais, em legenda partidária e brancos/nulos
            neutros de confiança na Tela 2.
        votos_protesto_branco_nulo: Votos em branco ou nulos deliberados na Tela 1.

    Returns:
        Taxa float a_e entre 0.0 e 1.0. Retorna 0.0 caso não haja comparecimento.

    Raises:
        ValueError: Se qualquer uma das contagens for negativa.
    """
    if votos_tema_validos < 0 or votos_protesto_branco_nulo < 0:
        raise ValueError("A contagem de votos não pode ser negativa.")

    total = votos_tema_validos + votos_protesto_branco_nulo
    if total == 0:
        return 0.0

    return votos_tema_validos / total


def calcular_tetos_nacionais(
    bancadas: Mapping[str, int],
    taxas_validos: Mapping[str, float],
    rho: float = RHO_TETO_MISSAO,
) -> dict[str, int]:
    """Calcula o dicionário {uf: u_e} de tetos efetivos para todas as bancadas estaduais.

    Args:
        bancadas: Dicionário mapeando sigla da UF para bancada total de cadeiras.
        taxas_validos: Dicionário mapeando sigla da UF para taxa a_e de válidos no Voto 4.
        rho: Percentual teto de missão (padrão 0.20).

    Returns:
        Dicionário com o teto efetivo u_e de cada UF.

    Raises:
        KeyError: Se alguma UF de bancadas não estiver presente em taxas_validos.
    """
    tetos: dict[str, int] = {}
    for uf, cadeiras in bancadas.items():
        if uf not in taxas_validos:
            raise KeyError(f"Taxa de votos válidos ausente para a UF: {uf}")
        tetos[uf] = calcular_teto_efetivo_uf(
            cadeiras_uf=cadeiras,
            taxa_validos_voto4=taxas_validos[uf],
            rho=rho,
        )
    return tetos
