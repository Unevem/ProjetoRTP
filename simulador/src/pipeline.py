# ---------------------------------------------------------------------------
# [BLK-L-006] Pipeline de Apuração Nacional RTP e Alocação Intracelular (STV/Lista)
# ---------------------------------------------------------------------------
"""Pipeline completo de apuração nacional do Representação Temática Proporcional (RTP).

Orquestra todas as etapas de totalização eleitoral em conformidade com o desenho
institucional da SPEC-002 e as decisões deliberadas no Red Team:
  - Etapa 0: Totalização dos votos nacionais por coluna temátiva (incluindo exterior/trânsito, RT-29/D-22);
  - Etapa 1: Dimensionamento dos tetos de missão institucional por UF (RT-01, RT-04, D-13, D-15);
  - Etapa 2: Repartição das cadeiras nacionais entre blocos e colunas (Sainte-Laguë, D-08 a D-10);
  - Etapa 3: Alocação biproporcional de matrizes de missão (3a) e principal (3b) (D-11);
  - Etapa 4: Alocação intracelular por Voto Único Transferível / STV com preferências e voto
    de confiança da legenda (RT-03, RT-04, RT-16, D-12) e busca regional de suplência (RT-11, D-20).
"""

from dataclasses import dataclass, field
from fractions import Fraction
import math
from typing import Final, Mapping, Sequence

try:
    from simulador.src.biproporcional import (
        ResultadoBiproporcional,
        alocar_biproporcional,
        alocar_matriz_missao,
    )
    from simulador.src.constantes import (
        BANCADAS_ESTADUAIS,
        CADEIRAS_LIVRES,
        COLUNAS_ESTADO,
        COLUNAS_MISSAO_PADRAO,
        COLUNAS_PERMANENTES,
        MACRORREGIOES,
        PISO_GENERALISTA,
        PISO_PERMANENTE,
        RHO_TETO_MISSAO,
        TOTAL_CADEIRAS,
    )
    from simulador.src.metricas import (
        RelatorioInvariantes,
        auditar_invariantes_constitucionais,
    )
    from simulador.src.sainte_lague import alocar_sainte_lague
    from simulador.src.teto_missao import (
        arredondar_sainte_lague,
        calcular_tetos_nacionais,
    )
except ImportError:  # pragma: no cover - fallback para execução de pacote local
    from biproporcional import (
        ResultadoBiproporcional,
        alocar_biproporcional,
        alocar_matriz_missao,
    )
    from constantes import (
        BANCADAS_ESTADUAIS,
        CADEIRAS_LIVRES,
        COLUNAS_ESTADO,
        COLUNAS_MISSAO_PADRAO,
        COLUNAS_PERMANENTES,
        MACRORREGIOES,
        PISO_GENERALISTA,
        PISO_PERMANENTE,
        RHO_TETO_MISSAO,
        TOTAL_CADEIRAS,
    )
    from metricas import (
        RelatorioInvariantes,
        auditar_invariantes_constitucionais,
    )
    from sainte_lague import alocar_sainte_lague
    from teto_missao import (
        arredondar_sainte_lague,
        calcular_tetos_nacionais,
    )


@dataclass(frozen=True)
class ResultadoApuracaoNacional:
    """Resultado consolidado da apuração e totalização eleitoral nacional RTP.

    Attributes:
        votos_nacionais_coluna: Total nacional de votos de cada coluna V_c (incluindo exterior/trânsito).
        tetos_missao_uf: Teto efetivo u_e de cada bancada estadual para colunas de missão.
        teto_missao_nacional: Capacidade máxima agregada U = sum(u_e).
        cadeiras_bloco_3: Total nacional de assentos H_3 alocado às colunas de missão.
        cadeiras_bloco_2: Total nacional de assentos H_2 alocado às colunas permanentes.
        cadeiras_colunas: Distribuição de assentos h_c para todas as colunas da Câmara dos Deputados.
        resultado_missao: Alocação biproporcional da matriz de missão (Etapa 3a).
        resultado_principal: Alocação biproporcional da matriz principal de Estado e permanentes (Etapa 3b).
        matriz_completa: Matriz integrada final 27 UFs x |C| de deputados federais eleitos.
        auditoria: Relatório estrito de auditoria das 6 invariantes constitucionais.
    """

    votos_nacionais_coluna: dict[str, int]
    tetos_missao_uf: dict[str, int]
    teto_missao_nacional: int
    cadeiras_bloco_3: int
    cadeiras_bloco_2: int
    cadeiras_colunas: dict[str, int]
    resultado_missao: ResultadoBiproporcional
    resultado_principal: ResultadoBiproporcional
    matriz_completa: dict[str, dict[str, int]]
    auditoria: RelatorioInvariantes


