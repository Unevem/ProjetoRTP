# ---------------------------------------------------------------------------
# [BLK-L-006-T] Testes de Integração e Invariantes Constitucionais de Ponta a Ponta
# ---------------------------------------------------------------------------
"""Suíte de testes de integração e auditoria de invariantes constitucionais do pipeline RTP.

Valida a ponta a ponta do sistema de apuração nacional:
  1. Cenário nacional completo com 27 UFs e 12 colunas temáticas (513 deputados).
  2. Cenário de protesto total no Voto 4 (H_3 = 0, H_2 = 333, integridade das invariantes).
  3. Deslocamento de cadeiras por votos do exterior e trânsito (RT-29 / D-22) sem violar s_e.
  4. Configuração com 6 colunas de missão ativas dos 2 finalistas presidenciais (RT-02 / D-17).
  5. Teste de estresse de Monte Carlo com 20 sementes determinísticas comprovando 100% de aprovação.
  6. Alocação intracelular por STV com transferências de preferência (RT-16), voto de confiança
     partidário na legenda (RT-04) e sucessão regional de suplência (RT-11 / D-20).
"""

import random
import unittest

from simulador.src.constantes import (
    BANCADAS_ESTADUAIS,
    COLUNAS_ESTADO,
    COLUNAS_MISSAO_PADRAO,
    COLUNAS_PERMANENTES,
    MACRORREGIOES,
    PISO_GENERALISTA,
    PISO_PERMANENTE,
    TODAS_COLUNAS_PADRAO,
    TOTAL_CADEIRAS,
)
from simulador.src.pipeline import (
    CandidatoCelula,
    ResultadoApuracaoNacional,
    ResultadoCelula,
    apurar_celula_stv,
    buscar_suplente_regiao,
    executar_apuracao_nacional,
)


