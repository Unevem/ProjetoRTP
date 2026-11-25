# ---------------------------------------------------------------------------
# [BLK-L-005-T] Testes de Métricas Eleitorais e Auditoria de Invariantes
# ---------------------------------------------------------------------------
"""Suíte de testes unitários para o módulo de métricas eleitorais e auditoria constitucional.

Valida a exatidão do cálculo do Índice de Gallagher (LSq), do Índice de Herfindahl (HHI),
do número efetivo de partidos (N_eff / Laakso-Taagepera), da curva de sobrevivência partidária
sob o Red Team RT-20, e a integridade da rotina de auditoria das 6 invariantes constitucionais
do modelo de Representação Temática Proporcional (RTP).
"""

import copy
import math
import unittest

from simulador.src.constantes import (
    BANCADAS_ESTADUAIS,
    COLUNAS_ESTADO,
    COLUNAS_MISSAO_PADRAO,
    COLUNAS_PERMANENTES,
    PISO_GENERALISTA,
    PISO_PERMANENTE,
    TOTAL_CADEIRAS,
)
from simulador.src.metricas import (
    RelatorioInvariantes,
    auditar_invariantes_constitucionais,
    curva_sobrevivencia_partidaria,
    indice_gallagher,
    indice_herfindahl,
    numero_efetivo_partidos,
)


class TestIndiceGallagher(unittest.TestCase):
    """Testes para o cálculo do índice de desproporcionalidade de Gallagher (LSq)."""

    def test_proporcionalidade_perfeita_retorna_zero(self) -> None:
        """Quando a distribuição de cadeiras espelha com exatidão os votos, LSq = 0.0."""
        votos = {"A": 60, "B": 40}
        cadeiras = {"A": 6, "B": 4}
        resultado = indice_gallagher(votos, cadeiras)
        self.assertAlmostEqual(resultado, 0.0, places=9)

    def test_caso_conhecido_literatura_eleitoral(self) -> None:
        """Cenário clássico da literatura eleitoral com valor analítico fechado.

        Votos: A (50%), B (30%), C (20%) -> Total 100 votos.
        Cadeiras: A (60%), B (30%), C (10%) -> Total 10 cadeiras.
        Diferenças percentuais: A = -10, B = 0, C = +10.
        Soma das diferenças ao quadrado = 100 + 0 + 100 = 200.
        LSq = sqrt(0.5 * 200) = sqrt(100) = 10.0 pontos percentuais.
        """
        votos = {"A": 50, "B": 30, "C": 20}
        cadeiras = {"A": 6, "B": 3, "C": 1}
        resultado = indice_gallagher(votos, cadeiras)
        self.assertAlmostEqual(resultado, 10.0, places=9)

    def test_partido_sem_cadeiras_e_partido_sem_votos(self) -> None:
        """Testa o cômputo correto quando há descompasso entre as legendas dos conjuntos."""
        votos = {"A": 50, "B": 40, "C": 10}
        cadeiras = {"A": 6, "B": 4}  # C recebeu 10% dos votos mas 0 cadeiras
        # Total votos 100, Total cadeiras 10
        # A: 50% votos, 60% cadeiras -> diff = -10, sq = 100
        # B: 40% votos, 40% cadeiras -> diff = 0, sq = 0
        # C: 10% votos, 0% cadeiras  -> diff = 10, sq = 100
        # LSq = sqrt(0.5 * 200) = 10.0
        resultado = indice_gallagher(votos, cadeiras)
        self.assertAlmostEqual(resultado, 10.0, places=9)

    def test_votos_e_cadeiras_vazios_retorna_zero(self) -> None:
        """Se ambos os mapeamentos estiverem vazios, a desproporcionalidade é 0.0."""
        self.assertEqual(indice_gallagher({}, {}), 0.0)

    def test_voto_negativo_levanta_value_error(self) -> None:
        """Contagem negativa de votos deve levantar ValueError."""
        with self.assertRaises(ValueError):
            indice_gallagher({"A": -10, "B": 100}, {"A": 1, "B": 9})

    def test_cadeira_negativa_levanta_value_error(self) -> None:
        """Contagem negativa de cadeiras deve levantar ValueError."""
        with self.assertRaises(ValueError):
            indice_gallagher({"A": 100, "B": 100}, {"A": -1, "B": 10})

    def test_apenas_um_total_zero_levanta_value_error(self) -> None:
        """Se houver votos mas 0 cadeiras (ou vice-versa), levanta ValueError."""
        with self.assertRaises(ValueError):
            indice_gallagher({"A": 100}, {"A": 0})
        with self.assertRaises(ValueError):
            indice_gallagher({"A": 0}, {"A": 10})


