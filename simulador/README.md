# Simulador Oficial — Representação Temática Proporcional (RTP)

Implementação de referência, determinística e auditável do algoritmo de apuração da **Representação Temática Proporcional (SPEC-002)**.

Construído utilizando **100% da Biblioteca Padrão do Python 3.12** (zero dependências externas) para permitir fácil inspeção e reprodução por pesquisadores, parlamentares, jornalistas de dados e auditores.

---

## Como Executar (1 Comando)

### 1. Rodar a Simulação Nacional e o Relatório de Estresse do Red Team
```powershell
python simulador/rodar_cenario.py
```

### 2. Rodar a Suíte Completa de Testes Automatizados (112 testes)
```powershell
python -m unittest discover -s simulador/tests -v
```

---

## Arquitetura dos Módulos (Particionamento BLK-L)

| Bloco | Arquivo | Responsabilidade |
|---|---|---|
| `BLK-L-001` | [`src/constantes.py`](src/constantes.py) | Bancadas das 27 UFs (Art. 45 da CF/88 somando 513), 5 macrorregiões do IBGE, 12 colunas e pisos/tetos. |
| `BLK-L-002` | [`src/teto_missao.py`](src/teto_missao.py) | Cálculo de $\tau_e$ e do teto efetivo $u_e = [\![\tau_e \cdot a_e]\!]$ com Sainte-Laguë (RT-01) e regra de 2 telas do Voto 4 (Protesto vs. Confiança/Legenda, RT-04). |
| `BLK-L-003` | [`src/sainte_lague.py`](src/sainte_lague.py) | Método de divisores de Sainte-Laguë (Webster) unidimensional com pisos protetores (D-09), tetos e divisor de equilíbrio $D$. |
| `BLK-L-004` | [`src/biproporcional.py`](src/biproporcional.py) | Alocação matricial 2D de Balinski-Demange (Escalonamento TIES + caminho de aumento de maior utilidade marginal Bellman-Ford + contingência lexicográfica RT-09 + coluna de folga de Gaffke-Pukelsheim). |
| `BLK-L-005` | [`src/metricas.py`](src/metricas.py) | Índices de Gallagher (LSq), Laakso-Taagepera ($N_{\text{eff}}$), Herfindahl (HHI), curva de sobrevivência partidária (RT-20) e auditor das 6 invariantes constitucionais. |
| `BLK-L-006` | [`src/pipeline.py`](src/pipeline.py) | Orquestrador nacional das Etapas 0 a 4 (votos do exterior RT-29, 3 a 6 colunas de missão RT-02, STV enxuto intracelular com voto de confiança neutro da Tela 2 e suplência regional RT-11). |
| `BLK-L-007` | [`src/estresse_redteam.py`](src/estresse_redteam.py) | Os 5 experimentos de estresse aprovados no Red Team (RT-19 a RT-23). |
| `BLK-L-008` | [`rodar_cenario.py`](rodar_cenario.py) | Interface de linha de comando que executa a apuração demonstrativa e imprime as tabelas completas. |