class TestInvariantesPipelineNacional(unittest.TestCase):
    """Testes de integração de ponta a ponta e checagem estrita de invariantes constitucionais."""

    def setUp(self) -> None:
        """Prepara base sintética determinística de votos para as 27 UFs e 12 colunas."""
        self.rng = random.Random(42)
        self.votos_padrao: dict[str, dict[str, int]] = {}

        for uf, bancada in BANCADAS_ESTADUAIS.items():
            self.votos_padrao[uf] = {}
            for col in TODAS_COLUNAS_PADRAO:
                # Volume de votos proporcional ao peso demográfico da bancada
                fator_base = bancada * 15000
                ruido = self.rng.randint(2000, 8000)
                self.votos_padrao[uf][col] = fator_base + ruido

        # Taxas médias normais de votos válidos no Voto 4 (entre 75% e 92%)
        self.taxas_padrao: dict[str, float] = {
            uf: 0.75 + (i % 18) * 0.01
            for i, uf in enumerate(BANCADAS_ESTADUAIS.keys())
        }

    def test_01_cenario_nacional_completo_27_ufs_12_colunas(self) -> None:
        """Teste 1: Cenário nacional completo com 27 UFs e 12 colunas (auditoria 100% aprovada)."""
        resultado = executar_apuracao_nacional(
            votos_uf_coluna=self.votos_padrao,
            taxas_validos_voto4_uf=self.taxas_padrao,
        )

        self.assertIsInstance(resultado, ResultadoApuracaoNacional)
        auditoria = resultado.auditoria

        # Invariantes fundamentais
        self.assertTrue(auditoria.aprovado, f"Erros na auditoria: {auditoria.erros}")
        self.assertTrue(auditoria.soma_total_513)
        self.assertTrue(auditoria.pacto_federativo_intacto)
        self.assertTrue(auditoria.fechamento_tematico_intacto)
        self.assertTrue(auditoria.nucleo_estado_60_fixo)
        self.assertTrue(auditoria.pisos_permanentes_respeitados)
        self.assertTrue(auditoria.tetos_missao_respeitados)
        self.assertEqual(auditoria.erros, [])

        # Conservação das 333 cadeiras livres
        self.assertEqual(
            resultado.cadeiras_bloco_2 + resultado.cadeiras_bloco_3,
            333,
        )
        self.assertEqual(sum(resultado.cadeiras_colunas.values()), TOTAL_CADEIRAS)

        # Checagem das somas de linhas (Pacto Federativo) e colunas
        for uf, bancada in BANCADAS_ESTADUAIS.items():
            soma_uf = sum(resultado.matriz_completa[uf].values())
            self.assertEqual(soma_uf, bancada)

        for col, meta_col in resultado.cadeiras_colunas.items():
            soma_col = sum(resultado.matriz_completa[uf][col] for uf in BANCADAS_ESTADUAIS)
            self.assertEqual(soma_col, meta_col)

        # Tríade Generalista deve ter exatamente 60 em cada uma das 3 colunas
        for col in COLUNAS_ESTADO:
            self.assertEqual(resultado.cadeiras_colunas[col], PISO_GENERALISTA)

        # Colunas permanentes devem respeitar piso de 20
        for col in COLUNAS_PERMANENTES:
            self.assertGreaterEqual(resultado.cadeiras_colunas[col], PISO_PERMANENTE)

        # Nenhuma UF pode violar seu teto efetivo u_e em missões
        for uf in BANCADAS_ESTADUAIS:
            soma_missao_uf = sum(
                resultado.matriz_completa[uf][c] for c in COLUNAS_MISSAO_PADRAO
            )
            self.assertLessEqual(soma_missao_uf, resultado.tetos_missao_uf[uf])

    def test_02_protesto_total_voto4_encolhimento_maximo(self) -> None:
        """Teste 2: Protesto total no Voto 4 (taxas 0.0 -> H_3 = 0, H_2 = 333, auditoria aprovada)."""
        taxas_protesto = {uf: 0.0 for uf in BANCADAS_ESTADUAIS}

        resultado = executar_apuracao_nacional(
            votos_uf_coluna=self.votos_padrao,
            taxas_validos_voto4_uf=taxas_protesto,
        )

        self.assertTrue(resultado.auditoria.aprovado, f"Erros: {resultado.auditoria.erros}")
        self.assertEqual(resultado.teto_missao_nacional, 0)
        self.assertEqual(resultado.cadeiras_bloco_3, 0)
        self.assertEqual(resultado.cadeiras_bloco_2, 333)

        # Todas as colunas de missão devem ter exatamente 0 cadeiras
        for col in COLUNAS_MISSAO_PADRAO:
            self.assertEqual(resultado.cadeiras_colunas[col], 0)

        # Nenhuma cadeira de missão alocada em nenhuma UF
        for uf in BANCADAS_ESTADUAIS:
            for col in COLUNAS_MISSAO_PADRAO:
                self.assertEqual(resultado.matriz_completa[uf][col], 0)

        # As 333 cadeiras livres ficam 100% com as 6 colunas permanentes
        soma_perm = sum(resultado.cadeiras_colunas[c] for c in COLUNAS_PERMANENTES)
        self.assertEqual(soma_perm, 333)

        # Soma total global rigorosamente 513
        self.assertEqual(sum(resultado.cadeiras_colunas.values()), 513)

    def test_03_votos_exterior_transito_deslocam_colunas_sem_alterar_bancadas_estaduais(
        self,
    ) -> None:
        """Teste 3: Votos do exterior e trânsito (RT-29 / D-22) alteram h_c sem mudar s_e."""
        # Apuração de referência SEM exterior/trânsito
        res_base = executar_apuracao_nacional(
            votos_uf_coluna=self.votos_padrao,
            taxas_validos_voto4_uf=self.taxas_padrao,
            votos_exterior_transito=None,
        )

        # Apuração COM 4 milhões de votos de legenda temática em C04_SAUDE
        votos_ext = {"C04_SAUDE": 4_000_000}
        res_com_ext = executar_apuracao_nacional(
            votos_uf_coluna=self.votos_padrao,
            taxas_validos_voto4_uf=self.taxas_padrao,
            votos_exterior_transito=votos_ext,
        )

        self.assertTrue(res_com_ext.auditoria.aprovado)

        # 1. As bancadas estaduais s_e permanecem RIGOROSAMENTE INTACTAS
        for uf, bancada in BANCADAS_ESTADUAIS.items():
            self.assertEqual(sum(res_base.matriz_completa[uf].values()), bancada)
            self.assertEqual(sum(res_com_ext.matriz_completa[uf].values()), bancada)

        # 2. A coluna beneficiada pelo exterior aumentou suas cadeiras nacionais h_c
        self.assertGreater(
            res_com_ext.cadeiras_colunas["C04_SAUDE"],
            res_base.cadeiras_colunas["C04_SAUDE"],
        )

        # 3. O total global de votos computados na coluna inclui os votos de trânsito
        self.assertEqual(
            res_com_ext.votos_nacionais_coluna["C04_SAUDE"],
            res_base.votos_nacionais_coluna["C04_SAUDE"] + 4_000_000,
        )

    def test_04_seis_colunas_missao_ativas_dois_finalistas(self) -> None:
        """Teste 4: Configuração com 6 colunas de missão ativas dos 2 finalistas (RT-02 / D-17)."""
        colunas_missao_finalistas = (
            "C10_M1_FIN1",
            "C11_M2_FIN1",
            "C12_M3_FIN1",
            "C13_M1_FIN2",
            "C14_M2_FIN2",
            "C15_M3_FIN2",
        )
        todas_15_colunas = (
            COLUNAS_ESTADO + COLUNAS_PERMANENTES + colunas_missao_finalistas
        )

        votos_15: dict[str, dict[str, int]] = {}
        for uf, bancada in BANCADAS_ESTADUAIS.items():
            votos_15[uf] = {}
            for col in todas_15_colunas:
                votos_15[uf][col] = bancada * 10000 + self.rng.randint(1000, 5000)

        resultado = executar_apuracao_nacional(
            votos_uf_coluna=votos_15,
            taxas_validos_voto4_uf=self.taxas_padrao,
            colunas_missao=colunas_missao_finalistas,
        )

        self.assertTrue(resultado.auditoria.aprovado, f"Erros: {resultado.auditoria.erros}")
        self.assertEqual(len(resultado.cadeiras_colunas), 15)

        # Cada uma das 6 colunas de missão deve ter assentos calculados
        soma_missao_total = sum(
            resultado.cadeiras_colunas[c] for c in colunas_missao_finalistas
        )
        self.assertEqual(soma_missao_total, resultado.cadeiras_bloco_3)
        self.assertLessEqual(soma_missao_total, resultado.teto_missao_nacional)

        # Todas as UFs respeitam o teto somando as 6 missões
        for uf in BANCADAS_ESTADUAIS:
            soma_uf_missao = sum(
                resultado.matriz_completa[uf][c] for c in colunas_missao_finalistas
            )
            self.assertLessEqual(soma_uf_missao, resultado.tetos_missao_uf[uf])

    def test_05_monte_carlo_20_sementes_determinismo_e_estabilidade(self) -> None:
        """Teste 5: Monte Carlo com 20 sementes determinísticas comprovando 100% de aprovação."""
        for seed in range(1, 21):
            with self.subTest(seed=seed):
                rng = random.Random(seed)

                # Gera cenário eleitoral aleatório
                votos_mc: dict[str, dict[str, int]] = {}
                for uf, bancada in BANCADAS_ESTADUAIS.items():
                    votos_mc[uf] = {}
                    for col in TODAS_COLUNAS_PADRAO:
                        # Votos variados de pequena a grande magnitude
                        votos_mc[uf][col] = rng.randint(500, bancada * 25000)

                # Taxas heterogêneas de comparecimento e validade no Voto 4 (0.10 a 1.00)
                taxas_mc = {uf: rng.uniform(0.10, 1.00) for uf in BANCADAS_ESTADUAIS}

                # Votos eventuais de trânsito
                votos_ext_mc = {
                    col: rng.randint(0, 100_000) for col in TODAS_COLUNAS_PADRAO
                }

                resultado = executar_apuracao_nacional(
                    votos_uf_coluna=votos_mc,
                    taxas_validos_voto4_uf=taxas_mc,
                    votos_exterior_transito=votos_ext_mc,
                )

                self.assertTrue(
                    resultado.auditoria.aprovado,
                    f"Falha na semente {seed}: {resultado.auditoria.erros}",
                )
                self.assertEqual(sum(resultado.cadeiras_colunas.values()), 513)

    def test_06_apuracao_celula_stv_e_suplencia_regional(self) -> None:
        """Teste 6: STV com transferência de preferências (RT-16), voto de confiança e suplência."""
        # =====================================================================
        # Parte A: RT-16 - Candidato puxador de votos salva candidato menor via 2ª preferência
        # =====================================================================
        candidatos_stv = [
            CandidatoCelula(
                id_candidato="puxador_A1",
                partido="PARTIDO_A",
                votos_primeira=1000,
                votos_segunda=0,
            ),
            CandidatoCelula(
                id_candidato="candidato_A2",
                partido="PARTIDO_A",
                votos_primeira=60,
                votos_segunda=0,
            ),
            CandidatoCelula(
                id_candidato="candidato_B1",
                partido="PARTIDO_B",
                votos_primeira=120,
                votos_segunda=450,  # Alta aceitação em 2ª preferência
            ),
            CandidatoCelula(
                id_candidato="candidato_C1",
                partido="PARTIDO_C",
                votos_primeira=150,
                votos_segunda=20,
            ),
        ]

        # 2 cadeiras na célula. Votos totais = 1330.
        # Cota de Droop = (1330 // 3) + 1 = 444.
        res_stv = apurar_celula_stv(candidatos=candidatos_stv, cadeiras=2)

        self.assertEqual(len(res_stv.eleitos), 2)
        # O puxador é eleito na 1ª rodada
        self.assertIn("puxador_A1", res_stv.eleitos)
        # O candidato B1 é salvo pelas segundas preferências e conquista a 2ª vaga
        self.assertIn("candidato_B1", res_stv.eleitos)
        self.assertNotIn("candidato_C1", res_stv.eleitos)
        # Suplentes ordenados
        self.assertEqual(res_stv.suplentes_celula[0], "candidato_C1")
        self.assertEqual(res_stv.cadeiras_por_partido["PARTIDO_A"], 1)
        self.assertEqual(res_stv.cadeiras_por_partido["PARTIDO_B"], 1)

        # =====================================================================
        # Parte B: RT-04 - Voto de confiança partidário (Tela 2) viabiliza eleição da legenda
        # =====================================================================
        candidatos_legenda = [
            CandidatoCelula(
                id_candidato="cand_alfa",
                partido="PARTIDO_ALFA",
                votos_primeira=80,
            ),
            CandidatoCelula(
                id_candidato="cand_beta",
                partido="PARTIDO_BETA",
                votos_primeira=115,
            ),
        ]
        # Partido ALFA recebe 60 votos em branco/confiança institucional da Tela 2
        # Total = 80 + 115 + 60 = 255. Cota Droop para 1 cadeira = (255 // 2) + 1 = 128.
        # Alfa recebe o montante para atingir a cota (80 + 60 = 140 >= 128) e vence.
        res_legenda = apurar_celula_stv(
            candidatos=candidatos_legenda,
            cadeiras=1,
            votos_confianca_partido={"PARTIDO_ALFA": 60},
        )
        self.assertEqual(res_legenda.eleitos, ["cand_alfa"])
        self.assertEqual(res_legenda.cadeiras_por_partido["PARTIDO_ALFA"], 1)
        self.assertEqual(res_legenda.suplentes_celula, ["cand_beta"])

        # =====================================================================
        # Parte C: RT-11 / D-20 - Regra de Suplência Temática Regional
        # =====================================================================
        suplentes_banco = {
            "SP": {
                "C04_SAUDE": [
                    CandidatoCelula(id_candidato="suplente_sp_p1", partido="P1", votos_primeira=5000),
                    CandidatoCelula(id_candidato="suplente_sp_p2", partido="P2", votos_primeira=3000),
                ]
            },
            "MG": {
                "C04_SAUDE": [
                    CandidatoCelula(id_candidato="suplente_mg_p3", partido="P3", votos_primeira=4000),
                    CandidatoCelula(id_candidato="suplente_mg_p1", partido="P1", votos_primeira=2500),
                ]
            },
            "RJ": {
                "C04_SAUDE": [
                    CandidatoCelula(id_candidato="suplente_rj_p3", partido="P3", votos_primeira=7000),
                ]
            },
            "AM": {
                "C04_SAUDE": [
                    CandidatoCelula(id_candidato="suplente_am_p4", partido="P4", votos_primeira=1000),
                ]
            },
            "PA": {
                "C04_SAUDE": [
                    CandidatoCelula(id_candidato="suplente_pa_p4", partido="P4", votos_primeira=3500),
                ]
            },
        }

        # 1ª Prioridade: Mesmo partido na célula local de SP
        s1 = buscar_suplente_regiao(
            partido="P1",
            coluna="C04_SAUDE",
            uf_origem="SP",
            suplentes_por_uf_coluna=suplentes_banco,
        )
        self.assertEqual(s1, "suplente_sp_p1")

        # 2ª Prioridade: Esgotado em SP para o partido P3 -> busca na mesma macrorregião Sudeste (MG ou RJ).
        # RJ tem suplente P3 com 7000 votos e MG com 4000 -> escolhe o do RJ por ser o mais votado.
        s2 = buscar_suplente_regiao(
            partido="P3",
            coluna="C04_SAUDE",
            uf_origem="SP",
            suplentes_por_uf_coluna=suplentes_banco,
        )
        self.assertEqual(s2, "suplente_rj_p3")

        # 3ª Prioridade: Esgotado em toda a macrorregião Sudeste para o partido P4 -> retorna None
        s3 = buscar_suplente_regiao(
            partido="P4",
            coluna="C04_SAUDE",
            uf_origem="SP",
            suplentes_por_uf_coluna=suplentes_banco,
        )
        self.assertIsNone(s3)

    def test_07_voto_confianca_coluna_neutro_tela2(self) -> None:
        """Teste 7: Branco/nulo neutro na Tela 2 rateia proporcionalmente na coluna sem viés partidário."""
        candidatos_coluna = [
            CandidatoCelula(
                id_candidato="cand_p1",
                partido="PARTIDO_A",
                votos_primeira=200,
            ),
            CandidatoCelula(
                id_candidato="cand_p2",
                partido="PARTIDO_B",
                votos_primeira=100,
            ),
        ]
        # 300 votos nominais + 300 votos em branco/nulo neutros na Tela 2 = 600 válidos.
        # Cota de Droop para 1 cadeira = (600 // 2) + 1 = 301.
        # Rateio proporcional neutro: cand_p1 recebe +200 (400 >= 301), cand_p2 recebe +100 (200 < 301).
        res = apurar_celula_stv(
            candidatos=candidatos_coluna,
            cadeiras=1,
            votos_confianca_coluna=300,
        )
        self.assertEqual(res.cota_droop, 301)
        self.assertEqual(res.eleitos, ["cand_p1"])
        self.assertEqual(res.cadeiras_por_partido["PARTIDO_A"], 1)
        self.assertEqual(res.cadeiras_por_partido["PARTIDO_B"], 0)
        self.assertEqual(res.suplentes_celula, ["cand_p2"])

        with self.assertRaises(ValueError):
            apurar_celula_stv(
                candidatos=candidatos_coluna,
                cadeiras=1,
                votos_confianca_coluna=-1,
            )

    def test_08_exatidao_racional_h3_sem_erro_ieee754(self) -> None:
        """Teste 8: Exatidão racional no cálculo de H_3 em ponto exato de meio-inteiro (333*21/666 = 10.5 -> 11)."""
        votos_edge: dict[str, dict[str, int]] = {}
        ufs_ord = sorted(BANCADAS_ESTADUAIS.keys())
        for idx, uf in enumerate(ufs_ord):
            votos_edge[uf] = {c: 0 for c in TODAS_COLUNAS_PADRAO}
            for c in COLUNAS_ESTADO:
                votos_edge[uf][c] = 100
        # Coloca exatamente V_C3 = 21 e V_C2 = 645 (645 + 21 = 666 -> 333 * 21 / 666 = 10.5 exato)
        votos_edge["SP"]["C10_MISSAO_1"] = 21
        votos_edge["SP"]["C04_SAUDE"] = 645

        taxas_altas = {uf: 1.0 for uf in BANCADAS_ESTADUAIS}
        res = executar_apuracao_nacional(
            votos_uf_coluna=votos_edge,
            taxas_validos_voto4_uf=taxas_altas,
        )
        self.assertTrue(res.auditoria.aprovado)
        self.assertEqual(res.cadeiras_bloco_3, 11)
        self.assertEqual(res.cadeiras_bloco_2, 322)

    def test_09_contingencia_bloco_permanente_zero_votos(self) -> None:
        """Teste 9: Salvaguarda quando V_C2 = 0 garante fechamento dos pisos de 20 e invariantes intactas."""
        votos_perm_zero: dict[str, dict[str, int]] = {}
        for uf, bancada in BANCADAS_ESTADUAIS.items():
            votos_perm_zero[uf] = {
                c: (bancada * 1000 if c in COLUNAS_ESTADO or c in COLUNAS_MISSAO_PADRAO else 0)
                for c in TODAS_COLUNAS_PADRAO
            }

        res = executar_apuracao_nacional(
            votos_uf_coluna=votos_perm_zero,
            taxas_validos_voto4_uf=self.taxas_padrao,
        )
        self.assertTrue(res.auditoria.aprovado)
        self.assertEqual(res.cadeiras_bloco_2, 333 - res.cadeiras_bloco_3)
        for c in COLUNAS_PERMANENTES:
            self.assertGreaterEqual(res.cadeiras_colunas[c], 20)

    def test_10_piso_desempenho_individual_dez_por_cento_droop(self) -> None:
        """Teste 10: Candidato abaixo de 10% da Cota de Droop em votos nominais não é puxado pela legenda."""
        candidatos_piso = [
            CandidatoCelula(
                id_candidato="cand_sem_piso",
                partido="PARTIDO_X",
                votos_primeira=10,  # abaixo de 10% de Droop (251 * 0.10 = 25.1)
            ),
            CandidatoCelula(
                id_candidato="cand_adversario",
                partido="PARTIDO_Y",
                votos_primeira=200,
            ),
        ]
        # Total = 10 + 200 + 290 = 500. Cota Droop (1 vaga) = 251. Piso 10% = 25.1.
        # PARTIDO_X tem apenas cand_sem_piso (10 < 25.1), portanto não recebe os 290 de legenda diretamente.
        res = apurar_celula_stv(
            candidatos=candidatos_piso,
            cadeiras=1,
            votos_confianca_partido={"PARTIDO_X": 290},
        )
        self.assertEqual(res.cota_droop, 251)
        self.assertEqual(res.eleitos, ["cand_adversario"])
        self.assertEqual(res.cadeiras_por_partido["PARTIDO_X"], 0)
        self.assertEqual(res.cadeiras_por_partido["PARTIDO_Y"], 1)

        # Se houver outro candidato habilitado no mesmo partido (>= 10% de Droop), ele recebe a legenda
        candidatos_com_habilitado = [
            CandidatoCelula(id_candidato="cand_sem_piso", partido="PARTIDO_X", votos_primeira=10),
            CandidatoCelula(id_candidato="cand_habilitado", partido="PARTIDO_X", votos_primeira=50),
            CandidatoCelula(id_candidato="cand_adversario", partido="PARTIDO_Y", votos_primeira=200),
        ]
        # Total = 10 + 50 + 200 + 240 = 500. Cota Droop = 251. Piso = 25.1.
        # cand_habilitado (50 >= 25.1) recebe 240 de legenda -> 290 >= 251 e vence.
        res2 = apurar_celula_stv(
            candidatos=candidatos_com_habilitado,
            cadeiras=1,
            votos_confianca_partido={"PARTIDO_X": 240},
        )
        self.assertEqual(res2.eleitos, ["cand_habilitado"])
        self.assertEqual(res2.cadeiras_por_partido["PARTIDO_X"], 1)


if __name__ == "__main__":
    unittest.main()