class TestFragmentacaoEConcentracao(unittest.TestCase):
    """Testes para o número efetivo de partidos (N_eff) e índice Herfindahl (HHI)."""

    def test_quatro_partidos_simetricos(self) -> None:
        """4 partidos iguais devem resultar em N_eff = 4.0 e HHI = 0.25."""
        contagens = {"A": 25, "B": 25, "C": 25, "D": 25}
        self.assertAlmostEqual(indice_herfindahl(contagens), 0.25, places=9)
        self.assertAlmostEqual(numero_efetivo_partidos(contagens), 4.0, places=9)

    def test_um_partido_monopolista(self) -> None:
        """Monopólio absoluto de 1 partido resulta em N_eff = 1.0 e HHI = 1.0."""
        contagens = {"A": 100}
        self.assertAlmostEqual(indice_herfindahl(contagens), 1.0, places=9)
        self.assertAlmostEqual(numero_efetivo_partidos(contagens), 1.0, places=9)

    def test_distribuicao_assimetrica(self) -> None:
        """Duas forças maiores e duas menores testam ponderação quadrática."""
        contagens = {"A": 40, "B": 40, "C": 10, "D": 10}
        # p_A = 0.4, p_B = 0.4, p_C = 0.1, p_D = 0.1
        # HHI = 0.16 + 0.16 + 0.01 + 0.01 = 0.34
        # N_eff = 1 / 0.34 = 2.941176...
        hhi = indice_herfindahl(contagens)
        neff = numero_efetivo_partidos(contagens)
        self.assertAlmostEqual(hhi, 0.34, places=9)
        self.assertAlmostEqual(neff, 1.0 / 0.34, places=9)

    def test_contagens_zeradas_ou_vazias_retornam_zero(self) -> None:
        """Mapeamentos vazios ou com todas contagens zero retornam 0.0."""
        self.assertEqual(indice_herfindahl({}), 0.0)
        self.assertEqual(numero_efetivo_partidos({}), 0.0)
        self.assertEqual(indice_herfindahl({"A": 0, "B": 0}), 0.0)
        self.assertEqual(numero_efetivo_partidos({"A": 0, "B": 0}), 0.0)

    def test_contagem_negativa_levanta_value_error(self) -> None:
        """Contagens negativas devem levantar ValueError em ambos os índices."""
        with self.assertRaises(ValueError):
            indice_herfindahl({"A": -5, "B": 10})
        with self.assertRaises(ValueError):
            numero_efetivo_partidos({"A": 5, "B": -1})


