# ---------------------------------------------------------------------------
# [BLK-L-004-T] Testes da Matriz Biproporcional e Invariantes Marginais
# ---------------------------------------------------------------------------
"""Suíte de testes unitários para a alocação biproporcional de Balinski-Demange.

Valida a conservação estrita das bancadas estaduais (somas de linhas r_e) e dos
mandatos por coluna temática (somas de colunas h_c), a convergência do algoritmo
em escala nacional com 27 UFs x 12 colunas, o refinamento exato por caminhos de
aumento de utilidade marginal, a regra de contingência lexicográfica RT-09 e a
alocação com tetos de missão institucional (Etapa 3a).
"""

import math
import unittest

from simulador.src.biproporcional import (
    ResultadoBiproporcional,
    alocar_biproporcional,
    alocar_matriz_missao,
)
from simulador.src.constantes import (
    BANCADAS_ESTADUAIS,
    COLUNAS_ESTADO,
    COLUNAS_MISSAO_PADRAO,
    COLUNAS_PERMANENTES,
    TODAS_COLUNAS_PADRAO,
    TOTAL_CADEIRAS,
)
from simulador.src.teto_missao import calcular_tetos_nacionais


class TestBiproporcionalBasico(unittest.TestCase):
    """Testes fundamentais em matrizes reduzidas 3x3 e cenários de controle."""

    def test_matriz_3x3_simples(self) -> None:
        """Cenário básico 3x3 com convergência direta e fechamento marginal perfeito."""
        ufs = ["UF_A", "UF_B", "UF_C"]
        colunas = ["C01", "C02", "C03"]

        cadeiras_uf = {"UF_A": 5, "UF_B": 4, "UF_C": 3}
        cadeiras_coluna = {"C01": 4, "C02": 4, "C03": 4}

        votos = {
            "UF_A": {"C01": 1000, "C02": 500, "C03": 200},
            "UF_B": {"C01": 300, "C02": 800, "C03": 400},
            "UF_C": {"C01": 100, "C02": 200, "C03": 900},
        }

        res = alocar_biproporcional(votos, cadeiras_uf, cadeiras_coluna)

        self.assertIsInstance(res, ResultadoBiproporcional)
        self.assertFalse(res.contingencia_acionada)

        # Checagem das somas de linha
        for u in ufs:
            self.assertEqual(sum(res.matriz[u].values()), cadeiras_uf[u])

        # Checagem das somas de coluna
        for c in colunas:
            soma_c = sum(res.matriz[u][c] for u in ufs)
            self.assertEqual(soma_c, cadeiras_coluna[c])

        # Verificação da alocação esperada
        self.assertEqual(
            res.matriz,
            {
                "UF_A": {"C01": 3, "C02": 1, "C03": 1},
                "UF_B": {"C01": 1, "C02": 2, "C03": 1},
                "UF_C": {"C01": 0, "C02": 1, "C03": 2},
            },
        )

    def test_total_cadeiras_zero(self) -> None:
        """Quando o alvo de cadeiras for zero, retorna matriz inteiramente zerada."""
        cadeiras_uf = {"SP": 0, "RJ": 0}
        cadeiras_coluna = {"C01": 0, "C02": 0}
        votos = {
            "SP": {"C01": 100, "C02": 200},
            "RJ": {"C01": 300, "C02": 400},
        }

        res = alocar_biproporcional(votos, cadeiras_uf, cadeiras_coluna)
        self.assertEqual(res.matriz, {"SP": {"C01": 0, "C02": 0}, "RJ": {"C01": 0, "C02": 0}})
        self.assertFalse(res.contingencia_acionada)
        self.assertEqual(res.iteracoes, 0)


