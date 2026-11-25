# ---------------------------------------------------------------------------
# [BLK-L-003-T] Testes de Alocação de Sainte-Laguë
# ---------------------------------------------------------------------------
"""Suíte de testes unitários para a alocação de Sainte-Laguë com pisos e tetos.

Valida a alocação proporcional de cadeiras, a eficácia do piso protetor (D-09),
a contenção por tetos máximos, a monotonicidade de casa (ausência do Paradoxo
do Alabama), o desempate determinístico em 3 níveis, o tratamento robusto de erros
e a consistência matemática do divisor de equilíbrio D.
"""

import math
import unittest

from simulador.src.sainte_lague import (
    alocar_sainte_lague,
    calcular_divisor_equilibrio,
)


class TestSainteLagueBasico(unittest.TestCase):
    """Testes fundamentais de proporcionalidade de Sainte-Laguë sem restrições."""

    def test_cenario_padrao_tres_partidos(self) -> None:
        """Cenário clássico da literatura eleitoral com 10 cadeiras."""
        votos = {"A": 452, "B": 351, "C": 197}
        total_cadeiras = 10

        alocacao = alocar_sainte_lague(votos, total_cadeiras)

        self.assertEqual(alocacao, {"A": 5, "B": 3, "C": 2})
        self.assertEqual(sum(alocacao.values()), total_cadeiras)

    def test_total_cadeiras_zero(self) -> None:
        """Com zero cadeiras a distribuir, todos recebem zero."""
        votos = {"A": 100, "B": 200}
        alocacao = alocar_sainte_lague(votos, 0)
        self.assertEqual(alocacao, {"A": 0, "B": 0})
        self.assertEqual(sum(alocacao.values()), 0)

    def test_um_unico_partido(self) -> None:
        """Quando apenas um partido concorre com votos, recebe todas as vagas."""
        votos = {"A": 1000}
        alocacao = alocar_sainte_lague(votos, 15)
        self.assertEqual(alocacao, {"A": 15})


class TestPisoProtetorD09(unittest.TestCase):
    """Validação da regra D-09: piso protetor de 20 cadeiras para colunas temáticas."""

    def test_protecao_coluna_minoritaria(self) -> None:
        """Uma coluna com apenas 2% dos votos é protegida no piso 20 e o restante reajusta."""
        colunas = {
            "C04_SAUDE": 30_000,
            "C05_EDUCACAO": 25_000,
            "C06_SEGURANCA": 20_000,
            "C07_INFRA": 13_000,
            "C08_AGRO": 10_000,
            "C09_CIENCIA": 2_000,  # 2% dos 100.000 votos válidos
        }
        total_cadeiras = 260
        pisos = {c: 20 for c in colunas}

        # 1. Sem piso: Ciência receberia ~5 cadeiras (2% de 260 = 5.2)
        alocacao_sem_piso = alocar_sainte_lague(colunas, total_cadeiras)
        self.assertEqual(alocacao_sem_piso["C09_CIENCIA"], 5)
        self.assertEqual(sum(alocacao_sem_piso.values()), 260)

        # 2. Com piso protetor de 20: Ciência é garantida com 20 cadeiras
        alocacao_com_piso = alocar_sainte_lague(colunas, total_cadeiras, pisos=pisos)

        self.assertEqual(alocacao_com_piso["C09_CIENCIA"], 20)
        self.assertEqual(sum(alocacao_com_piso.values()), 260)

        # Todas as colunas devem ter no mínimo o piso
        for col, h in alocacao_com_piso.items():
            self.assertGreaterEqual(h, 20, f"Coluna {col} violou o piso de 20.")

        # As outras 5 colunas absorvem as 240 cadeiras restantes proporcionalmente.
        # Note que C04 e C08 empatam no quociente de 204.08 (30000/147 == 10000/49);
        # pelo desempate por voto bruto, C04 (30.000) vence e fica com 74, C08 com 24.
        self.assertEqual(
            alocacao_com_piso,
            {
                "C04_SAUDE": 74,
                "C05_EDUCACAO": 61,
                "C06_SEGURANCA": 49,
                "C07_INFRA": 32,
                "C08_AGRO": 24,
                "C09_CIENCIA": 20,
            },
        )

    def test_total_cadeiras_igual_a_soma_dos_pisos(self) -> None:
        """Quando o total de cadeiras é exatamente a soma dos pisos, todos recebem o piso."""
        votos = {"A": 10_000, "B": 5_000, "C": 1_000}
        pisos = {"A": 10, "B": 5, "C": 2}
        total = 17

        alocacao = alocar_sainte_lague(votos, total, pisos=pisos)
        self.assertEqual(alocacao, {"A": 10, "B": 5, "C": 2})
        self.assertEqual(sum(alocacao.values()), 17)