class TestCurvaSobrevivenciaPartidaria(unittest.TestCase):
    """Testes para a métrica de sobrevivência parlamentar de legendas (RT-20)."""

    def test_tres_faixas_comportamento(self) -> None:
        """Verifica taxas diferenciadas nas 3 faixas [1%, 3%), [3%, 6%) e [6%, 10%)."""
        # Total de votos: 10.000 votos
        votos = {
            # Faixa 1% a 3% (100 a 299 votos): 2 partidos, 1 sobreviveu
            "P_1A": 150,  # 1.5% -> 1 cadeira
            "P_1B": 250,  # 2.5% -> 0 cadeiras
            # Faixa 3% a 6% (300 a 599 votos): 2 partidos, 2 sobreviveram
            "P_2A": 350,  # 3.5% -> 2 cadeiras
            "P_2B": 500,  # 5.0% -> 3 cadeiras
            # Faixa 6% a 10% (600 a 999 votos): 1 partido, 0 sobreviveram
            "P_3A": 800,  # 8.0% -> 0 cadeiras
            # Fora das faixas (<1% ou >=10%)
            "P_MICRO": 50,    # 0.5%
            "P_MAJOR": 7900,  # 79.0%
        }
        cadeiras = {
            "P_1A": 1,
            "P_1B": 0,
            "P_2A": 2,
            "P_2B": 3,
            "P_3A": 0,
            "P_MICRO": 0,
            "P_MAJOR": 40,
        }

        resultado = curva_sobrevivencia_partidaria(votos, cadeiras)

        self.assertAlmostEqual(resultado["1%_a_3%"], 0.5, places=9)
        self.assertAlmostEqual(resultado["3%_a_6%"], 1.0, places=9)
        self.assertAlmostEqual(resultado["6%_a_10%"], 0.0, places=9)

    def test_faixa_sem_partidos_retorna_zero(self) -> None:
        """Faixas que não possuem legendas concorrentes retornam 0.0."""
        votos = {"P_GRANDE": 1000}
        cadeiras = {"P_GRANDE": 10}
        resultado = curva_sobrevivencia_partidaria(votos, cadeiras)
        self.assertEqual(
            resultado,
            {"1%_a_3%": 0.0, "3%_a_6%": 0.0, "6%_a_10%": 0.0},
        )

    def test_limites_exatos_de_intervalo(self) -> None:
        """Verifica que intervalos são semiabertos [inf, sup)."""
        # Total de votos = 100
        votos = {
            "P_1": 1,    # Exatamente 1.0% -> pertence a "1%_a_3%"
            "P_3": 3,    # Exatamente 3.0% -> pertence a "3%_a_6%"
            "P_6": 6,    # Exatamente 6.0% -> pertence a "6%_a_10%"
            "P_10": 10,  # Exatamente 10.0% -> fora (>=10%)
            "P_80": 80,  # 80.0% -> fora
        }
        cadeiras = {
            "P_1": 1,
            "P_3": 1,
            "P_6": 1,
            "P_10": 2,
            "P_80": 20,
        }
        resultado = curva_sobrevivencia_partidaria(votos, cadeiras)
        self.assertEqual(resultado["1%_a_3%"], 1.0)
        self.assertEqual(resultado["3%_a_6%"], 1.0)
        self.assertEqual(resultado["6%_a_10%"], 1.0)

    def test_votos_zerados_retorna_zeros(self) -> None:
        """Total de votos igual a zero retorna taxa 0.0 em todas as faixas."""
        resultado = curva_sobrevivencia_partidaria({}, {})
        self.assertEqual(
            resultado,
            {"1%_a_3%": 0.0, "3%_a_6%": 0.0, "6%_a_10%": 0.0},
        )

    def test_valores_negativos_levantam_erro(self) -> None:
        """Votos ou cadeiras negativas levantam ValueError."""
        with self.assertRaises(ValueError):
            curva_sobrevivencia_partidaria({"A": -10}, {"A": 1})
        with self.assertRaises(ValueError):
            curva_sobrevivencia_partidaria({"A": 10}, {"A": -1})


