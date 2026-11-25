# ---------------------------------------------------------------------------
# [(BLK-L-001 & BLK-L-002)-T] Testes de Constantes Federativas e Teto de Missão
# ---------------------------------------------------------------------------
"""Suíte de testes unitários para constantes constitucionais e teto de missão.

Valida as bancadas das 27 UFs (Art. 45 da CF/88), macrorregiões do IBGE,
o arredondamento determinístico de Sainte-Laguë (RT-01), o teto nominal tau_e,
o teto efetivo u_e e o cálculo da taxa de votos válidos com 2 telas (RT-04 e D-15).
"""

import unittest

from simulador.src.constantes import (
    BANCADAS_ESTADUAIS,
    CADEIRAS_BLOCO_1,
    CADEIRAS_LIVRES,
    COLUNAS_ESTADO,
    COLUNAS_MISSAO_PADRAO,
    COLUNAS_PERMANENTES,
    MACRORREGIOES,
    PISO_GENERALISTA,
    PISO_PERMANENTE,
    RHO_TETO_MISSAO,
    TODAS_COLUNAS_PADRAO,
    TOTAL_CADEIRAS,
)
from simulador.src.teto_missao import (
    arredondar_sainte_lague,
    calcular_taxa_validos_voto4,
    calcular_teto_efetivo_uf,
    calcular_tetos_nacionais,
    calcular_tau_uf,
)


class TestConstantesFederativas(unittest.TestCase):
    """Validações das constantes constitucionais e bancadas federativas (BLK-L-001)."""

    def test_total_cadeiras_e_soma_bancadas(self) -> None:
        """A soma das 27 bancadas estaduais deve ser exatamente 513 cadeiras."""
        self.assertEqual(len(BANCADAS_ESTADUAIS), 27)
        self.assertEqual(sum(BANCADAS_ESTADUAIS.values()), TOTAL_CADEIRAS)
        self.assertEqual(TOTAL_CADEIRAS, 513)

    def test_bancadas_especificas(self) -> None:
        """Verifica bancadas de referência (extremos e intermediárias)."""
        self.assertEqual(BANCADAS_ESTADUAIS["SP"], 70)
        self.assertEqual(BANCADAS_ESTADUAIS["MG"], 53)
        self.assertEqual(BANCADAS_ESTADUAIS["RJ"], 46)
        self.assertEqual(BANCADAS_ESTADUAIS["BA"], 39)
        self.assertEqual(BANCADAS_ESTADUAIS["RS"], 31)
        self.assertEqual(BANCADAS_ESTADUAIS["PR"], 30)
        self.assertEqual(BANCADAS_ESTADUAIS["PE"], 25)
        self.assertEqual(BANCADAS_ESTADUAIS["CE"], 22)
        self.assertEqual(BANCADAS_ESTADUAIS["MA"], 18)
        self.assertEqual(BANCADAS_ESTADUAIS["GO"], 17)
        self.assertEqual(BANCADAS_ESTADUAIS["PA"], 17)
        self.assertEqual(BANCADAS_ESTADUAIS["SC"], 16)
        self.assertEqual(BANCADAS_ESTADUAIS["PB"], 12)
        self.assertEqual(BANCADAS_ESTADUAIS["ES"], 10)
        self.assertEqual(BANCADAS_ESTADUAIS["PI"], 10)
        self.assertEqual(BANCADAS_ESTADUAIS["AL"], 9)

        # 11 UFs no piso constitucional de 8 cadeiras
        ufs_piso_8 = ("AC", "AM", "AP", "DF", "MS", "MT", "RN", "RO", "RR", "SE", "TO")
        for uf in ufs_piso_8:
            with self.subTest(uf=uf):
                self.assertEqual(BANCADAS_ESTADUAIS[uf], 8)

    def test_macrorregioes_ibge(self) -> None:
        """Todas as 27 UFs devem estar mapeadas para uma das 5 macrorregiões oficiais."""
        self.assertEqual(len(MACRORREGIOES), 27)
        self.assertEqual(set(BANCADAS_ESTADUAIS.keys()), set(MACRORREGIOES.keys()))

        regioes_validas = {"N", "NE", "CO", "SE", "S"}
        self.assertTrue(set(MACRORREGIOES.values()).issubset(regioes_validas))

        # Contagem oficial de UFs por macrorregião
        contagem = {reg: sum(1 for r in MACRORREGIOES.values() if r == reg) for reg in regioes_validas}
        self.assertEqual(contagem["N"], 7)
        self.assertEqual(contagem["NE"], 9)
        self.assertEqual(contagem["CO"], 4)
        self.assertEqual(contagem["SE"], 4)
        self.assertEqual(contagem["S"], 3)

    def test_divisao_de_blocos_e_pisos(self) -> None:
        """Verifica a coerência das cadeiras de bloco e pisos constitucionais."""
        self.assertEqual(CADEIRAS_BLOCO_1 + CADEIRAS_LIVRES, TOTAL_CADEIRAS)
        self.assertEqual(CADEIRAS_BLOCO_1, 180)
        self.assertEqual(CADEIRAS_LIVRES, 333)
        self.assertEqual(PISO_GENERALISTA, 60)
        self.assertEqual(PISO_PERMANENTE, 20)
        self.assertAlmostEqual(RHO_TETO_MISSAO, 0.20, places=6)

    def test_colunas_tematicas(self) -> None:
        """Verifica as 12 colunas temáticas e sua partição por bloco."""
        self.assertEqual(len(COLUNAS_ESTADO), 3)
        self.assertEqual(len(COLUNAS_PERMANENTES), 6)
        self.assertEqual(len(COLUNAS_MISSAO_PADRAO), 3)
        self.assertEqual(len(TODAS_COLUNAS_PADRAO), 12)
        self.assertEqual(
            TODAS_COLUNAS_PADRAO,
            COLUNAS_ESTADO + COLUNAS_PERMANENTES + COLUNAS_MISSAO_PADRAO,
        )


