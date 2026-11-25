# ---------------------------------------------------------------------------
# [BLK-L-007] Simuladores de Estresse do Red Team (RT-19 a RT-23)
# ---------------------------------------------------------------------------
"""Módulo de experimentos de estresse e testes de robustez do Red Team.

Implementa as 5 simulações analíticas de estresse aprovadas no relatório
consolidado do Red Team (RT-01):
  - RT-19: Voto estratégico de enterro sob regras da Q-05 (M-06);
  - RT-20: Choque de votos de puxador temático e transbordamento federativo (M-07);
  - RT-21: Modelo de filas e tempo de cabine eleitoral (U-04);
  - RT-22: Comparecimento heterogêneo entre UFs com e sem 2º turno (U-03);
  - RT-23: Sensibilidade do cálculo biproporcional a atraso de totalização (U-08).

Todas as funções são puras, determinísticas, fortemente tipadas e executadas
utilizando unicamente a Standard Library do Python 3.12.
"""

from dataclasses import dataclass
import math
from typing import Final, Mapping, Sequence

try:
    from simulador.src.biproporcional import alocar_biproporcional
    from simulador.src.constantes import (
        BANCADAS_ESTADUAIS,
        COLUNAS_ESTADO,
        COLUNAS_PERMANENTES,
        PISO_PERMANENTE,
        TOTAL_CADEIRAS,
    )
    from simulador.src.sainte_lague import alocar_sainte_lague
except ImportError:  # pragma: no cover - fallback para imports locais
    from biproporcional import alocar_biproporcional
    from constantes import (
        BANCADAS_ESTADUAIS,
        COLUNAS_ESTADO,
        COLUNAS_PERMANENTES,
        PISO_PERMANENTE,
        TOTAL_CADEIRAS,
    )
    from sainte_lague import alocar_sainte_lague

# Constantes e valores de referência para os experimentos de estresse
UFS_2T_GOVERNADOR_PADRAO: Final[tuple[str, ...]] = (
    "AL", "AM", "BA", "ES", "MS", "PB", "PE", "RO", "RS", "SC", "SE", "SP"
)
UFS_REMOTAS_PADRAO: Final[tuple[str, ...]] = ("AC", "AM", "AP", "RR")


def gerar_matriz_votos_base_27x9() -> dict[str, dict[str, int]]:
    """Gera matriz determinística e realista de votos para as 27 UFs x 9 colunas.

    Aplica fatores temáticos regionais consistentes e determinísticos proporcionais
    às bancadas constitucionais de cada UF, sem depender de sementes aleatórias
    ou da função de hash não-determinística do interpretador.

    Returns:
        Matriz de votos {uf: {coluna: votos}} para as 27 UFs e 9 colunas básicas.
    """
    ufs = sorted(BANCADAS_ESTADUAIS.keys())
    colunas_9 = tuple(COLUNAS_ESTADO + COLUNAS_PERMANENTES)
    matriz: dict[str, dict[str, int]] = {}

    for i, u in enumerate(ufs):
        bancada = BANCADAS_ESTADUAIS[u]
        matriz[u] = {}
        for j, c in enumerate(colunas_9):
            fator = 1.0 + 0.04 * (((i * 5 + j * 11) % 13) - 6)
            matriz[u][c] = max(1000, int(bancada * 50_000 * fator))
    return matriz


# ===========================================================================
# RT-19: Voto Estratégico de Enterro (Q-05 / M-06)
# ===========================================================================

@dataclass(frozen=True)
class ResultadoVotoEnterroRT19:
    """Resultado da simulação de voto de enterro nas colunas permanentes (RT-19 / Q-05).

    Attributes:
        cenario_a_cumulacao: Cadeiras sob Regra A (cumulação permitida: 2 votos em Saúde).
        cenario_b_sincero: Cadeiras sob Regra B (sem cumulação, voto sincero: 1 Saúde, 1 Educação).
        cenario_c_enterro: Cadeiras sob Regra C (sem cumulação, voto enterro: 1 Saúde, 1 Ciência).
        cadeiras_saude: Comparativo das cadeiras da Saúde nos cenários {"A": ..., "B": ..., "C": ...}.
        cadeiras_educacao: Comparativo das cadeiras da Educação nos cenários.
        cadeiras_ciencia_trabalho: Comparativo das cadeiras de Ciência/Trabalho nos cenários.
        ganho_enterro_vs_sincero: Diferença de cadeiras da Saúde (Cenário C - Cenário B).
        coluna_enterro_travada_no_piso: True se a coluna de enterro ficou exatamente no piso (20).
    """

    cenario_a_cumulacao: dict[str, int]
    cenario_b_sincero: dict[str, int]
    cenario_c_enterro: dict[str, int]
    cadeiras_saude: dict[str, int]
    cadeiras_educacao: dict[str, int]
    cadeiras_ciencia_trabalho: dict[str, int]
    ganho_enterro_vs_sincero: int
    coluna_enterro_travada_no_piso: bool