class TestBiproporcionalEscalaNacional(unittest.TestCase):
    """Testes de alta escala com todas as 27 UFs e dimensões reais de 9 e 12 colunas."""

    def test_escala_nacional_27_ufs_por_9_colunas(self) -> None:
        """Validação nacional com 27 UFs x 9 colunas (3 estatais fixas + 6 permanentes = 513)."""
        ufs = list(BANCADAS_ESTADUAIS.keys())
        colunas = list(COLUNAS_ESTADO + COLUNAS_PERMANENTES)
        self.assertEqual(len(ufs), 27)
        self.assertEqual(len(colunas), 9)

        cadeiras_uf = dict(BANCADAS_ESTADUAIS)
        self.assertEqual(sum(cadeiras_uf.values()), TOTAL_CADEIRAS)

        # 3 colunas de estado com 60 cada (180) + 6 colunas permanentes somando 333
        cadeiras_coluna = {
            "C01_ECONOMIA": 60,
            "C02_JUSTICA": 60,
            "C03_SOCIAL": 60,
            "C04_SAUDE": 65,
            "C05_EDUCACAO": 60,
            "C06_SEGURANCA": 58,
            "C07_INFRAESTRUTURA": 50,
            "C08_AGRO_AMBIENTE": 50,
            "C09_CIENCIA_TRABALHO": 50,
        }
        self.assertEqual(sum(cadeiras_coluna.values()), TOTAL_CADEIRAS)

        # Votos proporcionais ao tamanho da bancada com diversificação determinística
        votos: dict[str, dict[str, int]] = {}
        for u in ufs:
            bancada = cadeiras_uf[u]
            votos[u] = {}
            for c in colunas:
                fator = 1.0 + 0.08 * ((hash((u, c)) % 19) - 9)
                votos[u][c] = max(100, int(bancada * 50_000 * fator))

        res = alocar_biproporcional(votos, cadeiras_uf, cadeiras_coluna)

        # Checagem estrita de todas as 27 bancadas federativas
        for u, b_alvo in cadeiras_uf.items():
            self.assertEqual(
                sum(res.matriz[u].values()),
                b_alvo,
                f"A bancada de {u} divergiu do alvo constitucional.",
            )

        # Checagem estrita de todas as 9 colunas
        for c, c_alvo in cadeiras_coluna.items():
            soma_col = sum(res.matriz[u][c] for u in ufs)
            self.assertEqual(
                soma_col,
                c_alvo,
                f"A coluna {c} divergiu do total alocado.",
            )

        # Divisores devem ser positivos
        self.assertTrue(all(v > 0 for v in res.lambda_uf.values()))
        self.assertTrue(all(v > 0 for v in res.mu_coluna.values()))
        self.assertFalse(res.contingencia_acionada)

    def test_escala_nacional_27_ufs_por_12_colunas(self) -> None:
        """Validação nacional completa com 27 UFs x 12 colunas oficiais (513 deputados)."""
        ufs = list(BANCADAS_ESTADUAIS.keys())
        colunas = list(TODAS_COLUNAS_PADRAO)
        self.assertEqual(len(colunas), 12)

        cadeiras_uf = dict(BANCADAS_ESTADUAIS)

        # Configuração: 3x60 (180) + 6x40 (240) + 3x31 (93) = 513
        cadeiras_coluna = {
            "C01_ECONOMIA": 60,
            "C02_JUSTICA": 60,
            "C03_SOCIAL": 60,
            "C04_SAUDE": 40,
            "C05_EDUCACAO": 40,
            "C06_SEGURANCA": 40,
            "C07_INFRAESTRUTURA": 40,
            "C08_AGRO_AMBIENTE": 40,
            "C09_CIENCIA_TRABALHO": 40,
            "C10_MISSAO_1": 31,
            "C11_MISSAO_2": 31,
            "C12_MISSAO_3": 31,
        }
        self.assertEqual(sum(cadeiras_coluna.values()), TOTAL_CADEIRAS)

        votos: dict[str, dict[str, int]] = {}
        for u in ufs:
            bancada = cadeiras_uf[u]
            votos[u] = {}
            for c in colunas:
                fator = 1.0 + 0.1 * ((hash((u, c)) % 13) - 6)
                votos[u][c] = max(500, int(bancada * 80_000 * fator))

        res = alocar_biproporcional(votos, cadeiras_uf, cadeiras_coluna)

        # Validação 100% de linhas e colunas
        for u, b_alvo in cadeiras_uf.items():
            self.assertEqual(sum(res.matriz[u].values()), b_alvo)
        for c, c_alvo in cadeiras_coluna.items():
            soma_c = sum(res.matriz[u][c] for u in ufs)
            self.assertEqual(soma_c, c_alvo)