class TestContencaoPorTetos(unittest.TestCase):
    """Validações de limites superiores (tetos u_c) na distribuição."""

    def test_teto_restringe_partido_majoritario(self) -> None:
        """Partido com maioria esmagadora é limitado por seu teto e repassa excedente."""
        votos = {"A": 1000, "B": 100, "C": 100}
        total = 10

        # Sem teto: A ganharia 8 cadeiras
        alocacao_livre = alocar_sainte_lague(votos, total)
        self.assertEqual(alocacao_livre["A"], 8)

        # Com teto de 4 cadeiras para A
        tetos = {"A": 4}
        alocacao_teto = alocar_sainte_lague(votos, total, tetos=tetos)

        self.assertEqual(alocacao_teto["A"], 4)
        self.assertEqual(alocacao_teto["B"], 3)
        self.assertEqual(alocacao_teto["C"], 3)
        self.assertEqual(sum(alocacao_teto.values()), 10)

    def test_pisos_e_tetos_simultaneos(self) -> None:
        """Combinação de pisos inferiores e tetos superiores operando em harmonia."""
        votos = {"A": 500, "B": 300, "C": 200}
        total = 12
        pisos = {"A": 3, "B": 2, "C": 2}
        tetos = {"A": 6, "B": 4, "C": 3}

        alocacao = alocar_sainte_lague(votos, total, pisos=pisos, tetos=tetos)

        self.assertEqual(sum(alocacao.values()), 12)
        for c in votos:
            self.assertGreaterEqual(alocacao[c], pisos[c])
            self.assertLessEqual(alocacao[c], tetos[c])


class TestMonotonicidadeDeCasa(unittest.TestCase):
    """Comprova a ausência do Paradoxo do Alabama (monotonicidade de casa)."""

    def test_aumento_de_cadeiras_nunca_reduz_vagas(self) -> None:
        """Aumentar o parlamento de H para H+1 nunca pode reduzir as cadeiras de ninguém."""
        votos = {"A": 725, "B": 480, "C": 310, "D": 190, "E": 95}
        pisos = {"A": 2, "B": 1, "C": 1, "D": 0, "E": 0}

        soma_pisos = sum(pisos.values())
        alocacao_anterior = alocar_sainte_lague(votos, soma_pisos, pisos=pisos)

        for h in range(soma_pisos + 1, soma_pisos + 40):
            alocacao_atual = alocar_sainte_lague(votos, h, pisos=pisos)

            self.assertEqual(sum(alocacao_atual.values()), h)
            for c in votos:
                self.assertGreaterEqual(
                    alocacao_atual[c],
                    alocacao_anterior[c],
                    f"Paradoxo do Alabama detectado na entidade '{c}' ao subir para {h} cadeiras!",
                )

            alocacao_anterior = alocacao_atual


class TestDesempateDeterministico(unittest.TestCase):
    """Valida o critério estrito de desempate em 3 níveis."""

    def test_desempate_por_voto_bruto(self) -> None:
        """Empate em quociente deve ser decidido a favor do maior número de votos brutos."""
        # A tem 300 votos e alocação 1 -> próximo quociente: 300 / 3 = 100
        # B tem 100 votos e alocação 0 -> próximo quociente: 100 / 1 = 100
        votos = {"A": 300, "B": 100}
        total = 2

        alocacao = alocar_sainte_lague(votos, total)

        # Cadeira 1 foi para A (300/1 > 100/1).
        # Cadeira 2: quociente 100 vs 100. Voto bruto de A (300) > B (100) -> A vence!
        self.assertEqual(alocacao, {"A": 2, "B": 0})

    def test_desempate_por_ordem_alfabetica(self) -> None:
        """Empate em quociente e votos brutos deve ser decidido por ordem alfabética."""
        votos = {"Z": 100, "A": 100}
        total = 1

        alocacao = alocar_sainte_lague(votos, total)

        # Ambos têm quociente 100 e votos 100. 'A' < 'Z' alfabeticamente.
        self.assertEqual(alocacao, {"A": 1, "Z": 0})