def simular_voto_enterro_rt19(
    votos_base: Mapping[str, int] | None = None,
    eleitores_estrategicos: int = 500_000,
    coluna_alvo: str = "C04_SAUDE",
    coluna_concorrente: str = "C05_EDUCACAO",
    coluna_enterro: str = "C09_CIENCIA_TRABALHO",
    total_cadeiras_bloco2: int = 333,
    piso_permanente: int = PISO_PERMANENTE,
) -> ResultadoVotoEnterroRT19:
    """Simula o impacto de um grupo organizado e do voto de enterro sob regras da Q-05.

    No Bloco 2 (colunas permanentes), cada eleitor possui 2 sufrágios (Voto 2 e Voto 3).
    A hipótese RT-19 analisa um contingente de eleitores cuja prioridade sincera é
    `coluna_alvo` (Saúde) e compara o resultado sob 3 regimes:
      - Regra A (cumulação permitida): 2 votos em Saúde.
      - Regra B (cumulação proibida, voto sincero): 1 voto em Saúde e 1 voto na
        segunda preferência sincera (`coluna_concorrente`, Educação).
      - Regra C (cumulação proibida, voto de enterro estratégico): 1 voto em Saúde e 1 voto
        enterrado em `coluna_enterro` (Ciência e Trabalho), coluna que já está
        ancorada no piso de 20 cadeiras.

    Ao enterrar o voto numa coluna presa ao piso, o eleitor evita alavancar a
    concorrente direta (Educação), aumentando a chance de Saúde conquistar uma
    cadeira marginal adicional pelo quociente de Sainte-Laguë.

    Args:
        votos_base: Dicionário base de votos nacionais das colunas permanentes.
        eleitores_estrategicos: Contingente de eleitores organizados da coluna alvo.
        coluna_alvo: Coluna prioritária dos eleitores estratégicos (padrão C04_SAUDE).
        coluna_concorrente: Coluna concorrente de maior quociente (padrão C05_EDUCACAO).
        coluna_enterro: Coluna de baixa votação ancorada no piso (padrão C09_CIENCIA_TRABALHO).
        total_cadeiras_bloco2: Total de assentos do bloco permanente (padrão 333).
        piso_permanente: Piso mínimo garantido por coluna permanente (padrão 20).

    Returns:
        Estrutura ResultadoVotoEnterroRT19 com a partilha de cadeiras nos 3 cenários.

    Raises:
        ValueError: Se contagens de votos forem negativas ou se as colunas forem inválidas.
    """
    if eleitores_estrategicos < 0:
        raise ValueError(f"Contingente de eleitores não pode ser negativo: {eleitores_estrategicos}")
    if total_cadeiras_bloco2 <= 0:
        raise ValueError(f"Total de cadeiras deve ser positivo: {total_cadeiras_bloco2}")
    if piso_permanente < 0:
        raise ValueError(f"Piso permanente não pode ser negativo: {piso_permanente}")

    if votos_base is None:
        votos_base = {
            "C04_SAUDE": 15_000_000,
            "C05_EDUCACAO": 14_500_000,
            "C06_SEGURANCA": 12_000_000,
            "C07_INFRAESTRUTURA": 10_000_000,
            "C08_AGRO_AMBIENTE": 8_000_000,
            "C09_CIENCIA_TRABALHO": 500_000,
        }

    for c in (coluna_alvo, coluna_concorrente, coluna_enterro):
        if c not in votos_base:
            raise ValueError(f"Coluna '{c}' não encontrada no mapeamento de votos_base.")

    pisos = {c: piso_permanente for c in votos_base}

    # Cenário A: Cumulação permitida (2 votos na coluna alvo)
    votos_a = dict(votos_base)
    votos_a[coluna_alvo] += 2 * eleitores_estrategicos
    aloc_a = alocar_sainte_lague(votos_a, total_cadeiras_bloco2, pisos)

    # Cenário B: Cumulação proibida, voto sincero (1 voto alvo, 1 concorrente)
    votos_b = dict(votos_base)
    votos_b[coluna_alvo] += eleitores_estrategicos
    votos_b[coluna_concorrente] += eleitores_estrategicos
    aloc_b = alocar_sainte_lague(votos_b, total_cadeiras_bloco2, pisos)

    # Cenário C: Cumulação proibida, voto de enterro (1 voto alvo, 1 enterro no piso)
    votos_c = dict(votos_base)
    votos_c[coluna_alvo] += eleitores_estrategicos
    votos_c[coluna_enterro] += eleitores_estrategicos
    aloc_c = alocar_sainte_lague(votos_c, total_cadeiras_bloco2, pisos)

    ganho = aloc_c[coluna_alvo] - aloc_b[coluna_alvo]
    travada = aloc_c[coluna_enterro] == piso_permanente

    return ResultadoVotoEnterroRT19(
        cenario_a_cumulacao=aloc_a,
        cenario_b_sincero=aloc_b,
        cenario_c_enterro=aloc_c,
        cadeiras_saude={
            "A": aloc_a[coluna_alvo],
            "B": aloc_b[coluna_alvo],
            "C": aloc_c[coluna_alvo],
        },
        cadeiras_educacao={
            "A": aloc_a[coluna_concorrente],
            "B": aloc_b[coluna_concorrente],
            "C": aloc_c[coluna_concorrente],
        },
        cadeiras_ciencia_trabalho={
            "A": aloc_a[coluna_enterro],
            "B": aloc_b[coluna_enterro],
            "C": aloc_c[coluna_enterro],
        },
        ganho_enterro_vs_sincero=ganho,
        coluna_enterro_travada_no_piso=travada,
    )