class TestContingenciaLexicograficaRT09(unittest.TestCase):
    """Testes da regra RT-09: votos zerados e ativação estrita de contingência."""

    def test_votos_zerados_nao_recebem_cadeiras_quando_dispensaveis(self) -> None:
        """Células com 0 votos não devem receber cadeira se as demais células suprirem a demanda."""
        ufs = ["UF1", "UF2"]
        colunas = ["C1", "C2"]
        cadeiras_uf = {"UF1": 2, "UF2": 2}
        cadeiras_coluna = {"C1": 2, "C2": 2}

        # UF1 tem 0 votos em C2, mas tem votos abundantes em C1
        # UF2 tem votos em C1 e C2
        votos = {
            "UF1": {"C1": 10_000, "C2": 0},
            "UF2": {"C1": 1_000, "C2": 10_000},
        }

        res = alocar_biproporcional(votos, cadeiras_uf, cadeiras_coluna)

        # UF1 não pode ter recebido cadeira em C2!
        self.assertEqual(res.matriz["UF1"]["C2"], 0)
        self.assertEqual(res.matriz["UF1"]["C1"], 2)
        self.assertEqual(res.matriz["UF2"]["C1"], 0)
        self.assertEqual(res.matriz["UF2"]["C2"], 2)
        self.assertFalse(res.contingencia_acionada)

    def test_contingencia_extrema_obrigatoria(self) -> None:
        """Quando for impossível fechar as margens sem células zero, a contingência é acionada."""
        # Coluna C3 necessita de 3 cadeiras.
        # Porém apenas UF1 teve votos nela.
        # A bancada total de UF1 é de apenas 1 cadeira!
        # Logo, é matematicamente mandatário que UF2 ou UF3 recebam cadeira em C3 mesmo com 0 votos!
        ufs = ["UF1", "UF2", "UF3"]
        colunas = ["C1", "C2", "C3"]

        cadeiras_uf = {"UF1": 1, "UF2": 2, "UF3": 2}
        cadeiras_coluna = {"C1": 1, "C2": 1, "C3": 3}

        votos = {
            "UF1": {"C1": 100, "C2": 100, "C3": 1_000},
            "UF2": {"C1": 500, "C2": 500, "C3": 0},
            "UF3": {"C1": 400, "C2": 400, "C3": 0},
        }

        res = alocar_biproporcional(votos, cadeiras_uf, cadeiras_coluna)

        # Margens devem fechar com exatidão matemática
        for u in ufs:
            self.assertEqual(sum(res.matriz[u].values()), cadeiras_uf[u])
        for c in colunas:
            soma_c = sum(res.matriz[u][c] for u in ufs)
            self.assertEqual(soma_c, cadeiras_coluna[c])

        # UF1 satura sua bancada única em C3 onde obteve votos
        self.assertEqual(res.matriz["UF1"]["C3"], 1)

        # A contingência RT-09 foi ativada
        self.assertTrue(res.contingencia_acionada)

        # Pelo menos uma célula com zero votos recebeu cadeira para viabilizar as margens
        zeros_com_cadeira = [
            (u, c) for u in ufs for c in colunas
            if votos[u][c] == 0 and res.matriz[u][c] > 0
        ]
        self.assertGreater(len(zeros_com_cadeira), 0)