class TestDivisorEquilibrio(unittest.TestCase):
    """Valida a precisão matemática e transparência do divisor D de Sainte-Laguë."""

    def _verificar_consistencia_divisor(
        self,
        votos: dict[str, int],
        total_cadeiras: int,
        pisos: dict[str, int] | None = None,
        tetos: dict[str, int] | None = None,
    ) -> None:
        alocacao = alocar_sainte_lague(votos, total_cadeiras, pisos=pisos, tetos=tetos)
        divisor = calcular_divisor_equilibrio(votos, alocacao, pisos=pisos, tetos=tetos)

        self.assertGreater(divisor, 0.0)

        for c, v in votos.items():
            f_c = pisos.get(c, 0) if pisos else 0
            u_c = tetos.get(c, total_cadeiras) if tetos else total_cadeiras

            arredondado = math.floor(v / divisor + 0.5)
            clamped = max(f_c, min(u_c, arredondado))

            self.assertEqual(
                clamped,
                alocacao[c],
                f"Divisor {divisor} inconsistente para '{c}': esperado {alocacao[c]}, obtido {clamped}.",
            )

    def test_consistencia_cenario_padrao(self) -> None:
        """Verifica reprodução exata da alocação pelo divisor D no cenário padrão."""
        votos = {"A": 452, "B": 351, "C": 197}
        self._verificar_consistencia_divisor(votos, 10)

    def test_consistencia_com_piso_protetor(self) -> None:
        """Verifica reprodução exata no cenário D-09 com pisos protetores (sem empate exato)."""
        colunas = {
            "C04": 30_500,
            "C05": 25_000,
            "C06": 20_000,
            "C07": 13_000,
            "C08": 10_000,
            "C09": 2_000,
        }
        pisos = {c: 20 for c in colunas}
        self._verificar_consistencia_divisor(colunas, 260, pisos=pisos)

    def test_consistencia_com_tetos(self) -> None:
        """Verifica reprodução exata em cenário com tetos ativos."""
        votos = {"A": 1000, "B": 100, "C": 100}
        tetos = {"A": 4}
        self._verificar_consistencia_divisor(votos, 10, tetos=tetos)

    def test_consistencia_limite_todos_no_piso(self) -> None:
        """Verifica cálculo do divisor quando total_cadeiras == soma_pisos."""
        votos = {"A": 500, "B": 300}
        pisos = {"A": 5, "B": 3}
        self._verificar_consistencia_divisor(votos, 8, pisos=pisos)

    def test_empate_exato_limiar_coincidente(self) -> None:
        """Demonstra o comportamento no ponto de empate exato (D_min == D_max)."""
        # Em 30.000 vs 10.000 com 2 cadeiras:
        # Cadeira 1 vai para C04 (30.000/1 > 10.000/1).
        # Cadeira 2: C04 tem 30.000/3 = 10.000; C08 tem 10.000/1 = 10.000.
        # Quocientes rigorosamente idênticos; por voto bruto C04 vence -> alocação {C04: 2, C08: 0}.
        # Limiar superior D_max = 30.000 / 1.5 = 20.000; Limiar inferior D_min = 10.000 / 0.5 = 20.000.
        colunas = {"C04": 30_000, "C08": 10_000}
        total = 2
        alocacao = alocar_sainte_lague(colunas, total)
        self.assertEqual(alocacao, {"C04": 2, "C08": 0})

        divisor = calcular_divisor_equilibrio(colunas, alocacao)
        self.assertEqual(divisor, 20_000.0)


class TestValidacoesEErros(unittest.TestCase):
    """Testes defensivos para integridade dos parâmetros de entrada."""

    def test_total_cadeiras_negativo(self) -> None:
        with self.assertRaises(ValueError):
            alocar_sainte_lague({"A": 100}, -1)

    def test_voto_negativo(self) -> None:
        with self.assertRaises(ValueError):
            alocar_sainte_lague({"A": -10}, 5)

    def test_piso_negativo(self) -> None:
        with self.assertRaises(ValueError):
            alocar_sainte_lague({"A": 100}, 5, pisos={"A": -1})

    def test_teto_negativo(self) -> None:
        with self.assertRaises(ValueError):
            alocar_sainte_lague({"A": 100}, 5, tetos={"A": -1})

    def test_teto_menor_que_piso(self) -> None:
        with self.assertRaises(ValueError):
            alocar_sainte_lague({"A": 100}, 10, pisos={"A": 5}, tetos={"A": 4})

    def test_chave_estranha_em_pisos(self) -> None:
        with self.assertRaises(ValueError):
            alocar_sainte_lague({"A": 100}, 5, pisos={"FANTASMA": 2})

    def test_chave_estranha_em_tetos(self) -> None:
        with self.assertRaises(ValueError):
            alocar_sainte_lague({"A": 100}, 5, tetos={"FANTASMA": 2})

    def test_soma_pisos_maior_que_total_cadeiras(self) -> None:
        with self.assertRaises(ValueError):
            alocar_sainte_lague({"A": 100, "B": 100}, 5, pisos={"A": 3, "B": 3})

    def test_soma_tetos_menor_que_total_cadeiras(self) -> None:
        with self.assertRaises(ValueError):
            alocar_sainte_lague({"A": 100, "B": 100}, 10, tetos={"A": 4, "B": 4})

    def test_votos_zerados_com_cadeiras_restantes(self) -> None:
        """Sem votos em categorias elegíveis, não é possível alocar as cadeiras restantes."""
        votos = {"A": 0, "B": 0}
        with self.assertRaises(ValueError):
            alocar_sainte_lague(votos, 5)

    def test_votos_zerados_exatamente_no_piso_tem_sucesso(self) -> None:
        """Se o total de cadeiras for igual à soma dos pisos, votos zerados não impedem alocação."""
        votos = {"A": 0, "B": 0}
        pisos = {"A": 2, "B": 3}
        alocacao = alocar_sainte_lague(votos, 5, pisos=pisos)
        self.assertEqual(alocacao, {"A": 2, "B": 3})


if __name__ == "__main__":
    unittest.main()