# ===========================================================================
# RT-20: Choque de Puxador Temático e Transbordamento Espacial (M-07 / RT-16)
# ===========================================================================

@dataclass(frozen=True)
class ResultadoTransbordamentoRT20:
    """Resultado do choque de votos de puxador temático em uma UF (RT-20 / M-07).

    Attributes:
        ganho_nacional_coluna: Cadeiras adicionais que a coluna conquistou nacionalmente.
        ganho_sp: Cadeiras adicionais que a coluna conquistou na UF do choque.
        ganho_outras_ufs: Cadeiras adicionais conquistadas nas demais 26 UFs (transbordamento).
        detalhe_outras_ufs: Variação de cadeiras da coluna em cada UF (excluindo a UF do choque).
        cadeiras_nacionais_antes: Cadeiras de cada coluna antes do choque.
        cadeiras_nacionais_depois: Cadeiras de cada coluna após o choque.
        cadeiras_sp_antes: Distribuição de cadeiras na UF do choque antes do choque.
        cadeiras_sp_depois: Distribuição de cadeiras na UF do choque após o choque.
    """

    ganho_nacional_coluna: int
    ganho_sp: int
    ganho_outras_ufs: int
    detalhe_outras_ufs: dict[str, int]
    cadeiras_nacionais_antes: dict[str, int]
    cadeiras_nacionais_depois: dict[str, int]
    cadeiras_sp_antes: dict[str, int]
    cadeiras_sp_depois: dict[str, int]


def simular_transbordamento_puxador_rt20(
    votos_base: Mapping[str, Mapping[str, int]] | None = None,
    votos_choque: int = 2_500_000,
    coluna_choque: str = "C06_SEGURANCA",
    uf_choque: str = "SP",
) -> ResultadoTransbordamentoRT20:
    """Simula o choque de um puxador temático concentrado em SP e seu efeito espacial.

    Modela a hipótese do Red Team onde uma candidatura emblemática de alta densidade
    eleitoral (ex: +2,5 milhões de votos em Segurança em SP) expande o tamanho nacional
    da coluna correspondente $h_c$ via Sainte-Laguë. Pelo cálculo biproporcional de
    Balinski-Demange, como a bancada de SP é rígida em 70 assentos (Art. 45), o excedente
    nacional transborda espacialmente para as outras 26 UFs (trade-off M-07 e RT-16).

    Args:
        votos_base: Matriz base de votos {uf: {coluna: votos}} de 27 UFs x 9 colunas.
        votos_choque: Votos extraordinários injetados na coluna da UF indicada.
        coluna_choque: Coluna que recebe o choque (padrão C06_SEGURANCA).
        uf_choque: Sigla da UF do puxador temático (padrão SP).

    Returns:
        ResultadoTransbordamentoRT20 mensurando ganhos em SP, no país e nas demais UFs.

    Raises:
        ValueError: Se votos_choque for negativo ou colunas/UFs forem inválidas.
    """
    if votos_choque < 0:
        raise ValueError(f"Votos de choque não podem ser negativos: {votos_choque}")

    if votos_base is None:
        votos_base = gerar_matriz_votos_base_27x9()

    ufs = sorted(BANCADAS_ESTADUAIS.keys())
    colunas_9 = tuple(COLUNAS_ESTADO + COLUNAS_PERMANENTES)

    if uf_choque not in votos_base:
        raise ValueError(f"UF do choque '{uf_choque}' não existe na matriz de votos.")
    if coluna_choque not in colunas_9:
        raise ValueError(f"Coluna do choque '{coluna_choque}' inválida para o cenário 9 colunas.")

    # 1. Alocação pré-choque (antes)
    v_col_antes = {c: sum(votos_base[u][c] for u in ufs) for c in colunas_9}
    cad_col_antes = {c: 60 for c in COLUNAS_ESTADO}
    cad_col_antes.update(
        alocar_sainte_lague(
            {c: v_col_antes[c] for c in COLUNAS_PERMANENTES},
            total_cadeiras=333,
            pisos={c: PISO_PERMANENTE for c in COLUNAS_PERMANENTES},
        )
    )
    res_antes = alocar_biproporcional(votos_base, BANCADAS_ESTADUAIS, cad_col_antes)

    # 2. Injeção do choque na UF indicada
    votos_depois: dict[str, dict[str, int]] = {u: dict(votos_base[u]) for u in ufs}
    votos_depois[uf_choque][coluna_choque] += votos_choque

    v_col_depois = {c: sum(votos_depois[u][c] for u in ufs) for c in colunas_9}
    cad_col_depois = {c: 60 for c in COLUNAS_ESTADO}
    cad_col_depois.update(
        alocar_sainte_lague(
            {c: v_col_depois[c] for c in COLUNAS_PERMANENTES},
            total_cadeiras=333,
            pisos={c: PISO_PERMANENTE for c in COLUNAS_PERMANENTES},
        )
    )
    res_depois = alocar_biproporcional(votos_depois, BANCADAS_ESTADUAIS, cad_col_depois)

    ganho_nacional = cad_col_depois[coluna_choque] - cad_col_antes[coluna_choque]
    ganho_uf = res_depois.matriz[uf_choque][coluna_choque] - res_antes.matriz[uf_choque][coluna_choque]

    detalhe_outras: dict[str, int] = {}
    ganho_outras = 0
    for u in ufs:
        if u != uf_choque:
            diff = res_depois.matriz[u][coluna_choque] - res_antes.matriz[u][coluna_choque]
            detalhe_outras[u] = diff
            ganho_outras += diff

    return ResultadoTransbordamentoRT20(
        ganho_nacional_coluna=ganho_nacional,
        ganho_sp=ganho_uf,
        ganho_outras_ufs=ganho_outras,
        detalhe_outras_ufs=detalhe_outras,
        cadeiras_nacionais_antes=cad_col_antes,
        cadeiras_nacionais_depois=cad_col_depois,
        cadeiras_sp_antes=res_antes.matriz[uf_choque],
        cadeiras_sp_depois=res_depois.matriz[uf_choque],
    )