@dataclass(frozen=True)
class CandidatoCelula:
    """Registro de votos nominais e preferências de um candidato na célula (UF x Coluna).

    Attributes:
        id_candidato: Identificador único do candidato.
        partido: Sigla partidária ou federação do candidato.
        votos_primeira: Votação nominal direta de 1ª preferência na urna.
        votos_segunda: Menções registradas em 2ª preferência (RT-16).
        votos_terceira: Menções registradas em 3ª preferência.
    """

    id_candidato: str
    partido: str
    votos_primeira: int
    votos_segunda: int = 0
    votos_terceira: int = 0


@dataclass(frozen=True)
class ResultadoCelula:
    """Resultado da apuração intracelular por voto preferencial transferível (STV).

    Attributes:
        eleitos: Lista ordenada com os identificadores dos candidatos eleitos na célula.
        suplentes_celula: Lista dos não eleitos ordenados por votação/pontuação final para suplência.
        cadeiras_por_partido: Mapeamento {partido: cadeiras_conquistadas}.
        cota_droop: Cota eleitoral de Droop calculada para a disputa na célula.
    """

    eleitos: list[str]
    suplentes_celula: list[str]
    cadeiras_por_partido: dict[str, int]
    cota_droop: int


def executar_apuracao_nacional(
    votos_uf_coluna: Mapping[str, Mapping[str, int]],
    taxas_validos_voto4_uf: Mapping[str, float],
    votos_exterior_transito: Mapping[str, int] | None = None,
    bancadas_uf: Mapping[str, int] = BANCADAS_ESTADUAIS,
    colunas_estado: tuple[str, ...] = COLUNAS_ESTADO,
    colunas_permanentes: tuple[str, ...] = COLUNAS_PERMANENTES,
    colunas_missao: tuple[str, ...] = COLUNAS_MISSAO_PADRAO,
    piso_generalista: int = PISO_GENERALISTA,
    piso_permanente: int = PISO_PERMANENTE,
    rho_missao: float = RHO_TETO_MISSAO,
) -> ResultadoApuracaoNacional:
    """Executa a apuração e totalização completa do modelo RTP das Etapas 0 a 3.

    Orquestra a contagem de sufrágios, dimensionamento de tetos de missão, distribuição
    de cadeiras nacionais por Sainte-Laguë e o duplo escalonamento biproporcional de
    Balinski-Demange (matriz de missão e matriz principal), gerando a auditoria constitucional.

    Args:
        votos_uf_coluna: Matriz {uf: {coluna: votos}} de votos nominais e temáticos computados.
        taxas_validos_voto4_uf: Taxa a_e [0.0, 1.0] de votos válidos no Voto 4 por UF.
        votos_exterior_transito: Votos de legenda temática exterior (ZZ) e trânsito (RT-29/D-22).
        bancadas_uf: Bancadas constitucionais de deputados por Estado (Art. 45 da CF/88).
        colunas_estado: Identificadores das colunas generalistas do Bloco 1 (padrão C01 a C03).
        colunas_permanentes: Identificadores das colunas permanentes do Bloco 2 (padrão C04 a C09).
        colunas_missao: Identificadores das colunas prioritárias de missão do Bloco 3.
        piso_generalista: Cadeiras fixas por coluna de Estado (padrão 60).
        piso_permanente: Piso mínimo por coluna temática permanente (padrão 20).
        rho_missao: Percentual máximo para cálculo de tau_e de missão (padrão 0.20).

    Returns:
        ResultadoApuracaoNacional consolidado e auditado.

    Raises:
        ValueError: Se houver dados marginais inconsistentes, contagens negativas ou tetos violados.
        KeyError: Se alguma UF das bancadas não for localizada nos mapas de votos ou taxas.
    """
    if not bancadas_uf:
        raise ValueError("O mapeamento de bancadas estaduais não pode estar vazio.")

    todas_colunas = colunas_estado + colunas_permanentes + colunas_missao

    # Validações prévias de integridade
    for uf, bancada in bancadas_uf.items():
        if bancada < 0:
            raise ValueError(f"Bancada da UF '{uf}' não pode ser negativa: {bancada}")
        if uf not in votos_uf_coluna:
            raise KeyError(f"UF '{uf}' não encontrada no mapeamento de votos.")
        if uf not in taxas_validos_voto4_uf:
            raise KeyError(f"Taxa de votos válidos do Voto 4 ausente para a UF '{uf}'.")

    for uf, col_map in votos_uf_coluna.items():
        for col, v in col_map.items():
            if v < 0:
                raise ValueError(f"Voto negativo detectado na célula ('{uf}', '{col}'): {v}")

    if votos_exterior_transito:
        for col, v in votos_exterior_transito.items():
            if v < 0:
                raise ValueError(f"Voto negativo no exterior/trânsito na coluna '{col}': {v}")

    # =========================================================================
    # Etapa 0: Totalização dos votos nacionais por coluna temática V_c
    # =========================================================================
    # Eleitores no exterior e em trânsito votam em legenda temática (RT-29 / D-22),
    # somando em V_c sem inflar nem alterar a bancada rígida s_e dos Estados.
    votos_nacionais_coluna: dict[str, int] = {c: 0 for c in todas_colunas}
    for uf in bancadas_uf:
        for c in todas_colunas:
            votos_nacionais_coluna[c] += votos_uf_coluna[uf].get(c, 0)

    if votos_exterior_transito:
        for c in todas_colunas:
            votos_nacionais_coluna[c] += votos_exterior_transito.get(c, 0)

    # =========================================================================
    # Etapa 1: Dimensionamento dos tetos de missão por UF (u_e) e teto nacional U
    # =========================================================================
    tetos_missao_uf = calcular_tetos_nacionais(
        bancadas=bancadas_uf,
        taxas_validos=taxas_validos_voto4_uf,
        rho=rho_missao,
    )
    teto_missao_nacional = sum(tetos_missao_uf.values())

    # =========================================================================
    # Etapa 2a: Dimensionamento global de cadeiras entre Bloco 2 e Bloco 3
    # =========================================================================
    total_cadeiras_federativas = sum(bancadas_uf.values())
    total_bloco_1 = len(colunas_estado) * piso_generalista
    cadeiras_livres_total = total_cadeiras_federativas - total_bloco_1

    if cadeiras_livres_total < 0:
        raise ValueError(
            f"Total de cadeiras das UFs ({total_cadeiras_federativas}) é insuficiente para "
            f"cobrir o núcleo fixo do Bloco 1 ({total_bloco_1})."
        )

    votos_bloco_2 = sum(votos_nacionais_coluna[c] for c in colunas_permanentes)
    votos_bloco_3 = sum(votos_nacionais_coluna[c] for c in colunas_missao)
    votos_livres = votos_bloco_2 + votos_bloco_3

    if votos_livres > 0 and len(colunas_missao) > 0:
        razao_exata = Fraction(cadeiras_livres_total * votos_bloco_3, votos_livres)
        h3_proporcional = math.floor(razao_exata + Fraction(1, 2))
    else:
        h3_proporcional = 0

    cadeiras_bloco_3 = min(teto_missao_nacional, h3_proporcional)
    cadeiras_bloco_2 = cadeiras_livres_total - cadeiras_bloco_3

    # =========================================================================
    # Etapa 2b: Repartição das cadeiras de missão entre as colunas do Bloco 3
    # =========================================================================
    cadeiras_missao_col: dict[str, int] = {}
    if colunas_missao:
        if cadeiras_bloco_3 > 0:
            votos_missao_unicos = {c: votos_nacionais_coluna[c] for c in colunas_missao}
            cadeiras_missao_col = alocar_sainte_lague(
                votos=votos_missao_unicos,
                total_cadeiras=cadeiras_bloco_3,
            )
        else:
            cadeiras_missao_col = {c: 0 for c in colunas_missao}

    # =========================================================================
    # Etapa 2c: Repartição das cadeiras permanentes com proteção de piso
    # =========================================================================
    pisos_permanentes = {c: piso_permanente for c in colunas_permanentes}
    votos_perm_unicos = {c: votos_nacionais_coluna[c] for c in colunas_permanentes}
    if sum(votos_perm_unicos.values()) > 0:
        cadeiras_perm_col = alocar_sainte_lague(
            votos=votos_perm_unicos,
            total_cadeiras=cadeiras_bloco_2,
            pisos=pisos_permanentes,
        )
    else:
        soma_pisos_perm = sum(pisos_permanentes.values())
        if soma_pisos_perm > cadeiras_bloco_2:
            raise ValueError(
                f"Soma dos pisos permanentes ({soma_pisos_perm}) excede o saldo do Bloco 2 ({cadeiras_bloco_2})."
            )
        cadeiras_perm_col = dict(pisos_permanentes)
        colunas_ordenadas = sorted(colunas_permanentes)
        restantes_bloco_2 = cadeiras_bloco_2 - soma_pisos_perm
        for idx in range(restantes_bloco_2):
            cadeiras_perm_col[colunas_ordenadas[idx % len(colunas_ordenadas)]] += 1

    # Consolidação do vetor nacional h_c para todas as colunas
    cadeiras_colunas: dict[str, int] = {}
    for c in colunas_estado:
        cadeiras_colunas[c] = piso_generalista
    for c in colunas_permanentes:
        cadeiras_colunas[c] = cadeiras_perm_col[c]
    for c in colunas_missao:
        cadeiras_colunas[c] = cadeiras_missao_col[c]

    # =========================================================================
    # Etapa 3a: Alocação biproporcional da matriz de missão institucional (Bloco 3)
    # =========================================================================
    votos_missao_mat = {
        uf: {c: votos_uf_coluna[uf].get(c, 0) for c in colunas_missao}
        for uf in bancadas_uf
    }
    resultado_missao = alocar_matriz_missao(
        votos_missao=votos_missao_mat,
        tetos_uf=tetos_missao_uf,
        cadeiras_coluna_missao=cadeiras_missao_col,
    )

    # Cadeiras de missão conquistadas por cada UF m_e
    m_e = {
        uf: sum(resultado_missao.matriz[uf][c] for c in colunas_missao)
        for uf in bancadas_uf
    }

    # =========================================================================
    # Etapa 3b: Alocação biproporcional da matriz principal (Blocos 1 e 2)
    # =========================================================================
    colunas_principais = colunas_estado + colunas_permanentes
    cadeiras_uf_principal = {uf: bancadas_uf[uf] - m_e[uf] for uf in bancadas_uf}
    cadeiras_coluna_principal = {c: cadeiras_colunas[c] for c in colunas_principais}
    votos_principal_mat = {
        uf: {c: votos_uf_coluna[uf].get(c, 0) for c in colunas_principais}
        for uf in bancadas_uf
    }

    resultado_principal = alocar_biproporcional(
        votos=votos_principal_mat,
        cadeiras_uf=cadeiras_uf_principal,
        cadeiras_coluna=cadeiras_coluna_principal,
    )

    # =========================================================================
    # Consolidação da matriz completa e auditoria de invariantes constitucionais
    # =========================================================================
    matriz_completa: dict[str, dict[str, int]] = {}
    for uf in bancadas_uf:
        matriz_completa[uf] = {}
        for c in colunas_principais:
            matriz_completa[uf][c] = resultado_principal.matriz[uf][c]
        for c in colunas_missao:
            matriz_completa[uf][c] = resultado_missao.matriz[uf][c]

    auditoria = auditar_invariantes_constitucionais(
        matriz_completa=matriz_completa,
        bancadas_uf=bancadas_uf,
        cadeiras_colunas=cadeiras_colunas,
        tetos_missao_uf=tetos_missao_uf,
        colunas_estado=colunas_estado,
        colunas_permanentes=colunas_permanentes,
        colunas_missao=colunas_missao,
        piso_generalista=piso_generalista,
        piso_permanente=piso_permanente,
        total_esperado=total_cadeiras_federativas,
    )

    return ResultadoApuracaoNacional(
        votos_nacionais_coluna=votos_nacionais_coluna,
        tetos_missao_uf=tetos_missao_uf,
        teto_missao_nacional=teto_missao_nacional,
        cadeiras_bloco_3=cadeiras_bloco_3,
        cadeiras_bloco_2=cadeiras_bloco_2,
        cadeiras_colunas=cadeiras_colunas,
        resultado_missao=resultado_missao,
        resultado_principal=resultado_principal,
        matriz_completa=matriz_completa,
        auditoria=auditoria,
    )


