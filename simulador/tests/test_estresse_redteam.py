# ---------------------------------------------------------------------------
# [BLK-L-007-T] Testes dos Cenários de Estresse do Red Team
# ---------------------------------------------------------------------------
"""Suíte de testes unitários para os experimentos de estresse do Red Team (RT-19 a RT-23).

Valida de forma pura, rápida e determinística:
  - RT-19: O incentivo ao voto estratégico de enterro versus voto sincero (Q-05 / M-06).
  - RT-20: O choque do puxador temático em SP e o transbordamento espacial para outras UFs (M-07 / RT-16).
  - RT-21: A dinâmica de filas, tempo de cabine e colapso operacional da ordenação extensa (U-04).
  - RT-22: A conservação estrita do pacto federativo (desvio 0) sob comparecimento desigual (U-03).
  - RT-23: A sensibilidade e estabilidade do cálculo biproporcional diante de urnas remotas pendentes (U-08).
"""

import unittest

from simulador.src.constantes import (
    BANCADAS_ESTADUAIS,
    COLUNAS_ESTADO,
    COLUNAS_PERMANENTES,
    PISO_PERMANENTE,
    TOTAL_CADEIRAS,
)
from simulador.src.estresse_redteam import (
    ResultadoAtrasoRT23,
    ResultadoComparecimentoRT22,
    ResultadoFilasRT21,
    ResultadoTransbordamentoRT20,
    ResultadoVotoEnterroRT19,
    gerar_matriz_votos_base_27x9,
    simular_atraso_totalizacao_rt23,
    simular_comparecimento_desigual_rt22,
    simular_filas_cabine_rt21,
    simular_transbordamento_puxador_rt20,
    simular_voto_enterro_rt19,
)


class TestVotoEnterroRT19(unittest.TestCase):
    """Testes para o experimento de voto estratégico de enterro (RT-19 / Q-05)."""

    def test_rt19_ganho_voto_enterro_vs_sincero(self) -> None:
        """Comprova que enterrar o 2º voto numa coluna presa ao piso gera ganho para a coluna prioritária."""
        res = simular_voto_enterro_rt19(eleitores_estrategicos=500_000)

        self.assertIsInstance(res, ResultadoVotoEnterroRT19)

        # Invariantes de conservação de assentos do bloco permanente (333 cadeiras)
        self.assertEqual(sum(res.cenario_a_cumulacao.values()), 333)
        self.assertEqual(sum(res.cenario_b_sincero.values()), 333)
        self.assertEqual(sum(res.cenario_c_enterro.values()), 333)

        # Coluna de enterro (Ciência e Trabalho) deve ficar estritamente no piso de 20
        self.assertTrue(res.coluna_enterro_travada_no_piso)
        self.assertEqual(res.cadeiras_ciencia_trabalho["C"], PISO_PERMANENTE)
        self.assertEqual(res.cadeiras_ciencia_trabalho["B"], PISO_PERMANENTE)

        # No Cenário C (enterro), Saúde ganha cadeira marginal que perderia no Cenário B (sincero)
        self.assertGreaterEqual(res.ganho_enterro_vs_sincero, 1)
        self.assertGreater(res.cadeiras_saude["C"], res.cadeiras_saude["B"])

        # Concorrente direta (Educação) é contida no Cenário C em comparação com Cenário B
        self.assertLess(res.cadeiras_educacao["C"], res.cadeiras_educacao["B"])

    def test_rt19_cumulacao_maxima_alavancagem(self) -> None:
        """Regra A (cumulação permitida) oferece a máxima potência de alavancagem para a coluna alvo."""
        res = simular_voto_enterro_rt19()
        # Cumulação (2 votos no alvo) >= Enterro (1 voto alvo) >= Sincero (1 voto alvo + 1 concorrente)
        self.assertGreaterEqual(res.cadeiras_saude["A"], res.cadeiras_saude["C"])
        self.assertGreaterEqual(res.cadeiras_saude["C"], res.cadeiras_saude["B"])

    def test_rt19_validacoes_defensivas(self) -> None:
        """Valida que entradas incoerentes disparam exceções apropriadas."""
        with self.assertRaises(ValueError):
            simular_voto_enterro_rt19(eleitores_estrategicos=-10)
        with self.assertRaises(ValueError):
            simular_voto_enterro_rt19(total_cadeiras_bloco2=0)
        with self.assertRaises(ValueError):
            simular_voto_enterro_rt19(piso_permanente=-1)
        with self.assertRaises(ValueError):
            simular_voto_enterro_rt19(coluna_alvo="COLUNA_INEXISTENTE")