# ===========================================================================
# RT-21: Modelo de Filas e Tempo de Cabine Eleitoral (U-04 / RT-21)
# ===========================================================================

@dataclass(frozen=True)
class MetricasFilaSecao:
    """Métricas operacionais de fila de uma seção eleitoral típica.

    Attributes:
        capacidade_maxima_secao: Capacidade teórica máxima de votantes nas 9h de votação.
        eleitores_atendidos_ate_17h: Total de eleitores que concluíram a votação até as 17h.
        fila_residual_as_17h: Total de eleitores que entraram na fila mas não concluíram até 17h.
        minutos_extras_apos_17h: Minutos adicionais além das 17h necessários para esgotar a fila.
        tempo_medio_espera_minutos: Tempo médio de espera em fila de cada eleitor em minutos.
    """

    capacidade_maxima_secao: int
    eleitores_atendidos_ate_17h: int
    fila_residual_as_17h: int
    minutos_extras_apos_17h: float
    tempo_medio_espera_minutos: float


@dataclass(frozen=True)
class ResultadoFilasRT21:
    """Comparativo de filas de cabine entre os modelos eleitorais (RT-21 / U-04).

    Attributes:
        cenario_1t_atual: Desempenho no 1º turno atual (57s votação + 15s biometria = 72s).
        cenario_rtp_sem_ranqueamento: Desempenho no 2º turno RTP uninominal simples (55s + 15s = 70s).
        cenario_rtp_stv_enxuto: Desempenho no 2º turno RTP com STV enxuto — 1 número obrigatório + 2ª opção opcional (72s + 15s = 87s).
        cenario_rtp_com_ranqueamento: Desempenho no 2º turno com ordenação extensa (130s + 15s = 145s).
    """

    cenario_1t_atual: MetricasFilaSecao
    cenario_rtp_sem_ranqueamento: MetricasFilaSecao
    cenario_rtp_stv_enxuto: MetricasFilaSecao
    cenario_rtp_com_ranqueamento: MetricasFilaSecao


def _simular_fila_unitaria(
    total_eleitores: int,
    tempo_servico_segundos: float,
    duracao_segundos: float,
    perfil_pesos_horarios: Sequence[float],
) -> MetricasFilaSecao:
    """Executa a simulação determinística de fila para uma seção eleitoral."""
    if total_eleitores == 0:
        return MetricasFilaSecao(
            capacidade_maxima_secao=int(duracao_segundos / tempo_servico_segundos),
            eleitores_atendidos_ate_17h=0,
            fila_residual_as_17h=0,
            minutos_extras_apos_17h=0.0,
            tempo_medio_espera_minutos=0.0,
        )

    # Distribuição determinística de chegadas ao longo das horas
    chegadas: list[float] = []
    contagens = [int(total_eleitores * p) for p in perfil_pesos_horarios]
    falta = total_eleitores - sum(contagens)
    for i in range(falta):
        contagens[i % len(contagens)] += 1

    duracao_hora_segundos = duracao_segundos / len(perfil_pesos_horarios)

    for h, cnt in enumerate(contagens):
        if cnt <= 0:
            continue
        intervalo = duracao_hora_segundos / cnt
        for k in range(cnt):
            t = h * duracao_hora_segundos + (k + 0.5) * intervalo
            chegadas.append(t)

    chegadas.sort()

    finish: list[float] = []
    esperas: list[float] = []
    f_prev = 0.0

    for a in chegadas:
        st = max(a, f_prev)
        fn = st + tempo_servico_segundos
        esperas.append(st - a)
        finish.append(fn)
        f_prev = fn

    cap_max = int(duracao_segundos / tempo_servico_segundos)
    atendidos_17h = sum(1 for f in finish if f <= duracao_segundos)
    fila_residual = total_eleitores - atendidos_17h
    minutos_extras = max(0.0, (finish[-1] - duracao_segundos) / 60.0) if finish else 0.0
    espera_media = (sum(esperas) / total_eleitores) / 60.0

    return MetricasFilaSecao(
        capacidade_maxima_secao=cap_max,
        eleitores_atendidos_ate_17h=atendidos_17h,
        fila_residual_as_17h=fila_residual,
        minutos_extras_apos_17h=round(minutos_extras, 2),
        tempo_medio_espera_minutos=round(espera_media, 2),
    )