class TestAuditoriaInvariantesConstitucionais(unittest.TestCase):
    """Testes exaustivos para a auditoria de invariantes constitucionais."""

    def setUp(self) -> None:
        """Monta um cenário canônico sintético perfeitamente válido de 27 UFs x 12 Colunas."""
        self.bancadas_uf = dict(BANCADAS_ESTADUAIS)
        self.colunas_estado = COLUNAS_ESTADO
        self.colunas_permanentes = COLUNAS_PERMANENTES
        self.colunas_missao = COLUNAS_MISSAO_PADRAO
        self.todas_colunas = (
            self.colunas_estado + self.colunas_permanentes + self.colunas_missao
        )

        # Totais planejados por coluna (fecham 513)
        # Estado (3 x 60 = 180)
        # Permanentes (5 x 40 + 1 x 43 = 243, todas >= 20)
        # Missão (3 x 30 = 90)
        self.cadeiras_colunas = {
            "C01_ECONOMIA": 60,
            "C02_JUSTICA": 60,
            "C03_SOCIAL": 60,
            "C04_SAUDE": 40,
            "C05_EDUCACAO": 40,
            "C06_SEGURANCA": 40,
            "C07_INFRAESTRUTURA": 40,
            "C08_AGRO_AMBIENTE": 40,
            "C09_CIENCIA_TRABALHO": 43,
            "C10_MISSAO_1": 30,
            "C11_MISSAO_2": 30,
            "C12_MISSAO_3": 30,
        }

        # Tetos de missão u_e = floor(bancada * 0.20)
        self.tetos_missao = {
            uf: math.floor(b * 0.20) for uf, b in self.bancadas_uf.items()
        }

        # Constrói matriz perfeitamente válida
        self.matriz_valida: dict[str, dict[str, int]] = {
            uf: {c: 0 for c in self.todas_colunas} for uf in self.bancadas_uf
        }

        # 1. Distribuir missões (90 vagas cabem na soma dos tetos de 91)
        # SP usa 13 (teto 14); as demais 26 UFs usam exatamente seu teto nominal
        cols_missao = list(self.colunas_missao)
        capacidade_missao = {c: self.cadeiras_colunas[c] for c in cols_missao}
        for uf, teto in self.tetos_missao.items():
            vagas_missao_uf = teto - 1 if uf == "SP" else teto
            for c in cols_missao:
                alocar = min(vagas_missao_uf, capacidade_missao[c])
                self.matriz_valida[uf][c] += alocar
                capacidade_missao[c] -= alocar
                vagas_missao_uf -= alocar
                if vagas_missao_uf == 0:
                    break

        # 2. Distribuir não-missões (423 vagas)
        cols_resto = list(self.colunas_estado + self.colunas_permanentes)
        capacidade_resto = {c: self.cadeiras_colunas[c] for c in cols_resto}
        for uf, bancada in self.bancadas_uf.items():
            vagas_resto_uf = bancada - sum(
                self.matriz_valida[uf][c] for c in cols_missao
            )
            for c in cols_resto:
                alocar = min(vagas_resto_uf, capacidade_resto[c])
                self.matriz_valida[uf][c] += alocar
                capacidade_resto[c] -= alocar
                vagas_resto_uf -= alocar
                if vagas_resto_uf == 0:
                    break

    def test_matriz_valida_passa_com_sucesso(self) -> None:
        """A matriz perfeitamente construída deve satisfazer todas as invariantes."""
        relatorio = auditar_invariantes_constitucionais(
            matriz_completa=self.matriz_valida,
            bancadas_uf=self.bancadas_uf,
            cadeiras_colunas=self.cadeiras_colunas,
            tetos_missao_uf=self.tetos_missao,
        )

        self.assertTrue(relatorio.aprovado)
        self.assertTrue(relatorio.soma_total_513)
        self.assertTrue(relatorio.pacto_federativo_intacto)
        self.assertTrue(relatorio.fechamento_tematico_intacto)
        self.assertTrue(relatorio.nucleo_estado_60_fixo)
        self.assertTrue(relatorio.pisos_permanentes_respeitados)
        self.assertTrue(relatorio.tetos_missao_respeitados)
        self.assertEqual(relatorio.erros, [])

    def test_violacao_pacto_federativo_soma_uf_errada(self) -> None:
        """Altera a bancada de uma UF (SP ganha +1 cadeira); deve falhar o Pacto Federativo."""
        matriz = copy.deepcopy(self.matriz_valida)
        matriz["SP"]["C01_ECONOMIA"] += 1  # SP passa a ter 71 em vez de 70

        relatorio = auditar_invariantes_constitucionais(
            matriz_completa=matriz,
            bancadas_uf=self.bancadas_uf,
            cadeiras_colunas=self.cadeiras_colunas,
            tetos_missao_uf=self.tetos_missao,
        )

        self.assertFalse(relatorio.aprovado)
        self.assertFalse(relatorio.pacto_federativo_intacto)
        self.assertFalse(relatorio.soma_total_513)
        self.assertTrue(
            any("Pacto federativo violado na UF 'SP'" in e for e in relatorio.erros)
        )

    def test_violacao_pacto_federativo_com_soma_total_conservada(self) -> None:
        """SP ganha 1 cadeira e MG perde 1 na mesma coluna: soma total 513 fecha mas pacto é violado."""
        matriz = copy.deepcopy(self.matriz_valida)
        matriz["SP"]["C01_ECONOMIA"] += 1
        matriz["MG"]["C01_ECONOMIA"] -= 1

        relatorio = auditar_invariantes_constitucionais(
            matriz_completa=matriz,
            bancadas_uf=self.bancadas_uf,
            cadeiras_colunas=self.cadeiras_colunas,
            tetos_missao_uf=self.tetos_missao,
        )

        self.assertFalse(relatorio.aprovado)
        self.assertFalse(relatorio.pacto_federativo_intacto)
        self.assertTrue(relatorio.soma_total_513)
        self.assertTrue(relatorio.fechamento_tematico_intacto)
        self.assertTrue(
            any("Pacto federativo violado na UF 'SP'" in e for e in relatorio.erros)
        )
        self.assertTrue(
            any("Pacto federativo violado na UF 'MG'" in e for e in relatorio.erros)
        )

    def test_violacao_nucleo_estado_coluna_generalista_com_59(self) -> None:
        """Uma coluna de Estado com 59 cadeiras deve falhar a invariante do Núcleo de Estado."""
        matriz = copy.deepcopy(self.matriz_valida)
        cadeiras_cols = copy.deepcopy(self.cadeiras_colunas)

        # Move 1 vaga de C01 (Estado) para C04 (Permanente) mantendo bancada de SP intacta
        matriz["SP"]["C01_ECONOMIA"] -= 1
        matriz["SP"]["C04_SAUDE"] += 1
        cadeiras_cols["C01_ECONOMIA"] = 59
        cadeiras_cols["C04_SAUDE"] = 41

        relatorio = auditar_invariantes_constitucionais(
            matriz_completa=matriz,
            bancadas_uf=self.bancadas_uf,
            cadeiras_colunas=cadeiras_cols,
            tetos_missao_uf=self.tetos_missao,
        )

        self.assertFalse(relatorio.aprovado)
        self.assertFalse(relatorio.nucleo_estado_60_fixo)
        self.assertTrue(
            any("Núcleo de Estado violado na coluna generalista 'C01_ECONOMIA'" in e for e in relatorio.erros)
        )

    def test_violacao_piso_permanente_com_19_cadeiras(self) -> None:
        """Coluna permanente com 19 cadeiras viola a garantia de piso temático (PISO_PERMANENTE=20)."""
        matriz = copy.deepcopy(self.matriz_valida)
        cadeiras_cols = copy.deepcopy(self.cadeiras_colunas)

        # Reduz C04 para 19 e compensa em C05 para manter bancadas de SP
        # Em matriz_valida, SP tem cadeiras em C04
        vagas_a_tirar = self.cadeiras_colunas["C04_SAUDE"] - 19  # 40 - 19 = 21 vagas
        # Remove 21 vagas de C04 de SP e adiciona em C05
        matriz["SP"]["C04_SAUDE"] -= vagas_a_tirar
        matriz["SP"]["C05_EDUCACAO"] += vagas_a_tirar
        cadeiras_cols["C04_SAUDE"] = 19
        cadeiras_cols["C05_EDUCACAO"] += vagas_a_tirar

        relatorio = auditar_invariantes_constitucionais(
            matriz_completa=matriz,
            bancadas_uf=self.bancadas_uf,
            cadeiras_colunas=cadeiras_cols,
            tetos_missao_uf=self.tetos_missao,
        )

        self.assertFalse(relatorio.aprovado)
        self.assertFalse(relatorio.pisos_permanentes_respeitados)
        self.assertTrue(
            any("Piso permanente violado na coluna 'C04_SAUDE'" in e for e in relatorio.erros)
        )

    def test_violacao_uf_estoura_teto_missao(self) -> None:
        """UF estoura o teto de missão institucional (u_e)."""
        matriz = copy.deepcopy(self.matriz_valida)
        # RR tem bancada 8 e teto de missão 1
        # Move 1 cadeira de RR de C01 para C10
        matriz["RR"]["C01_ECONOMIA"] -= 1
        matriz["RR"]["C10_MISSAO_1"] += 1
        # Compensa em SP para manter fechamento das colunas
        matriz["SP"]["C01_ECONOMIA"] += 1
        matriz["SP"]["C10_MISSAO_1"] -= 1

        relatorio = auditar_invariantes_constitucionais(
            matriz_completa=matriz,
            bancadas_uf=self.bancadas_uf,
            cadeiras_colunas=self.cadeiras_colunas,
            tetos_missao_uf=self.tetos_missao,
        )

        self.assertFalse(relatorio.aprovado)
        self.assertFalse(relatorio.tetos_missao_respeitados)
        self.assertTrue(
            any("Teto de missão violado na UF 'RR'" in e for e in relatorio.erros)
        )

    def test_violacao_fechamento_tematico_coluna(self) -> None:
        """Soma da coluna na matriz diverge do valor esperado em cadeiras_colunas."""
        cadeiras_cols = copy.deepcopy(self.cadeiras_colunas)
        cadeiras_cols["C01_ECONOMIA"] = 61  # Dicionário espera 61, mas matriz soma 60

        relatorio = auditar_invariantes_constitucionais(
            matriz_completa=self.matriz_valida,
            bancadas_uf=self.bancadas_uf,
            cadeiras_colunas=cadeiras_cols,
            tetos_missao_uf=self.tetos_missao,
        )

        self.assertFalse(relatorio.aprovado)
        self.assertFalse(relatorio.fechamento_tematico_intacto)
        self.assertTrue(
            any("Fechamento temático violado na coluna 'C01_ECONOMIA'" in e for e in relatorio.erros)
        )

    def test_violacao_cadeira_negativa_detectada(self) -> None:
        """Presença de valor negativo em qualquer célula invalida a auditoria."""
        matriz = copy.deepcopy(self.matriz_valida)
        matriz["SP"]["C01_ECONOMIA"] = -1

        relatorio = auditar_invariantes_constitucionais(
            matriz_completa=matriz,
            bancadas_uf=self.bancadas_uf,
            cadeiras_colunas=self.cadeiras_colunas,
            tetos_missao_uf=self.tetos_missao,
        )

        self.assertFalse(relatorio.aprovado)
        self.assertTrue(
            any("Cadeira negativa na célula ('SP', 'C01_ECONOMIA')" in e for e in relatorio.erros)
        )

    def test_uf_ausente_na_matriz_reprovada(self) -> None:
        """Se uma UF das bancadas oficiais não estiver na matriz, reprova."""
        matriz = copy.deepcopy(self.matriz_valida)
        del matriz["TO"]

        relatorio = auditar_invariantes_constitucionais(
            matriz_completa=matriz,
            bancadas_uf=self.bancadas_uf,
            cadeiras_colunas=self.cadeiras_colunas,
            tetos_missao_uf=self.tetos_missao,
        )

        self.assertFalse(relatorio.aprovado)
        self.assertFalse(relatorio.pacto_federativo_intacto)
        self.assertTrue(
            any("UF 'TO' ausente" in e for e in relatorio.erros)
        )

    def test_teto_missao_ausente_para_uf(self) -> None:
        """Se faltar o teto de missão de uma UF no mapeamento de tetos, reprova."""
        tetos = copy.deepcopy(self.tetos_missao)
        del tetos["AC"]

        relatorio = auditar_invariantes_constitucionais(
            matriz_completa=self.matriz_valida,
            bancadas_uf=self.bancadas_uf,
            cadeiras_colunas=self.cadeiras_colunas,
            tetos_missao_uf=tetos,
        )

        self.assertFalse(relatorio.aprovado)
        self.assertFalse(relatorio.tetos_missao_respeitados)
        self.assertTrue(
            any("Teto de missão ausente para a UF 'AC'" in e for e in relatorio.erros)
        )


if __name__ == "__main__":
    unittest.main()
