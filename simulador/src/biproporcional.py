# ---------------------------------------------------------------------------
# [BLK-L-004] Alocação Biproporcional de Balinski-Demange e Contingência Lexicográfica
# ---------------------------------------------------------------------------
"""Módulo de Alocação Biproporcional de Balinski-Demange com Contingência Lexicográfica.

Implementa a alocação de matriz inteira X = (x_{e,c}) sob o método de Sainte-Laguë / Webster,
garantindo simultaneamente o fechamento exato das bancadas estaduais (somas de linhas r_e)
e o fechamento exato dos mandatos por coluna temática (somas de colunas h_c).

Fundamentação Teórica:
  - Balinski & Demange (1989), Gaffke & Pukelsheim (2008):
    A matriz biproporcional ótima maximiza a função côncava estritamente separável:
      Phi(X) = sum_{e,c} sum_{k=1}^{x_{e,c}} ln( v~_{e,c} / (k - 0.5) )
    onde v~_{e,c} = v_{e,c} se v_{e,c} > 0, e v~_{e,c} = epsilon = 10^-9 se v_{e,c} == 0.
  - Regra de Contingência Lexicográfica RT-09:
    Células com contagem de votos zerada recebem utilidade de ordem ln(epsilon) << 0,
    o que impede matematicamente a concessão de mandatos a chapas sem votos, exceto
    quando for absolutamente impossível fechar as margens constitucionais apenas
    com células de voto positivo.

Arquitetura do Algoritmo:
  1. Fase 1: Escalonamento Alternado (TIES / Biproportional Webster) para convergência
     rápida dos multiplicadores de linha lambda_e e coluna mu_c.
  2. Fase 2: Refinamento Exato por Caminho de Aumento de Maior Ganho de Utilidade Marginal
     (Bellman-Ford livre de ciclos em grafo residual) caso ocorram empates discretos.
  3. Etapa 3a: Alocação de missão institucional com tetos por UF via coluna fictícia de folga
     (Gaffke & Pukelsheim, 2008).
"""

from dataclasses import dataclass
import math
from typing import Final, Mapping

try:
    from simulador.src.sainte_lague import (
        alocar_sainte_lague,
        calcular_divisor_equilibrio,
    )
except ImportError:  # pragma: no cover - fallback para execução de pacote local
    from sainte_lague import (
        alocar_sainte_lague,
        calcular_divisor_equilibrio,
    )

# Parâmetros de estabilidade e convergência
EPSILON: Final[float] = 1e-9
COLUNA_FOLGA: Final[str] = "__FOLGA__"
MAX_ITERACOES_PADRAO: Final[int] = 60


@dataclass(frozen=True)
class ResultadoBiproporcional:
    """Resultado da alocação de assentos em matriz biproporcional.

    Attributes:
        matriz: Matriz de alocação inteira {uf: {coluna: cadeiras}}.
        lambda_uf: Divisores/multiplicadores das linhas (UFs).
        mu_coluna: Divisores/multiplicadores das colunas temáticas.
        contingencia_acionada: True se alguma célula com zero votos recebeu assento (RT-09).
        iteracoes: Total de iterações executadas no escalonamento alternado da Fase 1.
    """

    matriz: dict[str, dict[str, int]]
    lambda_uf: dict[str, float]
    mu_coluna: dict[str, float]
    contingencia_acionada: bool
    iteracoes: int