def simular_filas_cabine_rt21(
    eleitores_aptos: int = 400,
    taxa_comparecimento: float = 0.80,
    duracao_minutos: int = 540,
    tempo_biometria_segundos: float = 15.0,
    tempo_1t_segundos: float = 57.0,
    tempo_sem_ranqueamento_segundos: float = 55.0,
    tempo_stv_enxuto_segundos: float = 72.0,
    tempo_com_ranqueamento_segundos: float = 130.0,
    perfil_chegada: Sequence[float] | None = None,
) -> ResultadoFilasRT21:
    """Modela a dinâmica de tempo de cabine e filas em uma seção eleitoral típica (RT-21).

    Avalia a crítica U-04 ("colapso de filas") comparando quatro regimes:
      1. 1º turno tradicional: 57s de votação + 15s de biometria = 72s totais.
      2. 2º turno RTP uninominal: 55s de votação simples + 15s de biometria = 70s totais.
      3. 2º turno RTP STV enxuto (D-12): 72s médios (1 número obrigatório + até uma 2ª opção
         estritamente opcional e rápida nos Votos 1–3) + 15s de biometria = 87s totais.
      4. 2º turno com ordenação extensa: 130s de cabine complexa + 15s de biometria = 145s.

    Demonstra que tanto o modelo uninominal simples quanto o STV enxuto (até 2ª opção opcional)
    mantêm capacidade operacional segura dentro das 9h de votação, enquanto a alternativa de
    ordenação extensa (3+ escolhas) rompe a capacidade de atendimento, gerando filas elevadas.

    Args:
        eleitores_aptos: Eleitores cadastrados na seção eleitoral (padrão 400).
        taxa_comparecimento: Taxa de eleitores que comparecem para votar (padrão 0.80 -> 320).
        duracao_minutos: Horas de funcionamento da seção em minutos (padrão 540 min = 9h).
        tempo_biometria_segundos: Tempo gasto no cadastramento biométrico/habilitação (padrão 15s).
        tempo_1t_segundos: Tempo de digitação no 1º turno atual (padrão 57s).
        tempo_sem_ranqueamento_segundos: Tempo no 2º turno RTP simples (padrão 55s).
        tempo_stv_enxuto_segundos: Tempo médio no 2º turno RTP STV enxuto (padrão 72s).
        tempo_com_ranqueamento_segundos: Tempo no modelo de ordenação longa (padrão 130s).
        perfil_chegada: Distribuição proporcional de chegada ao longo das horas.

    Returns:
        ResultadoFilasRT21 contendo o desempenho comparativo dos quatro cenários.

    Raises:
        ValueError: Se parâmetros forem negativos ou taxa_comparecimento fora de [0.0, 1.0].
    """
    if eleitores_aptos <= 0:
        raise ValueError(f"Eleitores aptos deve ser estritamente positivo: {eleitores_aptos}")
    if not (0.0 <= taxa_comparecimento <= 1.0):
        raise ValueError(f"Taxa de comparecimento deve estar em [0.0, 1.0]: {taxa_comparecimento}")
    if duracao_minutos <= 0:
        raise ValueError(f"Duração em minutos deve ser positiva: {duracao_minutos}")
    if min(
        tempo_biometria_segundos,
        tempo_1t_segundos,
        tempo_sem_ranqueamento_segundos,
        tempo_stv_enxuto_segundos,
        tempo_com_ranqueamento_segundos,
    ) <= 0:
        raise ValueError("Tempos operacionais de cabine devem ser estritamente positivos.")

    if perfil_chegada is None:
        # Perfil empírico típico de 9 horas de eleição no Brasil (8h às 17h)
        perfil_chegada = (0.12, 0.15, 0.14, 0.11, 0.09, 0.09, 0.10, 0.11, 0.09)

    soma_perfil = sum(perfil_chegada)
    if soma_perfil <= 0:
        raise ValueError("Soma dos pesos do perfil de chegada deve ser positiva.")
    perfil_norm = [p / soma_perfil for p in perfil_chegada]

    total_comparecimento = round(eleitores_aptos * taxa_comparecimento)
    duracao_segundos = duracao_minutos * 60.0

    tempo_1t_total = tempo_1t_segundos + tempo_biometria_segundos
    tempo_sem_ranq_total = tempo_sem_ranqueamento_segundos + tempo_biometria_segundos
    tempo_stv_enxuto_total = tempo_stv_enxuto_segundos + tempo_biometria_segundos
    tempo_com_ranq_total = tempo_com_ranqueamento_segundos + tempo_biometria_segundos

    res_1t = _simular_fila_unitaria(total_comparecimento, tempo_1t_total, duracao_segundos, perfil_norm)
    res_sem_ranq = _simular_fila_unitaria(total_comparecimento, tempo_sem_ranq_total, duracao_segundos, perfil_norm)
    res_stv_enxuto = _simular_fila_unitaria(total_comparecimento, tempo_stv_enxuto_total, duracao_segundos, perfil_norm)
    res_com_ranq = _simular_fila_unitaria(total_comparecimento, tempo_com_ranq_total, duracao_segundos, perfil_norm)

    return ResultadoFilasRT21(
        cenario_1t_atual=res_1t,
        cenario_rtp_sem_ranqueamento=res_sem_ranq,
        cenario_rtp_stv_enxuto=res_stv_enxuto,
        cenario_rtp_com_ranqueamento=res_com_ranq,
    )