class TestTransbordamentoPuxadorRT20(unittest.TestCase):
    """Testes para o experimento de choque de votos e transbordamento interestadual (RT-20 / M-07)."""

    def test_rt20_choque_puxador_seguranca_sp(self) -> None:
        """Valida o efeito de spillover: choque maciço em SP expande Segurança em SP e transborda para outras UFs."""
        res = simular_transbordamento_puxador_rt20(
            votos_choque=2_500_000,
            coluna_choque="C06_SEGURANCA",
            uf_choque="SP",
        )

        self.assertIsInstance(res, ResultadoTransbordamentoRT20)

        # 1. Conservação aditiva estrita do ganho
        self.assertEqual(
            res.ganho_nacional_coluna,
            res.ganho_sp + res.ganho_outras_ufs,
            "A soma do ganho de SP com o ganho das outras UFs deve fechar o ganho nacional da coluna.",
        )

        # 2. Comprova o ganho nacional e local
        self.assertGreater(res.ganho_nacional_coluna, 0)
        self.assertGreater(res.ganho_sp, 0)

        # 3. Comprova o transbordamento espacial (M-07 e RT-16)
        self.assertGreater(res.ganho_outras_ufs, 0)
        self.assertIn("ES", res.detalhe_outras_ufs)
        self.assertEqual(res.detalhe_outras_ufs["ES"], 1)

        # 4. Invariante federativa de SP: a bancada total de SP permanece 70 cadeiras
        self.assertEqual(sum(res.cadeiras_sp_antes.values()), BANCADAS_ESTADUAIS["SP"])
        self.assertEqual(sum(res.cadeiras_sp_depois.values()), BANCADAS_ESTADUAIS["SP"])

        # 5. Invariante total da Câmara dos Deputados: 513 cadeiras antes e depois
        self.assertEqual(sum(res.cadeiras_nacionais_antes.values()), TOTAL_CADEIRAS)
        self.assertEqual(sum(res.cadeiras_nacionais_depois.values()), TOTAL_CADEIRAS)

    def test_rt20_sem_choque_ganho_nulo(self) -> None:
        """Sem injeção de choque extraordinário, a alocação permanece idêntica."""
        res = simular_transbordamento_puxador_rt20(votos_choque=0)
        self.assertEqual(res.ganho_nacional_coluna, 0)
        self.assertEqual(res.ganho_sp, 0)
        self.assertEqual(res.ganho_outras_ufs, 0)

    def test_rt20_validacoes_defensivas(self) -> None:
        """Valida que parâmetros incorretos levantam ValueError."""
        with self.assertRaises(ValueError):
            simular_transbordamento_puxador_rt20(votos_choque=-500)
        with self.assertRaises(ValueError):
            simular_transbordamento_puxador_rt20(uf_choque="UF_INVALIDA")
        with self.assertRaises(ValueError):
            simular_transbordamento_puxador_rt20(coluna_choque="COLUNA_INVALIDA")