class TestArredondamentoSainteLague(unittest.TestCase):
    """Validações do algoritmo de arredondamento determinístico de Sainte-Laguë."""

    def test_contraste_com_round_nativo_python(self) -> None:
        """Comprova que round(0.5) dá 0 em Python nativo, mas Sainte-Laguë deve dar 1."""
        self.assertEqual(round(0.5), 0, "Python nativo deve realizar round-half-to-even")
        self.assertEqual(arredondar_sainte_lague(0.5), 1, "Sainte-Laguë exige 0.5 -> 1")

    def test_fronteiras_fracionarias(self) -> None:
        """Testa valores logo abaixo e logo acima da fronteira de 0.5."""
        self.assertEqual(arredondar_sainte_lague(0.0), 0)
        self.assertEqual(arredondar_sainte_lague(0.49), 0)
        self.assertEqual(arredondar_sainte_lague(0.499999), 0)
        self.assertEqual(arredondar_sainte_lague(0.50), 1)
        self.assertEqual(arredondar_sainte_lague(0.500001), 1)
        self.assertEqual(arredondar_sainte_lague(0.80), 1)
        self.assertEqual(arredondar_sainte_lague(1.0), 1)
        self.assertEqual(arredondar_sainte_lague(1.49), 1)
        self.assertEqual(arredondar_sainte_lague(1.50), 2)
        self.assertEqual(arredondar_sainte_lague(9.8), 10)

    def test_valor_negativo_lanca_excecao(self) -> None:
        """Valores negativos não fazem sentido em contagem de cadeiras e devem falhar."""
        with self.assertRaises(ValueError):
            arredondar_sainte_lague(-0.01)