# ===========================================================================
# RT-22: Comparecimento Heterogêneo entre UFs (U-03 / RT-22)
# ===========================================================================

@dataclass(frozen=True)
class ResultadoComparecimentoRT22:
    """Resultado do experimento de comparecimento heterogêneo entre UFs (RT-22 / U-03).

    Attributes:
        desvio_bancadas_uf: Desvio total absoluto das bancadas estaduais (rigorosamente 0).
        deslocamento_colunas: Total de cadeiras nacionais deslocadas entre colunas temáticas.
        cadeiras_colunas_homogeneo: Cadeiras das 9 colunas sob comparecimento homogêneo.
        cadeiras_colunas_heterogeneo: Cadeiras das 9 colunas sob comparecimento desigual.
        bancadas_uf_homogeneo: Bancada total de cada UF com comparecimento homogêneo.
        bancadas_uf_heterogeneo: Bancada total de cada UF com comparecimento desigual.
        diferenca_colunas: Diferença líquida por coluna {coluna: heterogeneo - homogeneo}.
    """

    desvio_bancadas_uf: int
    deslocamento_colunas: int
    cadeiras_colunas_homogeneo: dict[str, int]
    cadeiras_colunas_heterogeneo: dict[str, int]
    bancadas_uf_homogeneo: dict[str, int]
    bancadas_uf_heterogeneo: dict[str, int]
    diferenca_colunas: dict[str, int]