class TestAlocarMatrizMissao(unittest.TestCase):
    """Testes da alocação de missão institucional (Bloco 3) sob a regra de tetos (Etapa 3a)."""

    def test_missao_capacidade_exata(self) -> None:
        """Quando a soma das cadeiras de missão for exatamente igual à soma dos tetos."""
        tetos = {"UF_A": 3, "UF_B": 2}
        cadeiras_missao = {"C10_M1": 3, "C11_M2": 2}

        votos = {
            "UF_A": {"C10_M1": 1000, "C11_M2": 400},
            "UF_B": {"C10_M1": 200, "C11_M2": 800},
        }

        res = alocar_matriz_missao(votos, tetos, cadeiras_missao)

        for u, teto in tetos.items():
            self.assertEqual(sum(res.matriz[u].values()), teto)
        for c, alvo in cadeiras_missao.items():
            soma_c = sum(res.matriz[u][c] for u in tetos)
            self.assertEqual(soma_c, alvo)

    def test_missao_com_folga_menor_que_tetos(self) -> None:
        """Quando as cadeiras de missão somam menos que os tetos (coluna fictícia de folga)."""
        bancadas = dict(BANCADAS_ESTADUAIS)
        taxas = {u: 1.0 for u in bancadas}
        tetos = calcular_tetos_nacionais(bancadas, taxas)
        total_tetos = sum(tetos.values())
        self.assertEqual(total_tetos, 91)

        # Demandamos 60 cadeiras para as missões (folga de 31 cadeiras em relação ao teto 91)
        cadeiras_missao = {
            "C10_MISSAO_1": 25,
            "C11_MISSAO_2": 20,
            "C12_MISSAO_3": 15,
        }
        total_missao = sum(cadeiras_missao.values())
        self.assertEqual(total_missao, 60)
        self.assertLess(total_missao, total_tetos)

        votos_missao: dict[str, dict[str, int]] = {}
        for u in bancadas:
            votos_missao[u] = {
                "C10_MISSAO_1": 1000 + (hash((u, "M1")) % 700),
                "C11_MISSAO_2": 800 + (hash((u, "M2")) % 500),
                "C12_MISSAO_3": 600 + (hash((u, "M3")) % 300),
            }

        res = alocar_matriz_missao(votos_missao, tetos, cadeiras_missao)

        # 1. Nenhuma UF pode ultrapassar seu teto efetivo u_e
        for u, teto in tetos.items():
            soma_uf_missao = sum(res.matriz[u].values())
            self.assertLessEqual(
                soma_uf_missao,
                teto,
                f"UF {u} excedeu o teto de missão: {soma_uf_missao} > {teto}",
            )

        # 2. Todas as colunas de missão devem fechar exatamente seu total prescrito
        for c, alvo in cadeiras_missao.items():
            soma_c = sum(res.matriz[u][c] for u in bancadas)
            self.assertEqual(
                soma_c,
                alvo,
                f"Coluna {c} divergiu do alvo: {soma_c} != {alvo}",
            )

        # 3. A coluna fictícia '__FOLGA__' não deve vazar para a matriz retornada
        for u in bancadas:
            self.assertNotIn("__FOLGA__", res.matriz[u])
        self.assertNotIn("__FOLGA__", res.mu_coluna)

    def test_missao_capacidade_insuficiente_falha(self) -> None:
        """Se a soma das missões exceder a capacidade dos tetos, deve levantar ValueError."""
        tetos = {"UF_A": 2, "UF_B": 1}  # Total 3
        cadeiras_missao = {"M1": 2, "M2": 3}  # Total 5 > 3
        votos = {
            "UF_A": {"M1": 100, "M2": 100},
            "UF_B": {"M1": 50, "M2": 50},
        }

        with self.assertRaises(ValueError):
            alocar_matriz_missao(votos, tetos, cadeiras_missao)


class TestValidacoesEErros(unittest.TestCase):
    """Testes defensivos para integridade dos parâmetros e tratamento de exceções."""

    def test_soma_marginais_divergentes(self) -> None:
        """Soma das cadeiras das UFs diferente da soma das colunas deve levantar ValueError."""
        with self.assertRaises(ValueError):
            alocar_biproporcional(
                votos={"SP": {"C1": 10}},
                cadeiras_uf={"SP": 5},
                cadeiras_coluna={"C1": 6},
            )

    def test_cadeira_uf_negativa(self) -> None:
        """Alvo negativo de cadeiras de UF deve levantar ValueError."""
        with self.assertRaises(ValueError):
            alocar_biproporcional(
                votos={"SP": {"C1": 10}},
                cadeiras_uf={"SP": -1},
                cadeiras_coluna={"C1": -1},
            )

    def test_cadeira_coluna_negativa(self) -> None:
        """Alvo negativo de cadeiras de coluna deve levantar ValueError."""
        with self.assertRaises(ValueError):
            alocar_biproporcional(
                votos={"SP": {"C1": 10}},
                cadeiras_uf={"SP": 0},
                cadeiras_coluna={"C1": -1},
            )

    def test_voto_negativo(self) -> None:
        """Contagem de votos negativa deve levantar ValueError."""
        with self.assertRaises(ValueError):
            alocar_biproporcional(
                votos={"SP": {"C1": -10}},
                cadeiras_uf={"SP": 1},
                cadeiras_coluna={"C1": 1},
            )

    def test_uf_ausente_em_votos(self) -> None:
        """UF listada nas bancadas mas ausente nos votos deve levantar KeyError."""
        with self.assertRaises(KeyError):
            alocar_biproporcional(
                votos={"SP": {"C1": 10}},
                cadeiras_uf={"RJ": 1},
                cadeiras_coluna={"C1": 1},
            )

    def test_mapeamento_vazio(self) -> None:
        """Mapeamento vazio de cadeiras de UF ou colunas deve levantar ValueError."""
        with self.assertRaises(ValueError):
            alocar_biproporcional(
                votos={},
                cadeiras_uf={},
                cadeiras_coluna={"C1": 1},
            )
        with self.assertRaises(ValueError):
            alocar_biproporcional(
                votos={},
                cadeiras_uf={"SP": 1},
                cadeiras_coluna={},
            )