class TestTetoMissao(unittest.TestCase):
    """Validações do cálculo de tau_e, u_e e regras de encolhimento (BLK-L-002)."""

    def test_soma_tau_nacional_exata_91(self) -> None:
        """A soma do teto nominal tau_e para todas as 27 UFs deve totalizar exatamente 91 cadeiras."""
        taus = {uf: calcular_tau_uf(bancada) for uf, bancada in BANCADAS_ESTADUAIS.items()}
        self.assertEqual(sum(taus.values()), 91)

    def test_tau_por_tamanho_de_bancada(self) -> None:
        """Valida tau_e para UFs emblemáticas."""
        self.assertEqual(calcular_tau_uf(8), 1)    # 8 * 0.2 = 1.6 -> 1
        self.assertEqual(calcular_tau_uf(9), 1)    # AL: 9 * 0.2 = 1.8 -> 1
        self.assertEqual(calcular_tau_uf(10), 2)   # ES, PI: 10 * 0.2 = 2.0 -> 2
        self.assertEqual(calcular_tau_uf(12), 2)   # PB: 12 * 0.2 = 2.4 -> 2
        self.assertEqual(calcular_tau_uf(53), 10)  # MG: 53 * 0.2 = 10.6 -> 10
        self.assertEqual(calcular_tau_uf(70), 14)  # SP: 70 * 0.2 = 14.0 -> 14

    def test_regra_rt01_uf_oito_cadeiras_roraima(self) -> None:
        """Aplica os cenários da decisão RT-01 para UF com bancada mínima (8 cadeiras, tau=1)."""
        bancada_rr = 8

        # Taxa 1.0 (100% válidos) -> 1 * 1.0 = 1.0 -> 1
        self.assertEqual(calcular_teto_efetivo_uf(bancada_rr, 1.0), 1)

        # Taxa 0.80 (80% válidos) -> 1 * 0.80 = 0.80 -> 1
        self.assertEqual(calcular_teto_efetivo_uf(bancada_rr, 0.80), 1)

        # Taxa 0.50 (50% válidos - ponto crítico da decisão RT-01) -> 1 * 0.50 = 0.50 -> 1
        self.assertEqual(calcular_teto_efetivo_uf(bancada_rr, 0.50), 1)

        # Taxa 0.49 (abaixo de 50% de válidos - protesto majoritário) -> 1 * 0.49 = 0.49 -> 0
        self.assertEqual(calcular_teto_efetivo_uf(bancada_rr, 0.49), 0)

        # Taxa 0.0 (0% válidos - protesto unânime) -> 1 * 0.0 = 0.0 -> 0
        self.assertEqual(calcular_teto_efetivo_uf(bancada_rr, 0.0), 0)

    def test_teto_efetivo_ufs_grandes(self) -> None:
        """Valida o cálculo do teto efetivo para bancadas amplas (MG e SP)."""
        # MG: 53 cadeiras -> tau = 10. Com taxa 0.80 -> 10 * 0.80 = 8.0 -> 8
        self.assertEqual(calcular_teto_efetivo_uf(53, 0.80), 8)

        # SP: 70 cadeiras -> tau = 14. Com taxa 0.70 -> 14 * 0.70 = 9.8 -> 10
        self.assertEqual(calcular_teto_efetivo_uf(70, 0.70), 10)

        # SP com 50% válidos -> 14 * 0.50 = 7.0 -> 7
        self.assertEqual(calcular_teto_efetivo_uf(70, 0.50), 7)

    def test_calcular_taxa_validos_voto4(self) -> None:
        """Distingue votos válidos de tema (incluindo confiança na Tela 2) de protesto (Tela 1)."""
        # Cenário típico: 80% válidos e 20% protesto deliberado na Tela 1
        taxa = calcular_taxa_validos_voto4(
            votos_tema_validos=800,
            votos_protesto_branco_nulo=200,
        )
        self.assertAlmostEqual(taxa, 0.80, places=6)

        # 100% votos válidos (sem protesto)
        self.assertAlmostEqual(
            calcular_taxa_validos_voto4(votos_tema_validos=1500, votos_protesto_branco_nulo=0),
            1.0,
            places=6,
        )

        # 100% protesto (nenhum voto em missão)
        self.assertAlmostEqual(
            calcular_taxa_validos_voto4(votos_tema_validos=0, votos_protesto_branco_nulo=500),
            0.0,
            places=6,
        )

        # Sem comparecimento (0 votos totais) -> deve retornar 0.0 com segurança
        self.assertEqual(
            calcular_taxa_validos_voto4(votos_tema_validos=0, votos_protesto_branco_nulo=0),
            0.0,
        )

    def test_calcular_taxa_validos_voto4_validacoes(self) -> None:
        """Impede contagens negativas de votos."""
        with self.assertRaises(ValueError):
            calcular_taxa_validos_voto4(-1, 100)
        with self.assertRaises(ValueError):
            calcular_taxa_validos_voto4(100, -1)

    def test_calcular_tetos_nacionais_todos_cem_por_cento(self) -> None:
        """Com 100% de válidos em todas as UFs, os tetos efetivos somam exatamente 91."""
        taxas_100 = {uf: 1.0 for uf in BANCADAS_ESTADUAIS}
        tetos = calcular_tetos_nacionais(BANCADAS_ESTADUAIS, taxas_100)

        self.assertEqual(len(tetos), 27)
        self.assertEqual(sum(tetos.values()), 91)
        self.assertEqual(tetos["SP"], 14)
        self.assertEqual(tetos["RR"], 1)

    def test_calcular_tetos_nacionais_protesto_total(self) -> None:
        """Com 0% de válidos (protesto total), todas as UFs zeram as cadeiras de missão."""
        taxas_0 = {uf: 0.0 for uf in BANCADAS_ESTADUAIS}
        tetos = calcular_tetos_nacionais(BANCADAS_ESTADUAIS, taxas_0)
        self.assertEqual(sum(tetos.values()), 0)
        self.assertTrue(all(u == 0 for u in tetos.values()))

    def test_calcular_tetos_nacionais_uf_faltante_lanca_key_error(self) -> None:
        """Se o dicionário de taxas não cobrir todas as UFs da bancada, deve levantar KeyError."""
        taxas_incompletas = {"SP": 1.0, "MG": 0.8}
        with self.assertRaises(KeyError):
            calcular_tetos_nacionais(BANCADAS_ESTADUAIS, taxas_incompletas)

    def test_validacoes_parametros_invalidos(self) -> None:
        """Testa validações defensivas contra parâmetros inválidos."""
        with self.assertRaises(ValueError):
            calcular_tau_uf(cadeiras_uf=-5)
        with self.assertRaises(ValueError):
            calcular_tau_uf(cadeiras_uf=10, rho=-0.1)
        with self.assertRaises(ValueError):
            calcular_tau_uf(cadeiras_uf=10, rho=1.5)
        with self.assertRaises(ValueError):
            calcular_teto_efetivo_uf(cadeiras_uf=8, taxa_validos_voto4=-0.1)
        with self.assertRaises(ValueError):
            calcular_teto_efetivo_uf(cadeiras_uf=8, taxa_validos_voto4=1.01)


if __name__ == "__main__":
    unittest.main()