def simular_comparecimento_desigual_rt22(
    votos_base: Mapping[str, Mapping[str, int]] | None = None,
    ufs_com_2t: Sequence[str] | None = None,
    comparecimento_alto: float = 0.82,
    comparecimento_baixo: float = 0.55,
    comparecimento_base: float = 0.75,
) -> ResultadoComparecimentoRT22:
    """Simula o impacto de comparecimento heterogêneo entre UFs na data do 2º turno (RT-22).

    No Brasil, cerca de metade dos estados possui segundo turno para Governador de Estado,
    o que eleva o comparecimento local (`comparecimento_alto` = 0.82), enquanto nos estados
    com eleição executiva liquidada no 1º turno o comparecimento cai (`comparecimento_baixo` = 0.55).

    Comprova simultaneamente duas propriedades estruturais do modelo RTP:
      1. `desvio_bancadas_uf` = 0: Nenhuma bancada estadual perde ou ganha cadeiras no total
         federativo da Câmara, pois as margens estaduais $s_e$ são estritamente garantidas
         pelo Art. 45 da CF/88 no algoritmo biproporcional de Balinski-Demange.
      2. `deslocamento_colunas` > 0: As UFs com maior comparecimento exercem maior peso relativo
         na soma dos votos nacionais $V_c$, provocando modesto remanejamento no dimensionamento
         das colunas temáticas $h_c$.

    Args:
        votos_base: Matriz base de votos das 27 UFs x 9 colunas (opcional).
        ufs_com_2t: Lista de siglas das UFs com segundo turno estadual para governador.
        comparecimento_alto: Taxa de comparecimento nas UFs com 2º turno de governador (0.82).
        comparecimento_baixo: Taxa de comparecimento nas UFs sem 2º turno de governador (0.55).
        comparecimento_base: Taxa neutra de referência do cenário homogêneo (0.75).

    Returns:
        ResultadoComparecimentoRT22 comprovando desvio federativo zero e deslocamento temático.

    Raises:
        ValueError: Se as taxas forem negativas ou fora de [0.0, 1.0].
    """
    for nome, taxa in (
        ("comparecimento_alto", comparecimento_alto),
        ("comparecimento_baixo", comparecimento_baixo),
        ("comparecimento_base", comparecimento_base),
    ):
        if not (0.0 <= taxa <= 1.0):
            raise ValueError(f"A taxa '{nome}' deve estar no intervalo [0.0, 1.0]: {taxa}")

    if ufs_com_2t is None:
        ufs_com_2t = UFS_2T_GOVERNADOR_PADRAO
    set_2t = set(ufs_com_2t)

    ufs = sorted(BANCADAS_ESTADUAIS.keys())
    colunas_9 = tuple(COLUNAS_ESTADO + COLUNAS_PERMANENTES)

    # 1. Constrói votos homogêneos e heterogêneos com preferências temáticas distintas
    v_homog: dict[str, dict[str, int]] = {}
    v_heterog: dict[str, dict[str, int]] = {}

    for i, u in enumerate(ufs):
        bancada = BANCADAS_ESTADUAIS[u]
        tem_2t = u in set_2t
        mult = (comparecimento_alto / comparecimento_base) if tem_2t else (comparecimento_baixo / comparecimento_base)

        v_homog[u] = {}
        v_heterog[u] = {}
        for j, c in enumerate(colunas_9):
            if votos_base is not None and u in votos_base and c in votos_base[u]:
                base_val = votos_base[u][c]
            else:
                # UFs de 2T enfatizam Segurança e Agro; UFs sem 2T enfatizam Saúde e Educação
                pref = 1.15 if (tem_2t and c in ("C06_SEGURANCA", "C08_AGRO_AMBIENTE")) or (
                    not tem_2t and c in ("C04_SAUDE", "C05_EDUCACAO")
                ) else 0.95
                base_val = int(bancada * 50_000 * pref)

            v_homog[u][c] = base_val
            v_heterog[u][c] = max(100, int(base_val * mult))

    # 2. Alocação Homogênea
    v_col_hom = {c: sum(v_homog[u][c] for u in ufs) for c in colunas_9}
    cad_col_hom = {c: 60 for c in COLUNAS_ESTADO}
    cad_col_hom.update(
        alocar_sainte_lague(
            {c: v_col_hom[c] for c in COLUNAS_PERMANENTES},
            total_cadeiras=333,
            pisos={c: PISO_PERMANENTE for c in COLUNAS_PERMANENTES},
        )
    )
    res_hom = alocar_biproporcional(v_homog, BANCADAS_ESTADUAIS, cad_col_hom)

    # 3. Alocação Heterogênea
    v_col_het = {c: sum(v_heterog[u][c] for u in ufs) for c in colunas_9}
    cad_col_het = {c: 60 for c in COLUNAS_ESTADO}
    cad_col_het.update(
        alocar_sainte_lague(
            {c: v_col_het[c] for c in COLUNAS_PERMANENTES},
            total_cadeiras=333,
            pisos={c: PISO_PERMANENTE for c in COLUNAS_PERMANENTES},
        )
    )
    res_het = alocar_biproporcional(v_heterog, BANCADAS_ESTADUAIS, cad_col_het)

    bancadas_hom = {u: sum(res_hom.matriz[u].values()) for u in ufs}
    bancadas_het = {u: sum(res_het.matriz[u].values()) for u in ufs}

    desvio_bancadas = sum(abs(bancadas_het[u] - BANCADAS_ESTADUAIS[u]) for u in ufs)
    deslocamento_colunas = sum(abs(cad_col_het[c] - cad_col_hom[c]) for c in colunas_9) // 2
    diferenca_col = {c: cad_col_het[c] - cad_col_hom[c] for c in colunas_9}

    return ResultadoComparecimentoRT22(
        desvio_bancadas_uf=desvio_bancadas,
        deslocamento_colunas=deslocamento_colunas,
        cadeiras_colunas_homogeneo=cad_col_hom,
        cadeiras_colunas_heterogeneo=cad_col_het,
        bancadas_uf_homogeneo=bancadas_hom,
        bancadas_uf_heterogeneo=bancadas_het,
        diferenca_colunas=diferenca_col,
    )


# ===========================================================================
# RT-23: Atraso de Totalização Nacional (U-08 / RT-23)
# ===========================================================================

@dataclass(frozen=True)
class ResultadoAtrasoRT23:
    """Resultado do experimento de sensibilidade a urnas pendentes da apuração (RT-23 / U-08).

    Attributes:
        cadeiras_alteradas: Total de assentos na matriz (513) que mudam com os últimos votos.
        colunas_alteradas: Número de colunas que tiveram seu tamanho nacional h_c modificado.
        colunas_parcial: Tamanho nacional das colunas com apuração incompleta (ex: 98%).
        colunas_final: Tamanho nacional definitivo das colunas com 100% apurado.
        deslocamento_nacional_colunas: Cadeiras nacionais deslocadas entre temas no final.
        ufs_afetadas: Lista das UFs onde ao menos uma cadeira mudou de coluna temática.
    """

    cadeiras_alteradas: int
    colunas_alteradas: int
    colunas_parcial: dict[str, int]
    colunas_final: dict[str, int]
    deslocamento_nacional_colunas: int
    ufs_afetadas: list[str]


