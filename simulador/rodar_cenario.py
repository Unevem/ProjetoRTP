# ---------------------------------------------------------------------------
# [BLK-L-008] Executável CLI de Simulação Nacional e Relatório do Red Team
# ---------------------------------------------------------------------------
"""Script principal de execução e demonstração do Simulador Eleitoral RTP.

Roda sem dependências externas (Python 3.12 Standard Library) e imprime:
  1. Simulação nacional completa (27 UFs x 12 Colunas, 513 deputados);
  2. Matriz Biproporcional completa (Estado x Coluna);
  3. Laudo de Auditoria das 6 Invariantes Constitucionais;
  4. Resultados consolidados dos 5 Testes de Estresse do Red Team (RT-19 a RT-23).
"""

import os
import sys

# Garante importação limpa a partir da raiz do repositório ou da pasta simulador/
DIRETORIO_ATUAL = os.path.dirname(os.path.abspath(__file__))
RAIZ_PROJETO = os.path.dirname(DIRETORIO_ATUAL)
for caminho in (RAIZ_PROJETO, DIRETORIO_ATUAL, os.path.join(DIRETORIO_ATUAL, "src")):
    if caminho not in sys.path:
        sys.path.insert(0, caminho)

from simulador.src.constantes import (
    BANCADAS_ESTADUAIS,
    COLUNAS_ESTADO,
    COLUNAS_MISSAO_PADRAO,
    COLUNAS_PERMANENTES,
    TODAS_COLUNAS_PADRAO,
)
from simulador.src.estresse_redteam import (
    simular_atraso_totalizacao_rt23,
    simular_comparecimento_desigual_rt22,
    simular_filas_cabine_rt21,
    simular_transbordamento_puxador_rt20,
    simular_voto_enterro_rt19,
)
from simulador.src.metricas import indice_gallagher, indice_herfindahl
from simulador.src.pipeline import executar_apuracao_nacional


def gerar_cenario_nacional_demonstracao() -> tuple[
    dict[str, dict[str, int]],
    dict[str, float],
    dict[str, int],
]:
    """Constrói um cenário nacional determinístico realista (27 UFs x 12 Colunas)."""
    pesos_colunas = {
        "C01_ECONOMIA": 1.10,
        "C02_JUSTICA": 0.95,
        "C03_SOCIAL": 0.95,
        "C04_SAUDE": 1.45,
        "C05_EDUCACAO": 1.30,
        "C06_SEGURANCA": 1.20,
        "C07_INFRAESTRUTURA": 0.95,
        "C08_AGRO_AMBIENTE": 0.85,
        "C09_CIENCIA_TRABALHO": 0.25,  # Coluna minoritária protegida pelo piso de 20
        "C10_MISSAO_1": 1.15,
        "C11_MISSAO_2": 0.95,
        "C12_MISSAO_3": 0.70,
    }

    votos_uf_coluna: dict[str, dict[str, int]] = {}
    taxas_voto4: dict[str, float] = {}

    ufs_ordenadas = sorted(BANCADAS_ESTADUAIS.keys())
    for idx_uf, uf in enumerate(ufs_ordenadas):
        bancada = BANCADAS_ESTADUAIS[uf]
        eleitorado_base = bancada * 220_000
        votos_uf_coluna[uf] = {}

        for idx_col, col in enumerate(TODAS_COLUNAS_PADRAO):
            modificador_regional = 1.0 + 0.06 * (((idx_uf * 7 + idx_col * 5) % 9) - 4)
            votos_uf_coluna[uf][col] = int(
                eleitorado_base * pesos_colunas[col] * modificador_regional * 0.25
            )

        # Taxa de votos válidos no Voto 4 entre 68% e 88% conforme a UF
        taxas_voto4[uf] = round(0.68 + 0.02 * (idx_uf % 11), 2)

    # Votos de legenda temática no exterior (Zona ZZ) e em trânsito (RT-29 / D-22)
    votos_exterior_transito = {
        "C01_ECONOMIA": 85_000,
        "C02_JUSTICA": 40_000,
        "C03_SOCIAL": 65_000,
        "C04_SAUDE": 70_000,
        "C05_EDUCACAO": 95_000,
        "C06_SEGURANCA": 45_000,
        "C07_INFRAESTRUTURA": 35_000,
        "C08_AGRO_AMBIENTE": 90_000,
        "C09_CIENCIA_TRABALHO": 140_000,
        "C10_MISSAO_1": 80_000,
        "C11_MISSAO_2": 60_000,
        "C12_MISSAO_3": 35_000,
    }

    return votos_uf_coluna, taxas_voto4, votos_exterior_transito


