# ---------------------------------------------------------------------------
# [BLK-L-005] Métricas Eleitorais e Auditoria de Invariantes Constitucionais
# ---------------------------------------------------------------------------
"""Métricas eleitorais e auditoria constitucional do modelo RTP.

Implementa o cálculo de índices clássicos e contemporâneos de representação
proporcional (Índice de Gallagher/LSq, Índice de Laakso-Taagepera e HHI),
a curva de sobrevivência parlamentar de legendas de médio e pequeno porte (RT-20)
e a rotina de auditoria matemática e constitucional estrita que atesta
o fechamento das 6 invariantes fundamentais do modelo.
"""

from dataclasses import dataclass
import math
from typing import Mapping

try:
    from simulador.src.constantes import (
        COLUNAS_ESTADO,
        COLUNAS_MISSAO_PADRAO,
        COLUNAS_PERMANENTES,
        PISO_GENERALISTA,
        PISO_PERMANENTE,
        TOTAL_CADEIRAS,
    )
except ImportError:  # pragma: no cover
    from constantes import (
        COLUNAS_ESTADO,
        COLUNAS_MISSAO_PADRAO,
        COLUNAS_PERMANENTES,
        PISO_GENERALISTA,
        PISO_PERMANENTE,
        TOTAL_CADEIRAS,
    )


@dataclass
class RelatorioInvariantes:
    """Resultado da auditoria de invariantes constitucionais da alocação de cadeiras.

    Attributes:
        aprovado: True se todas as invariantes e regras foram 100% satisfeitas.
        soma_total_513: True se a soma global de cadeiras na matriz for exatamente 513.
        pacto_federativo_intacto: True se cada bancada estadual coincidir com o Art. 45 da CF/88.
        fechamento_tematico_intacto: True se cada coluna fechar exatamente com seu total previsto.
        nucleo_estado_60_fixo: True se cada coluna generalista tiver rigorosamente 60 cadeiras.
        pisos_permanentes_respeitados: True se cada coluna permanente tiver pelo menos 20 cadeiras.
        tetos_missao_respeitados: True se nenhuma UF exceder seu teto de missão u_e.
        erros: Lista com mensagens descritivas detalhando cada violação detectada.
    """

    aprovado: bool
    soma_total_513: bool
    pacto_federativo_intacto: bool
    fechamento_tematico_intacto: bool
    nucleo_estado_60_fixo: bool
    pisos_permanentes_respeitados: bool
    tetos_missao_respeitados: bool
    erros: list[str]


def indice_gallagher(
    votos: Mapping[str, int],
    cadeiras: Mapping[str, int],
) -> float:
    """Calcula o índice de desproporcionalidade de mínimos quadrados de Gallagher (LSq).

    Mede o desvio de proporcionalidade entre a distribuição percentual de votos populares
    e a distribuição percentual de cadeiras parlamentares conquistadas pelos partidos.
    A escala varia de 0.0 (proporcionalidade perfeita) a 100.0 (desproporcionalidade total):

        LSq = sqrt( 0.5 * sum( (v_i% - s_i%)^2 ) )

    Args:
        votos: Mapeamento {partido: votos_recebidos}. Votos devem ser >= 0.
        cadeiras: Mapeamento {partido: cadeiras_conquistadas}. Cadeiras devem ser >= 0.

    Returns:
        Valor float do índice de Gallagher em pontos percentuais [0.0, 100.0].
        Retorna 0.0 caso não haja votos e nem cadeiras a comparar.

    Raises:
        ValueError: Se houver votos ou cadeiras negativos, ou se apenas um dos totais for zero.
    """
    for p, v in votos.items():
        if v < 0:
            raise ValueError(f"Contagem de votos não pode ser negativa: '{p}' tem {v} votos.")
    for p, s in cadeiras.items():
        if s < 0:
            raise ValueError(f"Contagem de cadeiras não pode ser negativa: '{p}' tem {s} cadeiras.")

    total_votos = sum(votos.values())
    total_cadeiras = sum(cadeiras.values())

    if total_votos == 0 and total_cadeiras == 0:
        return 0.0

    if total_votos == 0 or total_cadeiras == 0:
        raise ValueError(
            f"Total de votos ({total_votos}) e total de cadeiras ({total_cadeiras}) "
            "devem ser ambos estritamente positivos para calcular a desproporcionalidade."
        )

    todos_partidos = set(votos.keys()) | set(cadeiras.keys())
    soma_diferencas_quadrado = 0.0

    for p in todos_partidos:
        v_pct = (votos.get(p, 0) / total_votos) * 100.0
        s_pct = (cadeiras.get(p, 0) / total_cadeiras) * 100.0
        diff = v_pct - s_pct
        soma_diferencas_quadrado += diff * diff

    return math.sqrt(0.5 * soma_diferencas_quadrado)


