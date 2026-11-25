# ---------------------------------------------------------------------------
# [BLK-L-001] Constantes Constitucionais, Bancadas Federativas e Colunas Temáticas
# ---------------------------------------------------------------------------
"""Constantes constitucionais e eleitorais do modelo RTP.

Define a distribuição de cadeiras por Unidade Federativa (CF/88, Art. 45),
as macrorregiões oficiais do IBGE, as dimensões dos blocos de colunas
e os parâmetros de pisos e tetos de missão institucional.
"""

from typing import Final

# Total constitucional de deputados federais
TOTAL_CADEIRAS: Final[int] = 513

# Distribuição de cadeiras entre blocos
CADEIRAS_BLOCO_1: Final[int] = 180  # 3 colunas generalistas x 60 cadeiras fixas
CADEIRAS_LIVRES: Final[int] = 333   # 513 - 180 para colunas permanentes e de missão

# Pisos de garantia de representação
PISO_GENERALISTA: Final[int] = 60   # Cadeiras fixas por coluna de Estado (C01 a C03)
PISO_PERMANENTE: Final[int] = 20    # Piso mínimo nacional por coluna permanente (C04 a C09)

# Parâmetro rho para teto de missão (Bloco 3) por UF (20% das cadeiras da bancada)
RHO_TETO_MISSAO: Final[float] = 0.20

# Bancadas estaduais oficiais da Câmara dos Deputados (Art. 45, § 1º, CF/88)
# Soma rigorosa: 513 cadeiras
BANCADAS_ESTADUAIS: Final[dict[str, int]] = {
    "SP": 70,
    "MG": 53,
    "RJ": 46,
    "BA": 39,
    "RS": 31,
    "PR": 30,
    "PE": 25,
    "CE": 22,
    "MA": 18,
    "GO": 17,
    "PA": 17,
    "SC": 16,
    "PB": 12,
    "ES": 10,
    "PI": 10,
    "AL": 9,
    "AC": 8,
    "AM": 8,
    "AP": 8,
    "DF": 8,
    "MS": 8,
    "MT": 8,
    "RN": 8,
    "RO": 8,
    "RR": 8,
    "SE": 8,
    "TO": 8,
}

# Mapeamento oficial das 27 UFs para as macrorregiões do IBGE
MACRORREGIOES: Final[dict[str, str]] = {
    # Norte (7 UFs)
    "AC": "N",
    "AM": "N",
    "AP": "N",
    "PA": "N",
    "RO": "N",
    "RR": "N",
    "TO": "N",
    # Nordeste (9 UFs)
    "AL": "NE",
    "BA": "NE",
    "CE": "NE",
    "MA": "NE",
    "PB": "NE",
    "PE": "NE",
    "PI": "NE",
    "RN": "NE",
    "SE": "NE",
    # Centro-Oeste (4 UFs)
    "DF": "CO",
    "GO": "CO",
    "MS": "CO",
    "MT": "CO",
    # Sudeste (4 UFs)
    "ES": "SE",
    "MG": "SE",
    "RJ": "SE",
    "SP": "SE",
    # Sul (3 UFs)
    "PR": "S",
    "RS": "S",
    "SC": "S",
}

# Nomes identificadores padronizados das 12 colunas temáticas
COLUNAS_ESTADO: Final[tuple[str, ...]] = (
    "C01_ECONOMIA",
    "C02_JUSTICA",
    "C03_SOCIAL",
)

COLUNAS_PERMANENTES: Final[tuple[str, ...]] = (
    "C04_SAUDE",
    "C05_EDUCACAO",
    "C06_SEGURANCA",
    "C07_INFRAESTRUTURA",
    "C08_AGRO_AMBIENTE",
    "C09_CIENCIA_TRABALHO",
)

COLUNAS_MISSAO_PADRAO: Final[tuple[str, ...]] = (
    "C10_MISSAO_1",
    "C11_MISSAO_2",
    "C12_MISSAO_3",
)

# Conjunto completo padronizado das 12 colunas da Câmara dos Deputados
TODAS_COLUNAS_PADRAO: Final[tuple[str, ...]] = (
    COLUNAS_ESTADO + COLUNAS_PERMANENTES + COLUNAS_MISSAO_PADRAO
)