class TestFilasCabineRT21(unittest.TestCase):
    """Testes para o modelo de tempo de cabine e filas de votação (RT-21 / U-04)."""

    def test_rt21_comparacao_tres_cenarios(self) -> None:
        """Comprova a estabilidade do modelo uninominal simples versus colapso da ordenação complexa."""
        res = simular_filas_cabine_rt21(
            eleitores_aptos=400,
            taxa_comparecimento=0.80,  # 320 eleitores
            duracao_minutos=540,       # 9 horas = 32.400 segundos
        )

        self.assertIsInstance(res, ResultadoFilasRT21)

        # 1. Capacidades teóricas máximas das 9 horas
        # 1T atual: 32400 / (57 + 15) = 32400 / 72 = 450
        self.assertEqual(res.cenario_1t_atual.capacidade_maxima_secao, 450)
        # RTP sem ranqueamento: 32400 / (55 + 15) = 32400 / 70 = 462
        self.assertEqual(res.cenario_rtp_sem_ranqueamento.capacidade_maxima_secao, 462)
        # RTP STV enxuto (D-12): 32400 / (72 + 15) = 32400 / 87 = 372
        self.assertEqual(res.cenario_rtp_stv_enxuto.capacidade_maxima_secao, 372)
        # RTP com ranqueamento longo: 32400 / (130 + 15) = 32400 / 145 = 223
        self.assertEqual(res.cenario_rtp_com_ranqueamento.capacidade_maxima_secao, 223)

        # 2. O modelo sem ranqueamento opera de forma limpa e rápida (similar ou melhor que o 1T)
        self.assertLessEqual(res.cenario_rtp_sem_ranqueamento.fila_residual_as_17h, 1)
        self.assertLess(res.cenario_rtp_sem_ranqueamento.minutos_extras_apos_17h, 1.0)
        self.assertGreaterEqual(res.cenario_rtp_sem_ranqueamento.eleitores_atendidos_ate_17h, 319)

        # 2b. O STV enxuto (1 número obrigatório + 2ª opção opcional) mantém folga segura
        self.assertLessEqual(res.cenario_rtp_stv_enxuto.fila_residual_as_17h, 2)
        self.assertLess(res.cenario_rtp_stv_enxuto.minutos_extras_apos_17h, 5.0)
        self.assertGreaterEqual(res.cenario_rtp_stv_enxuto.eleitores_atendidos_ate_17h, 318)

        # 3. O modelo com ranqueamento complexo colapsa operacionalmente (U-04)
        # A capacidade (223) é inferior ao comparecimento (320), restando 97 eleitores às 17h
        self.assertEqual(res.cenario_rtp_com_ranqueamento.eleitores_atendidos_ate_17h, 223)
        self.assertEqual(res.cenario_rtp_com_ranqueamento.fila_residual_as_17h, 97)
        self.assertGreater(res.cenario_rtp_com_ranqueamento.minutos_extras_apos_17h, 200.0)

    def test_rt21_zero_comparecimento(self) -> None:
        """Com comparecimento nulo, a fila permanece vazia e sem minutos extras."""
        res = simular_filas_cabine_rt21(taxa_comparecimento=0.0)
        self.assertEqual(res.cenario_1t_atual.eleitores_atendidos_ate_17h, 0)
        self.assertEqual(res.cenario_1t_atual.fila_residual_as_17h, 0)
        self.assertEqual(res.cenario_1t_atual.minutos_extras_apos_17h, 0.0)

    def test_rt21_validacoes_defensivas(self) -> None:
        """Valida que parâmetros inconsistentes disparam ValueError."""
        with self.assertRaises(ValueError):
            simular_filas_cabine_rt21(eleitores_aptos=0)
        with self.assertRaises(ValueError):
            simular_filas_cabine_rt21(taxa_comparecimento=1.5)
        with self.assertRaises(ValueError):
            simular_filas_cabine_rt21(duracao_minutos=-10)
        with self.assertRaises(ValueError):
            simular_filas_cabine_rt21(tempo_1t_segundos=-5.0)


class TestComparecimentoDesigualRT22(unittest.TestCase):
    """Testes para o comparecimento heterogêneo entre UFs com e sem 2º turno (RT-22 / U-03)."""

    def test_rt22_pacto_federativo_e_deslocamento_tematico(self) -> None:
        """Comprova: desvio de bancadas estaduais é rigorosamente zero e colunas têm leve deslocamento."""
        res = simular_comparecimento_desigual_rt22(
            comparecimento_alto=0.82,
            comparecimento_baixo=0.55,
            comparecimento_base=0.75,
        )

        self.assertIsInstance(res, ResultadoComparecimentoRT22)

        # 1. Comprovação Fundamental do Pacto Federativo (Art. 45 da CF/88):
        # Nenhuma UF perde ou ganha cadeiras no total da Câmara dos Deputados
        self.assertEqual(res.desvio_bancadas_uf, 0)
        for u, b_constitucional in BANCADAS_ESTADUAIS.items():
            self.assertEqual(res.bancadas_uf_heterogeneo[u], b_constitucional)
            self.assertEqual(res.bancadas_uf_homogeneo[u], b_constitucional)

        # 2. Deslocamento temático das colunas nacionais (h_c responde ao comparecimento relativo)
        self.assertGreater(res.deslocamento_colunas, 0)
        self.assertEqual(res.deslocamento_colunas, 2)

        # 3. Conservação exata de 513 cadeiras
        self.assertEqual(sum(res.cadeiras_colunas_homogeneo.values()), TOTAL_CADEIRAS)
        self.assertEqual(sum(res.cadeiras_colunas_heterogeneo.values()), TOTAL_CADEIRAS)

        # 4. Três colunas generalistas intocadas em 60 assentos cada (Invariante do Núcleo de Estado)
        for c in COLUNAS_ESTADO:
            self.assertEqual(res.cadeiras_colunas_homogeneo[c], 60)
            self.assertEqual(res.cadeiras_colunas_heterogeneo[c], 60)

        # 5. Colunas permanentes respeitam rigorosamente o piso de 20
        for c in COLUNAS_PERMANENTES:
            self.assertGreaterEqual(res.cadeiras_colunas_heterogeneo[c], PISO_PERMANENTE)

    def test_rt22_comparecimento_igual_gera_deslocamento_zero(self) -> None:
        """Quando o comparecimento é idêntico em todas as UFs, o deslocamento temático é estritamente zero."""
        res = simular_comparecimento_desigual_rt22(
            comparecimento_alto=0.75,
            comparecimento_baixo=0.75,
            comparecimento_base=0.75,
        )
        self.assertEqual(res.desvio_bancadas_uf, 0)
        self.assertEqual(res.deslocamento_colunas, 0)
        self.assertEqual(res.cadeiras_colunas_homogeneo, res.cadeiras_colunas_heterogeneo)

    def test_rt22_validacoes_defensivas(self) -> None:
        """Testa rejeição de taxas inválidas de comparecimento."""
        with self.assertRaises(ValueError):
            simular_comparecimento_desigual_rt22(comparecimento_alto=1.2)
        with self.assertRaises(ValueError):
            simular_comparecimento_desigual_rt22(comparecimento_baixo=-0.1)