def indice_herfindahl(contagens: Mapping[str, int]) -> float:
    """Calcula o índice de concentração de Herfindahl-Hirschman (HHI) normalizado [0.0, 1.0].

    Utilizado para medir a concentração da representação espacial das UFs dentro de
    uma coluna temática (D-06) ou o nível de concentração partidária:

        HHI = sum( p_i^2 ), onde p_i = c_i / sum( c_j )

    Args:
        contagens: Mapeamento {entidade: contagem}. Valores devem ser >= 0.

    Returns:
        Float no intervalo [0.0, 1.0]. Retorna 0.0 se a soma das contagens for zero.

    Raises:
        ValueError: Se houver valores estritamente negativos.
    """
    for k, v in contagens.items():
        if v < 0:
            raise ValueError(f"Contagem não pode ser negativa: '{k}' tem {v}.")

    total = sum(contagens.values())
    if total == 0:
        return 0.0

    return sum((v / total) ** 2 for v in contagens.values())


def numero_efetivo_partidos(contagens: Mapping[str, int]) -> float:
    """Calcula o número efetivo de partidos (N_eff) pelo índice de Laakso-Taagepera (1979).

    Mede a fragmentação partidária ponderando o peso eleitoral ou parlamentar:

        N_eff = 1 / sum( p_i^2 ) = 1 / HHI

    Args:
        contagens: Mapeamento {partido: contagem_votos_ou_cadeiras}. Valores devem ser >= 0.

    Returns:
        Float indicando o número efetivo de partidos. Retorna 0.0 se a soma for zero.

    Raises:
        ValueError: Se houver valores estritamente negativos.
    """
    hhi = indice_herfindahl(contagens)
    if hhi == 0.0:
        return 0.0
    return 1.0 / hhi


def curva_sobrevivencia_partidaria(
    votos_partidos: Mapping[str, int],
    cadeiras_partidos: Mapping[str, int],
) -> dict[str, float]:
    """Calcula a taxa de sobrevivência parlamentar por faixa de votos (Métrica RT-20 / M-10).

    Classifica os partidos nacionais em 3 faixas de votação popular:
      - "1%_a_3%": partidos com proporção de votos em [0.01, 0.03)
      - "3%_a_6%": partidos com proporção de votos em [0.03, 0.06)
      - "6%_a_10%": partidos com proporção de votos em [0.06, 0.10)

    Para cada faixa, calcula a proporção [0.0, 1.0] de legendas que obtiveram pelo menos
    1 cadeira parlamentar (cadeiras > 0). Se não houver partidos em uma faixa, retorna 0.0.

    Args:
        votos_partidos: Mapeamento {partido: votos_nacionais}. Valores >= 0.
        cadeiras_partidos: Mapeamento {partido: cadeiras_totais}. Valores >= 0.

    Returns:
        Dicionário com as 3 faixas como chaves e suas respectivas taxas de sobrevivência.

    Raises:
        ValueError: Se houver contagens de votos ou cadeiras negativas.
    """
    for p, v in votos_partidos.items():
        if v < 0:
            raise ValueError(f"Contagem de votos não pode ser negativa: '{p}' tem {v} votos.")
    for p, s in cadeiras_partidos.items():
        if s < 0:
            raise ValueError(f"Contagem de cadeiras não pode ser negativa: '{p}' tem {s} cadeiras.")

    resultado: dict[str, float] = {
        "1%_a_3%": 0.0,
        "3%_a_6%": 0.0,
        "6%_a_10%": 0.0,
    }

    total_votos = sum(votos_partidos.values())
    if total_votos == 0:
        return resultado

    faixas = (
        ("1%_a_3%", 0.01, 0.03),
        ("3%_a_6%", 0.03, 0.06),
        ("6%_a_10%", 0.06, 0.10),
    )

    partidos_por_faixa: dict[str, list[str]] = {nome: [] for nome, _, _ in faixas}

    for p, v in votos_partidos.items():
        prop = v / total_votos
        for nome, inf, sup in faixas:
            if inf <= prop < sup:
                partidos_por_faixa[nome].append(p)
                break

    for nome, partidos in partidos_por_faixa.items():
        if partidos:
            sobreviventes = sum(1 for p in partidos if cadeiras_partidos.get(p, 0) > 0)
            resultado[nome] = sobreviventes / len(partidos)

    return resultado