def simular_atraso_totalizacao_rt23(
    votos_finais: Mapping[str, Mapping[str, int]] | None = None,
    fracao_pendente: float = 0.02,
    ufs_remotas: Sequence[str] | None = None,
) -> ResultadoAtrasoRT23:
    """Mede a sensibilidade da alocação biproporcional ao atraso de urnas remotas (RT-23).

    Nas eleições brasileiras, urnas de regiões fluviais ou remotas da Amazônia Legal
    (AC, AM, AP, RR) chegam com algumas horas de atraso à totalização do TSE.
    Este experimento simula a estabilidade da projeção parlamentar quando uma
    fração pendente (padrão 2% dos votos nacionais) ainda não foi processada,
    comparando a matriz preliminar com o resultado final consolidado.

    Args:
        votos_finais: Matriz completa de votos de 27 UFs x 9 colunas (100% apurado).
        fracao_pendente: Proporção de votos nacionais ainda não totalizados (padrão 0.02 = 2%).
        ufs_remotas: UFs onde a pendência de apuração está concentrada (padrão Norte: AC, AM, AP, RR).

    Returns:
        ResultadoAtrasoRT23 detalhando colunas, cadeiras alteradas e UFs afetadas.

    Raises:
        ValueError: Se fracao_pendente não estiver contida em [0.0, 1.0).
    """
    if not (0.0 <= fracao_pendente < 1.0):
        raise ValueError(f"Fração pendente deve estar em [0.0, 1.0): {fracao_pendente}")

    if votos_finais is None:
        votos_finais = gerar_matriz_votos_base_27x9()

    if ufs_remotas is None:
        ufs_remotas = UFS_REMOTAS_PADRAO

    ufs = sorted(BANCADAS_ESTADUAIS.keys())
    colunas_9 = tuple(COLUNAS_ESTADO + COLUNAS_PERMANENTES)

    for u in ufs_remotas:
        if u not in votos_finais:
            raise ValueError(f"UF remota '{u}' não encontrada no mapa de votos.")

    # 1. Totalização Final (100% dos votos)
    v_col_fin = {c: sum(votos_finais[u][c] for u in ufs) for c in colunas_9}
    cad_col_fin = {c: 60 for c in COLUNAS_ESTADO}
    cad_col_fin.update(
        alocar_sainte_lague(
            {c: v_col_fin[c] for c in COLUNAS_PERMANENTES},
            total_cadeiras=333,
            pisos={c: PISO_PERMANENTE for c in COLUNAS_PERMANENTES},
        )
    )
    res_final = alocar_biproporcional(votos_finais, BANCADAS_ESTADUAIS, cad_col_fin)

    # 2. Totalização Parcial (com fracao_pendente concentrada nas UFs remotas)
    total_votos_pais = sum(votos_finais[u][c] for u in ufs for c in colunas_9)
    votos_pendentes = int(total_votos_pais * fracao_pendente)

    votos_remotas = sum(votos_finais[u][c] for u in ufs_remotas for c in colunas_9)
    fator_reducao_remoto = min(0.90, votos_pendentes / max(1, votos_remotas))

    votos_parcial: dict[str, dict[str, int]] = {u: dict(votos_finais[u]) for u in ufs}
    for u in ufs_remotas:
        for c in colunas_9:
            votos_parcial[u][c] = max(10, int(votos_finais[u][c] * (1.0 - fator_reducao_remoto)))

    v_col_par = {c: sum(votos_parcial[u][c] for u in ufs) for c in colunas_9}
    cad_col_par = {c: 60 for c in COLUNAS_ESTADO}
    cad_col_par.update(
        alocar_sainte_lague(
            {c: v_col_par[c] for c in COLUNAS_PERMANENTES},
            total_cadeiras=333,
            pisos={c: PISO_PERMANENTE for c in COLUNAS_PERMANENTES},
        )
    )
    res_parcial = alocar_biproporcional(votos_parcial, BANCADAS_ESTADUAIS, cad_col_par)

    colunas_alteradas = sum(1 for c in colunas_9 if cad_col_par[c] != cad_col_fin[c])
    deslocamento_colunas = sum(abs(cad_col_par[c] - cad_col_fin[c]) for c in colunas_9) // 2
    cadeiras_alteradas = sum(
        abs(res_parcial.matriz[u][c] - res_final.matriz[u][c])
        for u in ufs
        for c in colunas_9
    ) // 2

    ufs_afetadas = sorted(
        u for u in ufs
        if any(res_parcial.matriz[u][c] != res_final.matriz[u][c] for c in colunas_9)
    )

    return ResultadoAtrasoRT23(
        cadeiras_alteradas=cadeiras_alteradas,
        colunas_alteradas=colunas_alteradas,
        colunas_parcial=cad_col_par,
        colunas_final=cad_col_fin,
        deslocamento_nacional_colunas=deslocamento_colunas,
        ufs_afetadas=ufs_afetadas,
    )