def apurar_celula_stv(
    candidatos: Sequence[CandidatoCelula],
    cadeiras: int,
    votos_confianca_partido: Mapping[str, int] | None = None,
    votos_confianca_coluna: int = 0,
    percentual_piso_legenda: float = 0.10,
) -> ResultadoCelula:
    """Apura a alocação intracelular de assentos por voto único transferível (Etapa 4 / STV).

    Implementa os postulados de RT-03, RT-04, RT-16, D-12 e D-15:
      1. Computa o total de sufrágios válidos, somando os votos nominais diretos, os votos
         de legenda partidária na coluna (`votos_confianca_partido`) e os votos em branco
         ou nulo neutros na Tela 2 da coluna de missão (`votos_confianca_coluna`).
      2. Calcula a cota eleitoral de Droop q = floor(V_total / (cadeiras + 1)) + 1.
      3. Rateia `votos_confianca_coluna` proporcionalmente à votação nominal inicial entre
         todos os candidatos da célula (neutro entre partidos) e atribui
         `votos_confianca_partido` apenas aos candidatos habilitados (com votação nominal
         direta >= percentual_piso_legenda * q, padrão 10% da Cota de Droop) em ordem
         decrescente de votos nominais até atingir a cota q, alocando eventual saldo
         residual ao candidato habilitado mais votado do partido.
      4. Elege candidatos que atingem q e transfere excedentes (surplus) e votos de
         eliminados em cascata sequencial mutuamente exclusiva (`transferir_votos`):
           (1) Havendo `votos_segunda > 0` nos candidatos ativos, rateia proporcionalmente
               a `votos_segunda` entre os ativos (STV simplificado, D-12 / RT-16);
           (2) Senão, havendo `votos_terceira > 0` nos ativos, rateia proporcionalmente a
               `votos_terceira` (mantido no código por generalidade algorítmica);
           (3) Senão, havendo correligionários ativos do mesmo partido na célula, rateia
               proporcionalmente a `max(1, votos_primeira)` entre eles (fallback D-12);
           (4) Senão, rateia proporcionalmente a `max(1, votos_primeira)` entre todos os ativos.
      5. Retorna a lista de eleitos, suplentes ordenados e distribuição partidária.

    Args:
        candidatos: Sequência com os registros de votação e preferências de cada concorrente.
        cadeiras: Total de mandatos parlamentares a preencher na célula (UF x Coluna).
        votos_confianca_partido: Votos de legenda partidária na coluna (todos os blocos).
        votos_confianca_coluna: Votos em branco ou nulo na Tela 2 da coluna de missão,
            neutros entre partidos e rateados proporcionalmente na célula (D-15 / RT-04).
        percentual_piso_legenda: Cláusula de barreira nominal individual em proporção à Cota
            de Droop (padrão 0.10 = 10%) para habilitação a votos de legenda partidária.

    Returns:
        ResultadoCelula estruturado com eleitos, suplentes e cotas.

    Raises:
        ValueError: Se houver contagens de votos negativas, número negativo de assentos ou
            percentual_piso_legenda fora de [0.0, 1.0].
    """
    if cadeiras < 0:
        raise ValueError(f"O número de cadeiras da célula não pode ser negativo: {cadeiras}")
    if votos_confianca_coluna < 0:
        raise ValueError(
            f"Votos de confiança neutros da coluna não podem ser negativos: {votos_confianca_coluna}"
        )
    if not (0.0 <= percentual_piso_legenda <= 1.0):
        raise ValueError(
            f"O percentual mínimo nominal para legenda deve estar em [0.0, 1.0]: {percentual_piso_legenda}"
        )

    for c in candidatos:
        if c.votos_primeira < 0 or c.votos_segunda < 0 or c.votos_terceira < 0:
            raise ValueError(
                f"Contagens de votos negativas detectadas para o candidato '{c.id_candidato}'."
            )

    if votos_confianca_partido:
        for p, v in votos_confianca_partido.items():
            if v < 0:
                raise ValueError(
                    f"Voto de confiança partidário não pode ser negativo: '{p}' tem {v} votos."
                )

    partidos_presentes = {c.partido for c in candidatos}
    if votos_confianca_partido:
        partidos_presentes.update(votos_confianca_partido.keys())

    if not candidatos or cadeiras == 0:
        # Nenhum assento a preencher ou nenhum candidato registrado
        suplentes_ordenados = [
            c.id_candidato
            for c in sorted(
                candidatos,
                key=lambda x: (-x.votos_primeira, -x.votos_segunda, x.id_candidato),
            )
        ]
        return ResultadoCelula(
            eleitos=[],
            suplentes_celula=suplentes_ordenados,
            cadeiras_por_partido={p: 0 for p in partidos_presentes},
            cota_droop=0,
        )

    # Cálculo da cota de Droop
    total_confianca = (
        sum(votos_confianca_partido.values()) if votos_confianca_partido else 0
    )
    votos_totais = (
        sum(c.votos_primeira for c in candidatos)
        + total_confianca
        + votos_confianca_coluna
    )

    if votos_totais == 0:
        cota_droop = 1
    else:
        cota_droop = (votos_totais // (cadeiras + 1)) + 1

    # Pontuação inicial, rateio neutro da coluna e votos de legenda partidária (Tela 2)
    pontuacao: dict[str, float] = {c.id_candidato: float(c.votos_primeira) for c in candidatos}
    candidatos_map = {c.id_candidato: c for c in candidatos}

    if votos_confianca_coluna > 0:
        soma_primeira = sum(c.votos_primeira for c in candidatos)
        if soma_primeira > 0:
            for c in candidatos:
                pontuacao[c.id_candidato] += votos_confianca_coluna * (
                    c.votos_primeira / soma_primeira
                )
        else:
            fatia_uniforme = votos_confianca_coluna / len(candidatos)
            for c in candidatos:
                pontuacao[c.id_candidato] += fatia_uniforme

    piso_nominal_legenda = Fraction(str(percentual_piso_legenda)) * cota_droop
    if votos_confianca_partido:
        for p, v_disp in votos_confianca_partido.items():
            if v_disp <= 0:
                continue
            # Candidatos habilitados do partido (>= 10% da Cota de Droop) ordenados por votação nominal
            membros = sorted(
                [
                    c
                    for c in candidatos
                    if c.partido == p and Fraction(c.votos_primeira) >= piso_nominal_legenda
                ],
                key=lambda x: (-x.votos_primeira, -x.votos_segunda, x.id_candidato),
            )
            if not membros:
                continue

            saldo = float(v_disp)
            # Distribui primeiramente a quem ainda precisa atingir a cota
            for membro in membros:
                cid = membro.id_candidato
                if pontuacao[cid] < cota_droop:
                    necessario = cota_droop - pontuacao[cid]
                    alocar = min(saldo, necessario)
                    pontuacao[cid] += alocar
                    saldo -= alocar
                    if saldo <= 0:
                        break

            # Se ainda houver saldo excedente de legenda, atribui ao candidato habilitado mais votado
            if saldo > 0:
                pontuacao[membros[0].id_candidato] += saldo

    # =========================================================================
    # Processo de Voto Único Transferível (STV)
    # =========================================================================
    eleitos: list[str] = []
    eliminados: list[str] = []
    ativos = set(pontuacao.keys())

    def transferir_votos(fonte_id: str, montante: float) -> None:
        """Transfere excedente ou votos de eliminado conforme preferências e legenda."""
        if montante <= 1e-9 or not ativos:
            return

        # Prioridade 1: Preferências subsequentes declaradas (RT-16)
        soma_segunda = sum(candidatos_map[cid].votos_segunda for cid in ativos)
        if soma_segunda > 0:
            for cid in ativos:
                peso = candidatos_map[cid].votos_segunda / soma_segunda
                pontuacao[cid] += montante * peso
            return

        soma_terceira = sum(candidatos_map[cid].votos_terceira for cid in ativos)
        if soma_terceira > 0:
            for cid in ativos:
                peso = candidatos_map[cid].votos_terceira / soma_terceira
                pontuacao[cid] += montante * peso
            return

        # Prioridade 2: Correligionários da mesma legenda por votação nominal (D-12)
        partido_fonte = candidatos_map[fonte_id].partido
        correligionarios = [cid for cid in ativos if candidatos_map[cid].partido == partido_fonte]
        if correligionarios:
            soma_nom = sum(max(1, candidatos_map[cid].votos_primeira) for cid in correligionarios)
            for cid in correligionarios:
                peso = max(1, candidatos_map[cid].votos_primeira) / soma_nom
                pontuacao[cid] += montante * peso
            return

        # Prioridade 3: Rateio proporcional entre todos os ativos restantes
        soma_geral = sum(max(1, candidatos_map[cid].votos_primeira) for cid in ativos)
        for cid in ativos:
            peso = max(1, candidatos_map[cid].votos_primeira) / soma_geral
            pontuacao[cid] += montante * peso

    while len(eleitos) < cadeiras and ativos:
        # Se o total de candidatos restantes coincidir com as vagas abertas, todos são eleitos
        if len(ativos) <= (cadeiras - len(eleitos)):
            restantes = sorted(
                ativos,
                key=lambda cid: (
                    -pontuacao[cid],
                    -candidatos_map[cid].votos_primeira,
                    cid,
                ),
            )
            eleitos.extend(restantes)
            ativos.clear()
            break

        # Candidatos que superaram ou atingiram a cota de Droop
        qualificados = [cid for cid in ativos if pontuacao[cid] >= cota_droop]
        if qualificados:
            # Elege o mais bem colocado
            vencedor = min(
                qualificados,
                key=lambda cid: (
                    -pontuacao[cid],
                    -candidatos_map[cid].votos_primeira,
                    cid,
                ),
            )
            eleitos.append(vencedor)
            ativos.remove(vencedor)
            excedente = pontuacao[vencedor] - cota_droop
            pontuacao[vencedor] = float(cota_droop)

            if excedente > 0:
                transferir_votos(vencedor, excedente)
            continue

        # Nenhum candidato atingiu a cota: elimina o de menor pontuação
        candidato_eliminado = min(
            ativos,
            key=lambda cid: (
                pontuacao[cid],
                candidatos_map[cid].votos_primeira,
                candidatos_map[cid].id_candidato,
            ),
        )
        ativos.remove(candidato_eliminado)
        eliminados.append(candidato_eliminado)
        votos_eliminado = pontuacao[candidato_eliminado]
        pontuacao[candidato_eliminado] = 0.0

        if votos_eliminado > 0:
            transferir_votos(candidato_eliminado, votos_eliminado)

    # Ordenação dos suplentes não eleitos por desempenho final
    nao_eleitos = [c.id_candidato for c in candidatos if c.id_candidato not in eleitos]
    suplentes_ordenados = sorted(
        nao_eleitos,
        key=lambda cid: (
            -pontuacao[cid],
            -candidatos_map[cid].votos_primeira,
            -candidatos_map[cid].votos_segunda,
            cid,
        ),
    )

    cadeiras_partidos: dict[str, int] = {p: 0 for p in partidos_presentes}
    for eid in eleitos:
        p = candidatos_map[eid].partido
        cadeiras_partidos[p] = cadeiras_partidos.get(p, 0) + 1

    return ResultadoCelula(
        eleitos=eleitos,
        suplentes_celula=suplentes_ordenados,
        cadeiras_por_partido=cadeiras_partidos,
        cota_droop=cota_droop,
    )


def buscar_suplente_regiao(
    partido: str,
    coluna: str,
    uf_origem: str,
    suplentes_por_uf_coluna: Mapping[str, Mapping[str, Sequence[CandidatoCelula]]],
    macrorregioes: Mapping[str, str] = MACRORREGIOES,
) -> str | None:
    """Localiza o suplente legítimo do mandato conforme a regra aprovada no RT-11 (D-20).

    Ordem estrita de sucessão:
      1ª Prioridade: Suplente da mesma legenda partidária na mesma célula (uf_origem, coluna).
      2ª Prioridade: Suplente mais votado do mesmo partido na mesma coluna em outra UF da
         mesma macrorregião geográfica oficial do IBGE.
      Se esgotadas todas as opções na macrorregião, retorna None.

    Args:
        partido: Sigla do partido titular do mandato parlamentar vago.
        coluna: Coluna temática do mandato a substituir.
        uf_origem: Sigla da UF originária do mandato.
        suplentes_por_uf_coluna: Mapeamento {uf: {coluna: sequencia_suplentes_ordenados}}.
        macrorregioes: Mapeamento {uf: regiao_ibge} das macrorregiões brasileiras.

    Returns:
        Identificador id_candidato do suplente sucessor, ou None caso inexista.
    """
    # 1ª Prioridade: Mesmo partido na célula local de origem
    if uf_origem in suplentes_por_uf_coluna:
        suplentes_locais = suplentes_por_uf_coluna[uf_origem].get(coluna, ())
        for cand in suplentes_locais:
            if cand.partido == partido:
                return cand.id_candidato

    # 2ª Prioridade: Mesmo partido na mesma coluna em outra UF da mesma macrorregião
    regiao_origem = macrorregioes.get(uf_origem)
    if not regiao_origem:
        return None

    candidatos_regionais: list[CandidatoCelula] = []
    for outra_uf, reg in macrorregioes.items():
        if reg == regiao_origem and outra_uf != uf_origem:
            if outra_uf in suplentes_por_uf_coluna:
                suplentes_outra = suplentes_por_uf_coluna[outra_uf].get(coluna, ())
                for cand in suplentes_outra:
                    if cand.partido == partido:
                        candidatos_regionais.append(cand)

    if not candidatos_regionais:
        return None

    # Seleciona o suplente regional com maior votação nominal
    sucessor_regional = min(
        candidatos_regionais,
        key=lambda c: (
            -c.votos_primeira,
            -c.votos_segunda,
            -c.votos_terceira,
            c.id_candidato,
        ),
    )
    return sucessor_regional.id_candidato