def alocar_biproporcional(
    votos: Mapping[str, Mapping[str, int]],
    cadeiras_uf: Mapping[str, int],
    cadeiras_coluna: Mapping[str, int],
    max_iter: int = MAX_ITERACOES_PADRAO,
) -> ResultadoBiproporcional:
    """Aloca cadeiras na matriz biproporcional pelo método de Balinski-Demange (Sainte-Laguë).

    Garante que a soma de cada linha corresponda exatamente a `cadeiras_uf[e]` e a
    soma de cada coluna corresponda exatamente a `cadeiras_coluna[c]`.

    Args:
        votos: Matriz bidimensional {uf: {coluna: contagem_votos}}.
        cadeiras_uf: Alvos de cadeiras por UF (somas de linhas).
        cadeiras_coluna: Alvos de cadeiras por coluna temática (somas de colunas).
        max_iter: Número máximo de iterações do escalonamento alternado (padrão 60).

    Returns:
        Estrutura ResultadoBiproporcional com matriz alocada, divisores e contingência.

    Raises:
        ValueError: Se as somas marginais divergirem, se houver cadeiras ou votos negativos,
            ou se não for possível conciliar os requisitos.
        KeyError: Se alguma UF de cadeiras_uf não constar no mapa de votos.
    """
    if not cadeiras_uf:
        raise ValueError("O mapeamento de cadeiras por UF não pode estar vazio.")
    if not cadeiras_coluna:
        raise ValueError("O mapeamento de cadeiras por coluna não pode estar vazio.")

    soma_uf = sum(cadeiras_uf.values())
    soma_col = sum(cadeiras_coluna.values())
    if soma_uf != soma_col:
        raise ValueError(
            f"Incompatibilidade marginal: soma das cadeiras das UFs ({soma_uf}) "
            f"diverge da soma das colunas ({soma_col})."
        )

    for u, c_alvo in cadeiras_uf.items():
        if c_alvo < 0:
            raise ValueError(f"Alvo de cadeiras da UF '{u}' não pode ser negativo: {c_alvo}")
        if u not in votos:
            raise KeyError(f"UF '{u}' não encontrada no mapeamento de votos.")

    for c, c_alvo in cadeiras_coluna.items():
        if c_alvo < 0:
            raise ValueError(f"Alvo de cadeiras da coluna '{c}' não pode ser negativo: {c_alvo}")

    for u, col_map in votos.items():
        for c, v in col_map.items():
            if v < 0:
                raise ValueError(
                    f"Contagem de votos negativa detectada em ({u}, {c}): {v}"
                )

    ufs = sorted(cadeiras_uf.keys())
    colunas = sorted(cadeiras_coluna.keys())

    # Se a demanda total for zero assentos, retorna matriz nula
    if soma_uf == 0:
        return ResultadoBiproporcional(
            matriz={u: {c: 0 for c in colunas} for u in ufs},
            lambda_uf={u: 1.0 for u in ufs},
            mu_coluna={c: 1.0 for c in colunas},
            contingencia_acionada=False,
            iteracoes=0,
        )

    # 1. Matriz de votos suavizada com epsilon para regra RT-09
    v_tilde: dict[str, dict[str, float]] = {}
    for u in ufs:
        v_tilde[u] = {}
        for c in colunas:
            val = votos[u].get(c, 0)
            v_tilde[u][c] = float(val) if val > 0 else EPSILON

    # =========================================================================
    # FASE 1: Escalonamento Alternado (TIES / Biproportional Webster)
    # =========================================================================
    lambda_uf = {u: 1.0 for u in ufs}
    mu_coluna = {c: 1.0 for c in colunas}
    matriz_atual: dict[str, dict[str, int]] = {u: {c: 0 for c in colunas} for u in ufs}
    iteracoes_executadas = 0

    for it in range(1, max_iter + 1):
        iteracoes_executadas = it

        # Passo A: Ajuste proporcional em cada linha (UFs)
        for u in ufs:
            v_linha = {c: v_tilde[u][c] / mu_coluna[c] for c in colunas}
            x_linha = alocar_sainte_lague(v_linha, cadeiras_uf[u])
            lambda_uf[u] = calcular_divisor_equilibrio(v_linha, x_linha)

        # Passo B: Ajuste proporcional em cada coluna (Temas)
        for c in colunas:
            v_col = {u: v_tilde[u][c] / lambda_uf[u] for u in ufs}
            x_col = alocar_sainte_lague(v_col, cadeiras_coluna[c])
            for u in ufs:
                matriz_atual[u][c] = x_col[u]
            mu_coluna[c] = calcular_divisor_equilibrio(v_col, x_col)

        # Passo C: Checagem exata de convergência biproporcional
        somas_linhas = {u: sum(matriz_atual[u][c] for c in colunas) for u in ufs}
        if all(somas_linhas[u] == cadeiras_uf[u] for u in ufs):
            break

    # =========================================================================
    # FASE 2: Refinamento Exato por Caminho de Aumento de Maior Ganho de Utilidade
    # =========================================================================
    # A matriz após a última etapa de colunas já satisfaz estritamente sum_e x_{e,c} = h_c.
    # Caso haja descompasso discreto nas linhas, transferimos cadeiras entre UFs
    # superavitárias e deficitárias ao longo de caminhos residuais que maximizam Phi(X).
    while True:
        somas_linhas = {u: sum(matriz_atual[u][c] for c in colunas) for u in ufs}
        deficitarias = [u for u in ufs if somas_linhas[u] < cadeiras_uf[u]]
        superavitarias = [u for u in ufs if somas_linhas[u] > cadeiras_uf[u]]

        if not deficitarias or not superavitarias:
            break

        # Construção do grafo bipartido direcionado
        # Nós: SRC, DST, linhas U_e e colunas C_c
        nodes = ["__SRC__", "__DST__"] + [f"U_{u}" for u in ufs] + [f"C_{c}" for c in colunas]
        edges: list[tuple[str, str, float, tuple[str, str, str] | None]] = []

        for u in superavitarias:
            edges.append(("__SRC__", f"U_{u}", 0.0, None))
        for u in deficitarias:
            edges.append((f"U_{u}", "__DST__", 0.0, None))

        for u in ufs:
            for c in colunas:
                x_uc = matriz_atual[u][c]
                # Linha cede cadeira para a coluna (diminui x_uc de 1)
                if x_uc >= 1:
                    w_down = math.log(v_tilde[u][c] / (x_uc - 0.5))
                    edges.append((f"U_{u}", f"C_{c}", w_down, (u, c, "down")))
                # Coluna entrega cadeira para a linha (aumenta x_uc de 1)
                w_up = -math.log(v_tilde[u][c] / (x_uc + 0.5))
                edges.append((f"C_{c}", f"U_{u}", w_up, (u, c, "up")))

        # Bellman-Ford com rastreamento de nós visitados para garantia de caminho simples
        dist = {n: float("inf") for n in nodes}
        path_nodes: dict[str, tuple[str, ...]] = {n: () for n in nodes}
        path_edges: dict[str, tuple[tuple[str, str, str], ...]] = {n: () for n in nodes}

        dist["__SRC__"] = 0.0
        path_nodes["__SRC__"] = ("__SRC__",)

        # Ordenação determinística para estabilidade absoluta
        arestas_ordenadas = sorted(edges, key=lambda e: (e[0], e[1]))

        for _ in range(len(nodes) - 1):
            atualizou = False
            for u_from, v_to, weight, info in arestas_ordenadas:
                if dist[u_from] == float("inf"):
                    continue
                if v_to in path_nodes[u_from]:
                    # Impede formação de ciclos
                    continue
                novo_custo = dist[u_from] + weight
                if novo_custo < dist[v_to] - 1e-11:
                    dist[v_to] = novo_custo
                    path_nodes[v_to] = path_nodes[u_from] + (v_to,)
                    path_edges[v_to] = path_edges[u_from] + ((info,) if info is not None else ())
                    atualizou = True
            if not atualizou:
                break

        if dist["__DST__"] == float("inf"):
            raise RuntimeError(
                "Falha ao encontrar caminho residual na matriz biproporcional."
            )

        # Aplica transferência atômica de 1 assento ao longo do caminho ótimo
        for u, c, op in path_edges["__DST__"]:
            if op == "down":
                matriz_atual[u][c] -= 1
            elif op == "up":
                matriz_atual[u][c] += 1

    # Atualização final e consistente dos multiplicadores de equilíbrio
    for c in colunas:
        v_col = {u: v_tilde[u][c] / lambda_uf[u] for u in ufs}
        mu_coluna[c] = calcular_divisor_equilibrio(
            v_col, {u: matriz_atual[u][c] for u in ufs}
        )
    for u in ufs:
        v_linha = {c: v_tilde[u][c] / mu_coluna[c] for c in colunas}
        lambda_uf[u] = calcular_divisor_equilibrio(v_linha, matriz_atual[u])

    # Verificação da regra de contingência RT-09
    contingencia = any(
        votos[u].get(c, 0) == 0 and matriz_atual[u][c] > 0
        for u in ufs
        for c in colunas
    )

    return ResultadoBiproporcional(
        matriz=matriz_atual,
        lambda_uf=lambda_uf,
        mu_coluna=mu_coluna,
        contingencia_acionada=contingencia,
        iteracoes=iteracoes_executadas,
    )