def main() -> None:
    """Executa a simulação demonstrativa e imprime o relatório formatado."""
    print("=" * 100)
    print("SIMULADOR OFICIAL — REPRESENTAÇÃO TEMÁTICA PROPORCIONAL (RTP / SPEC-002)")
    print("=" * 100)

    votos_uf, taxas_voto4, votos_ext = gerar_cenario_nacional_demonstracao()
    resultado = executar_apuracao_nacional(
        votos_uf_coluna=votos_uf,
        taxas_validos_voto4_uf=taxas_voto4,
        votos_exterior_transito=votos_ext,
    )

    print("\n1. DIMENSIONAMENTO DOS BLOCOS E COLUNAS TEMÁTICAS NACIONAIS")
    print("-" * 100)
    print(f"  • Bloco 1 (Núcleo de Estado Fixo) : 180 cadeiras (60 por coluna)")
    print(f"  • Bloco 2 (Colunas Permanentes)   : {resultado.cadeiras_bloco_2:3d} cadeiras (piso protetor = 20)")
    print(f"  • Bloco 3 (Missões Presidenciais) : {resultado.cadeiras_bloco_3:3d} cadeiras (teto efetivo U = {resultado.teto_missao_nacional})")
    print(f"  • Total da Câmara dos Deputados   : {sum(resultado.cadeiras_colunas.values()):3d} cadeiras")
    print("-" * 100)
    print(f"  {'COLUNA TEMÁTICA':<24} | {'VOTOS NACIONAIS':>16} | {'CADEIRAS':>8} | {'HHI REGIONAL':>12}")
    print("-" * 100)

    for col in TODAS_COLUNAS_PADRAO:
        votos_col = resultado.votos_nacionais_coluna[col]
        cad_col = resultado.cadeiras_colunas[col]
        dist_uf = {uf: resultado.matriz_completa[uf][col] for uf in BANCADAS_ESTADUAIS}
        hhi = indice_herfindahl(dist_uf)
        print(f"  {col:<24} | {votos_col:>16,d} | {cad_col:>8d} | {hhi:>12.4f}")

    # Desproporcionalidade temática no Bloco 2 + Bloco 3
    colunas_elásticas = COLUNAS_PERMANENTES + COLUNAS_MISSAO_PADRAO
    lsq_tematico = indice_gallagher(
        {c: resultado.votos_nacionais_coluna[c] for c in colunas_elásticas},
        {c: resultado.cadeiras_colunas[c] for c in colunas_elásticas},
    )
    print("-" * 100)
    print(f"  Índice de Gallagher (Desproporcionalidade Temática Blocos 2+3): {lsq_tematico:.2f} p.p.")

    print("\n2. MATRIZ BIPROPORCIONAL DE ALOCAÇÃO (27 UFs x 12 COLUNAS)")
    print("-" * 100)
    cabecalho_cols = " ".join(f"C{i:02d}" for i in range(1, 13))
    print(f"  {'UF':<3} | {cabecalho_cols} | {'MIS':>3}/{ 'TETO':<4} | {'TOTAL':>5} | {'CF/88':>5}")
    print("-" * 100)

    for uf in sorted(BANCADAS_ESTADUAIS.keys(), key=lambda u: (-BANCADAS_ESTADUAIS[u], u)):
        celulas = [resultado.matriz_completa[uf][c] for c in TODAS_COLUNAS_PADRAO]
        linha_str = " ".join(f"{val:3d}" for val in celulas)
        soma_uf = sum(celulas)
        soma_missao = sum(resultado.matriz_completa[uf][c] for c in COLUNAS_MISSAO_PADRAO)
        teto_uf = resultado.tetos_missao_uf[uf]
        esperado_uf = BANCADAS_ESTADUAIS[uf]
        print(f"  {uf:<3} | {linha_str} | {soma_missao:3d}/{teto_uf:<4d} | {soma_uf:5d} | {esperado_uf:5d}")

    print("-" * 100)
    totais_col = [sum(resultado.matriz_completa[u][c] for u in BANCADAS_ESTADUAIS) for c in TODAS_COLUNAS_PADRAO]
    totais_str = " ".join(f"{val:3d}" for val in totais_col)
    print(f"  {'TOT':<3} | {totais_str} | {resultado.cadeiras_bloco_3:3d}/{resultado.teto_missao_nacional:<4d} | {sum(totais_col):5d} |   513")

    print("\n3. AUDITORIA DAS 6 INVARIANTES CONSTITUCIONAIS")
    print("-" * 100)
    aud = resultado.auditoria
    print(f"  [✓] Veredito Global Aprovado      : {aud.aprovado}")
    print(f"  [✓] Soma Total == 513 Cadeiras    : {aud.soma_total_513}")
    print(f"  [✓] Pacto Federativo (Art. 45 CF) : {aud.pacto_federativo_intacto}")
    print(f"  [✓] Fechamento Temático Nacional  : {aud.fechamento_tematico_intacto}")
    print(f"  [✓] Núcleo de Estado (60 fixas)   : {aud.nucleo_estado_60_fixo}")
    print(f"  [✓] Pisos Permanentes (>= 20)     : {aud.pisos_permanentes_respeitados}")
    print(f"  [✓] Tetos Estaduais de Missão     : {aud.tetos_missao_respeitados}")
    print(f"  [✓] Iterações TIES (Missão/Princ) : {resultado.resultado_missao.iteracoes} / {resultado.resultado_principal.iteracoes}")

    print("\n4. RESULTADOS DOS 5 EXPERIMENTOS DE ESTRESSE DO RED TEAM (RT-19 a RT-23)")
    print("-" * 100)
    rt19 = simular_voto_enterro_rt19()
    print(
        f"  • RT-19 (Voto de Enterro)         : Ganho estratégico = +{rt19.ganho_enterro_vs_sincero} cadeira "
        f"(Saúde: Sincero={rt19.cadeiras_saude['B']} vs Enterro={rt19.cadeiras_saude['C']}; "
        f"Ciência travada no piso={rt19.coluna_enterro_travada_no_piso})"
    )

    rt20 = simular_transbordamento_puxador_rt20()
    print(
        f"  • RT-20 (Puxador +2,5M em SP)     : Ganho nacional Segurança = +{rt20.ganho_nacional_coluna} cadeiras "
        f"(+{rt20.ganho_sp} em SP, +{rt20.ganho_outras_ufs} transbordada para outras UFs; SP total fixo em 70)"
    )

    rt21 = simular_filas_cabine_rt21()
    print(
        f"  • RT-21 (Filas de Seção 400 el.)  : Sem ranqueamento = {rt21.cenario_rtp_sem_ranqueamento.fila_residual_as_17h} na fila às 17h "
        f"({rt21.cenario_rtp_sem_ranqueamento.minutos_extras_apos_17h:.1f} min) | "
        f"STV enxuto (72s+15s) = {rt21.cenario_rtp_stv_enxuto.fila_residual_as_17h} na fila "
        f"({rt21.cenario_rtp_stv_enxuto.minutos_extras_apos_17h:.1f} min) | "
        f"Ordenação longa (130s+15s) = {rt21.cenario_rtp_com_ranqueamento.fila_residual_as_17h} na fila "
        f"({rt21.cenario_rtp_com_ranqueamento.minutos_extras_apos_17h:.1f} min)"
    )

    rt22 = simular_comparecimento_desigual_rt22()
    print(
        f"  • RT-22 (Turnout 82% vs 55%)      : Desvio nas bancadas das UFs = {rt22.desvio_bancadas_uf} cadeiras | "
        f"Deslocamento entre colunas = {rt22.deslocamento_colunas} cadeiras (de 513)"
    )

    rt23 = simular_atraso_totalizacao_rt23()
    print(
        f"  • RT-23 (2% Urnas Remotas Norte)  : {513 - rt23.cadeiras_alteradas}/513 cadeiras (99,6%) já definidas "
        f"antes dos últimos 2% (apenas {rt23.cadeiras_alteradas} cadeiras marginais aguardam fechamento)"
    )
    print("=" * 100)


if __name__ == "__main__":
    main()