def auditar_invariantes_constitucionais(
    matriz_completa: Mapping[str, Mapping[str, int]],
    bancadas_uf: Mapping[str, int],
    cadeiras_colunas: Mapping[str, int],
    tetos_missao_uf: Mapping[str, int],
    colunas_estado: tuple[str, ...] = COLUNAS_ESTADO,
    colunas_permanentes: tuple[str, ...] = COLUNAS_PERMANENTES,
    colunas_missao: tuple[str, ...] = COLUNAS_MISSAO_PADRAO,
    piso_generalista: int = PISO_GENERALISTA,
    piso_permanente: int = PISO_PERMANENTE,
    total_esperado: int = TOTAL_CADEIRAS,
) -> RelatorioInvariantes:
    """Realiza a auditoria matemática e constitucional estrita da alocação final de cadeiras.

    Verifica o cumprimento simultâneo das seguintes invariantes fundamentais do modelo RTP:
      1. Conservação estrita de vagas: soma total das cadeiras na matriz == total_esperado (513).
      2. Pacto Federativo: soma das cadeiras de cada UF == bancada constitucional do Art. 45 da CF.
      3. Soberania Temática: soma das cadeiras de cada coluna == cadeiras previstas da coluna.
      4. Núcleo de Estado: cada coluna generalista (C01 a C03) possui rigorosamente piso_generalista (60).
      5. Pisos Temáticos: cada coluna permanente (C04 a C09) possui no mínimo piso_permanente (20).
      6. Contenção Federativa: soma em colunas de missão de cada UF <= teto efetivo u_e.
      7. Não-negatividade: nenhuma célula da matriz possui valor menor que zero.

    Args:
        matriz_completa: Mapeamento aninhado {uf: {coluna: cadeiras}}.
        bancadas_uf: Mapeamento {uf: bancada_total_constitucional}.
        cadeiras_colunas: Mapeamento {coluna: cadeiras_previstas}.
        tetos_missao_uf: Mapeamento {uf: teto_maximo_em_missao}.
        colunas_estado: Tupla de identificadores das colunas generalistas (padrão C01 a C03).
        colunas_permanentes: Tupla de identificadores das colunas permanentes (padrão C04 a C09).
        colunas_missao: Tupla de identificadores das colunas de missão (padrão C10 a C12).
        piso_generalista: Cadeiras fixas por coluna de Estado (padrão 60).
        piso_permanente: Cadeiras mínimas por coluna permanente (padrão 20).
        total_esperado: Total nacional de vagas (padrão 513).

    Returns:
        Instância de RelatorioInvariantes com o veredito de cada teste e lista de erros encontrados.
    """
    erros: list[str] = []

    soma_total = 0
    somas_uf: dict[str, int] = {}
    somas_coluna: dict[str, int] = {}
    somas_missao_uf: dict[str, int] = {}

    for uf, col_map in matriz_completa.items():
        soma_uf = 0
        soma_missao = 0
        for col, qtd in col_map.items():
            if qtd < 0:
                erros.append(f"Cadeira negativa na célula ('{uf}', '{col}'): {qtd}.")
            soma_uf += qtd
            soma_total += qtd
            somas_coluna[col] = somas_coluna.get(col, 0) + qtd
            if col in colunas_missao:
                soma_missao += qtd
        somas_uf[uf] = soma_uf
        somas_missao_uf[uf] = soma_missao

    # Invariante 1: Soma total de 513 cadeiras
    soma_total_ok = (soma_total == total_esperado)
    if not soma_total_ok:
        erros.append(
            f"Soma total da matriz ({soma_total}) difere do total esperado ({total_esperado})."
        )

    # Invariante 2: Pacto Federativo (Bancadas Estaduais)
    pacto_ok = True
    for uf, bancada in bancadas_uf.items():
        alocada_uf = somas_uf.get(uf, 0)
        if uf not in matriz_completa:
            pacto_ok = False
            erros.append(f"Pacto federativo violado: UF '{uf}' ausente na matriz de alocação.")
        elif alocada_uf != bancada:
            pacto_ok = False
            erros.append(
                f"Pacto federativo violado na UF '{uf}': total alocado={alocada_uf}, "
                f"bancada constitucional={bancada}."
            )
    for uf in matriz_completa:
        if uf not in bancadas_uf:
            pacto_ok = False
            erros.append(
                f"Pacto federativo violado: UF '{uf}' presente na matriz mas ausente das bancadas oficiais."
            )

    # Invariante 3: Fechamento Temático (Cadeiras por Coluna)
    fechamento_ok = True
    for col, esperado_col in cadeiras_colunas.items():
        alocada_col = somas_coluna.get(col, 0)
        if alocada_col != esperado_col:
            fechamento_ok = False
            erros.append(
                f"Fechamento temático violado na coluna '{col}': total alocado={alocada_col}, "
                f"esperado={esperado_col}."
            )
    for col in somas_coluna:
        if col not in cadeiras_colunas:
            fechamento_ok = False
            erros.append(
                f"Fechamento temático violado: coluna '{col}' presente na matriz mas não prevista."
            )

    # Invariante 4: Núcleo de Estado (60 fixo em C01-C03)
    nucleo_ok = True
    for col in colunas_estado:
        alocada_col = somas_coluna.get(col, 0)
        if alocada_col != piso_generalista:
            nucleo_ok = False
            erros.append(
                f"Núcleo de Estado violado na coluna generalista '{col}': total alocado={alocada_col}, "
                f"esperado fixo={piso_generalista}."
            )

    # Invariante 5: Pisos Permanentes (>= 20 em C04-C09)
    pisos_ok = True
    for col in colunas_permanentes:
        alocada_col = somas_coluna.get(col, 0)
        if alocada_col < piso_permanente:
            pisos_ok = False
            erros.append(
                f"Piso permanente violado na coluna '{col}': total alocado={alocada_col} "
                f"é inferior ao piso mínimo={piso_permanente}."
            )

    # Invariante 6: Tetos de Missão Institucional (Bloco 3)
    tetos_ok = True
    for uf, alocada_missao in somas_missao_uf.items():
        if uf not in tetos_missao_uf:
            tetos_ok = False
            erros.append(f"Teto de missão ausente para a UF '{uf}'.")
            continue
        teto_max = tetos_missao_uf[uf]
        if alocada_missao > teto_max:
            tetos_ok = False
            erros.append(
                f"Teto de missão violado na UF '{uf}': total alocado em missão={alocada_missao} "
                f"excede o teto permitido={teto_max}."
            )

    aprovado = bool(
        soma_total_ok
        and pacto_ok
        and fechamento_ok
        and nucleo_ok
        and pisos_ok
        and tetos_ok
        and not erros
    )

    return RelatorioInvariantes(
        aprovado=aprovado,
        soma_total_513=soma_total_ok,
        pacto_federativo_intacto=pacto_ok,
        fechamento_tematico_intacto=fechamento_ok,
        nucleo_estado_60_fixo=nucleo_ok,
        pisos_permanentes_respeitados=pisos_ok,
        tetos_missao_respeitados=tetos_ok,
        erros=erros,
    )