class TestAtrasoTotalizacaoRT23(unittest.TestCase):
    """Testes para o experimento de sensibilidade a urnas pendentes da apuração (RT-23 / U-08)."""

    def test_rt23_estabilidade_urnas_remotas(self) -> None:
        """Comprova que 2% de urnas pendentes concentradas na Amazônia alteram apenas margem restrita de cadeiras."""
        res = simular_atraso_totalizacao_rt23(fracao_pendente=0.02)

        self.assertIsInstance(res, ResultadoAtrasoRT23)

        # 1. Conservação global das 513 cadeiras nos dois estados da totalização
        self.assertEqual(sum(res.colunas_parcial.values()), TOTAL_CADEIRAS)
        self.assertEqual(sum(res.colunas_final.values()), TOTAL_CADEIRAS)

        # 2. Estabilidade parlamentar: com 98% apurado, o resultado já está mais de 99% cristalizado
        # Apenas 2 assentos (em 513) mudam com os 2% restantes de urnas
        self.assertLessEqual(res.cadeiras_alteradas, 4)
        self.assertLessEqual(res.colunas_alteradas, 4)
        self.assertGreaterEqual(res.cadeiras_alteradas, 1)

        # 3. UFs afetadas são identificadas com clareza
        self.assertIsInstance(res.ufs_afetadas, list)
        self.assertGreater(len(res.ufs_afetadas), 0)

    def test_rt23_pendencia_zero_nenhuma_alteracao(self) -> None:
        """Com fração pendente zero (100% totalizado), a matriz parcial é idêntica à final."""
        res = simular_atraso_totalizacao_rt23(fracao_pendente=0.0)
        self.assertEqual(res.cadeiras_alteradas, 0)
        self.assertEqual(res.colunas_alteradas, 0)
        self.assertEqual(res.deslocamento_nacional_colunas, 0)
        self.assertEqual(res.ufs_afetadas, [])

    def test_rt23_validacoes_defensivas(self) -> None:
        """Testa validações de parâmetros para a totalização."""
        with self.assertRaises(ValueError):
            simular_atraso_totalizacao_rt23(fracao_pendente=-0.01)
        with self.assertRaises(ValueError):
            simular_atraso_totalizacao_rt23(fracao_pendente=1.0)
        with self.assertRaises(ValueError):
            simular_atraso_totalizacao_rt23(ufs_remotas=["UF_INEXISTENTE"])


class TestDeterminismoReproduzibilidade(unittest.TestCase):
    """Garante que todas as simulações do Red Team são 100% determinísticas e idempotentes."""

    def test_determinismo_reproduzibilidade_absoluta(self) -> None:
        """Execuções repetidas com os mesmos parâmetros devem produzir exatamente o mesmo resultado."""
        r19_a = simular_voto_enterro_rt19()
        r19_b = simular_voto_enterro_rt19()
        self.assertEqual(r19_a, r19_b)

        r20_a = simular_transbordamento_puxador_rt20()
        r20_b = simular_transbordamento_puxador_rt20()
        self.assertEqual(r20_a, r20_b)

        r21_a = simular_filas_cabine_rt21()
        r21_b = simular_filas_cabine_rt21()
        self.assertEqual(r21_a, r21_b)

        r22_a = simular_comparecimento_desigual_rt22()
        r22_b = simular_comparecimento_desigual_rt22()
        self.assertEqual(r22_a, r22_b)

        r23_a = simular_atraso_totalizacao_rt23()
        r23_b = simular_atraso_totalizacao_rt23()
        self.assertEqual(r23_a, r23_b)


if __name__ == "__main__":
    unittest.main()