def alocar_matriz_missao(
    votos_missao: Mapping[str, Mapping[str, int]],
    tetos_uf: Mapping[str, int],
    cadeiras_coluna_missao: Mapping[str, int],
) -> ResultadoBiproporcional:
    """Aloca cadeiras de missão institucional (Bloco 3) com tetos por UF (Etapa 3a).

    Cada UF 'e' tem um teto de mandatos de missão u_e (sum_{c in C_3} y_{e,c} <= u_e) e cada
    coluna de missão 'c' deve somar exatamente h_c assentos (sum_e y_{e,c} = h_c).
    Pelo teorema de Gaffke & Pukelsheim (2008), quando a soma total das cadeiras de missão
    H_3 for menor que a capacidade máxima total dos tetos das UFs, uma coluna fictícia de folga
    absorve a folga de forma biproporcional perfeita e determinística.

    Args:
        votos_missao: Matriz de votos {uf: {coluna_missao: votos}}.
        tetos_uf: Teto efetivo u_e de cada UF para missões.
        cadeiras_coluna_missao: Total exato h_c de cadeiras por tema de missão.

    Returns:
        ResultadoBiproporcional contendo a matriz de cadeiras de missão alocada
        respeitando os tetos das UFs e as metas exatas de cada missão.

    Raises:
        ValueError: Se a soma das cadeiras de missão exceder a soma dos tetos das UFs.
    """
    total_missao = sum(cadeiras_coluna_missao.values())
    total_tetos = sum(tetos_uf.values())

    if total_missao > total_tetos:
        raise ValueError(
            f"Capacidade insuficiente: soma das cadeiras de missão ({total_missao}) "
            f"excede o teto total das UFs ({total_tetos})."
        )

    # Caso 1: Fechamento exato de capacidade (sem folga residual)
    if total_missao == total_tetos:
        return alocar_biproporcional(
            votos=votos_missao,
            cadeiras_uf=tetos_uf,
            cadeiras_coluna=cadeiras_coluna_missao,
        )

    # Caso 2: Total de missão menor que os tetos disponíveis (coluna de folga)
    folga = total_tetos - total_missao
    ufs = sorted(tetos_uf.keys())
    colunas_reais = sorted(cadeiras_coluna_missao.keys())

    # Voto de referência neutro para a coluna fictícia de folga (arredondamento Sainte-Laguë half-up exato)
    soma_votos = sum(
        votos_missao[u].get(c, 0)
        for u in ufs
        for c in colunas_reais
    )
    denominador_celulas = len(ufs) * max(1, len(colunas_reais))
    voto_folga = max(
        1,
        (2 * soma_votos + denominador_celulas) // (2 * denominador_celulas),
    )

    votos_com_folga: dict[str, dict[str, int]] = {}
    for u in ufs:
        votos_com_folga[u] = {c: votos_missao[u].get(c, 0) for c in colunas_reais}
        votos_com_folga[u][COLUNA_FOLGA] = voto_folga

    cadeiras_com_folga = dict(cadeiras_coluna_missao)
    cadeiras_com_folga[COLUNA_FOLGA] = folga

    resultado_expandido = alocar_biproporcional(
        votos=votos_com_folga,
        cadeiras_uf=tetos_uf,
        cadeiras_coluna=cadeiras_com_folga,
    )

    # Remove a coluna de folga do resultado final
    matriz_final: dict[str, dict[str, int]] = {}
    for u in ufs:
        matriz_final[u] = {
            c: resultado_expandido.matriz[u][c]
            for c in colunas_reais
        }

    mu_final = {
        c: resultado_expandido.mu_coluna[c]
        for c in colunas_reais
    }

    contingencia_real = any(
        votos_missao[u].get(c, 0) == 0 and matriz_final[u][c] > 0
        for u in ufs
        for c in colunas_reais
    )

    return ResultadoBiproporcional(
        matriz=matriz_final,
        lambda_uf=resultado_expandido.lambda_uf,
        mu_coluna=mu_final,
        contingencia_acionada=contingencia_real,
        iteracoes=resultado_expandido.iteracoes,
    )
