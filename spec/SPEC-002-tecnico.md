# SPEC-002-T — Modelo Matemático, Algoritmo de Apuração e Evidências do Simulador

| Campo | Valor |
|---|---|
| Versão | 0.2 (consolidada e validada pelo simulador oficial) |
| Documento par | [SPEC-002-desenho.md](SPEC-002-desenho.md) |
| Registro de decisões | [decisoes.md](../decisoes.md) — IDs `D-01` a `D-23` |
| Red Team | [RT-01-consolidado.md](../redteam/RT-01-consolidado.md) — itens `RT-01` a `RT-30` |
| Implementação de referência | [simulador/README.md](../simulador/README.md) — Python 3.12 (Standard Library, `BLK-L-001` a `BLK-L-008`) |

> **Regra de rastreabilidade:** todas as definições fechadas abaixo estão sincronizadas com `decisoes.md`, `RT-01-consolidado.md` e os módulos auditáveis em `simulador/src/`. Os resultados empíricos da Seção 8 foram gerados diretamente por `simulador/rodar_cenario.py` e validados por 112 testes automatizados em `simulador/tests/`.

---

## 1. Notação

| Símbolo | Significado |
|---|---|
| $E$ | Conjunto de unidades federativas, $\lvert E\rvert = 27$ |
| $s_e$ | Bancada constitucional da UF $e$ (Art. 45, §1º, CF/88); $S = \sum_{e \in E} s_e = 513$ |
| $C_1$ | As 3 Colunas de Estado / Generalistas (`C01_ECONOMIA`, `C02_JUSTICA`, `C03_SOCIAL`) |
| $C_2$ | As 6 Colunas Permanentes (`C04_SAUDE` a `C09_CIENCIA_TRABALHO`) |
| $C_3$ | Colunas de Missão Presidencial ativas na eleição, com $\lvert C_3\rvert \in \{3, \dots, 6\}$ (`D-17` / `RT-02`) |
| $C = C_1 \cup C_2 \cup C_3$ | Conjunto total de colunas temáticas ativas (12 no cenário-base; até 15 com 6 missões distintas) |
| $v_{e,c}$ | Votos válidos nominais/temáticos na coluna $c$ dentro da UF $e$ (para as Etapas 2 e 3) |
| $V_{e,c}$ | Total de votos válidos considerados na célula $(e,c)$ para a Etapa 4: soma dos votos nominais de 1ª preferência, votos de legenda partidária (2 dígitos) e votos em branco/nulo neutros de confiança da Tela 2 |
| $v_{ext,c}$ | Votos de legenda temática pura na Zona ZZ (exterior) e em trânsito interestadual para a coluna $c$ (`D-22` / `RT-29`) |
| $V_c = \sum_{e \in E} v_{e,c} + v_{ext,c}$ | Total nacional de votos válidos da coluna $c$ |
| $w_e$ | Total de Votos 4 válidos na UF $e$ (inclui escolha nominal na Tela 2, votos em legenda partidária de 2 dígitos dentro do tema e votos em branco/nulo neutros de confiança na **Tela 2**, conforme `D-15` / `RT-04`) |
| $w_e^{prot}$ | Votos em branco ou nulos deliberados de protesto na **Tela 1** do Voto 4 dentro da UF $e$ |
| $N_e$ | Total de eleitores que compareceram na UF $e$ (usado apenas na variante configurável alternativa do denominador de $a_e$) |
| $a_e$ | Taxa de validade na Tela 1 do Voto 4 na UF $e$; no padrão implementado, $a_e = w_e / (w_e + w_e^{prot})$ |
| $[\![x]\!] = \lfloor x + 0{,}5 \rfloor$ | Arredondamento determinístico de Sainte-Laguë (*half-up*: frações $\ge 0{,}5$ sobem; evita o *round-half-to-even* do IEEE 754) |
| $\tilde{v}_{e,c}$ | Voto suavizado na célula $(e,c)$ para contingência lexicográfica (`RT-09`): $v_{e,c}$ se $v_{e,c} > 0$, ou $\epsilon = 10^{-9}$ se $v_{e,c} = 0$ |
| $h_c$ | Cadeiras nacionais totais da coluna $c$ |
| $x_{e,c}, \; y_{e,c}$ | Cadeiras alocadas à coluna $c$ na UF $e$ nas matrizes principal ($C_1 \cup C_2$) e de missão ($C_3$), respectivamente |
| $m_e = \sum_{c \in C_3} y_{e,c}$ | Total efetivo de cadeiras de missão conquistadas pela UF $e$ |

---

## 2. Parâmetros do modelo

| Parâmetro | Valor / Regra | Status | Ref. |
|---|---|---|---|
| $S$ (cadeiras totais) | $513$ (bancadas Art. 45, Anexo A) | Fechado (parametrizável) | Q-14 |
| $h_c$ para $c \in C_1$ | $60$ fixo por coluna ($180$ no Bloco 1) | Fechado | D-08 |
| Cadeiras disputáveis $S - 180$ | $333$ (divididas entre Bloco 2 e Bloco 3) | Fechado | D-08, D-09 |
| Piso $f_c$ para $c \in C_2$ | $20$ por coluna permanente (6 colunas) | Fechado | D-07, D-08, D-09 |
| Piso para $c \in C_3$ | $0$ (sem garantia mínima) | Fechado | D-08 |
| Teto relativo da missão $\rho$ | $0{,}20$ ($20\%$ da bancada de cada UF) | Fechado | D-13 |
| Arredondamento do teto nominal $\tau_e$ | Para baixo: $\lfloor \rho \, s_e \rfloor$ ($\sum_e \tau_e = 91$) | Fechado | D-13 |
| Arredondamento do teto efetivo $u_e$ | **Sainte-Laguë *half-up***: $[\![\tau_e \, a_e]\!] = \lfloor \tau_e \, a_e + 0{,}5 \rfloor$ | **Fechado (corrigido)** | RT-01, D-13 |
| Método de divisores (1D e 2D) | Sainte-Laguë / Webster (divisores $1, 3, 5, \dots$ / pontos médios $k - 0{,}5$) | Fechado | D-10, D-11 |
| Fluxo do Voto 4 (2 telas) | Tela 1: branco/nulo encolhe $u_e$; Tela 2: 2 dígitos = legenda partidária e branco/nulo = confiança neutra rateada proporcionalmente na coluna | **Fechado** | RT-04, D-15 |
| Temas de missão ativos no 2º turno | Ambos os finalistas ativos ($\lvert C_3\rvert \in \{3, \dots, 6\}$) | **Fechado** | RT-02, D-17 |
| Votos do exterior (ZZ) e trânsito | Somam em $V_c$ (legenda temática pura), sem alterar $s_e$ | **Fechado** | RT-29, D-22 |
| Contingência lexicográfica | $\epsilon = 10^{-9}$ para células com voto zero | Fechado em princípio | RT-09 |
| Denominador alternativo de $a_e$ | Comparecimento total $N_e$ vs. total votado na Tela 1 ($w_e + w_e^{prot}$) | **Configurável** | D-15 |
| Cumulação de Votos 2 e 3 (`Q-05`) | Permitida vs. proibida na mesma coluna (testada em `RT-19`) | **Configurável** | Q-05, RT-19 |
| Regras de transferência STV (`Q-08`) | **STV enxuto** (1 número obrigatório + até uma 2ª opção opcional; calibração no `RT-21` antes do PLP) + cota de Droop | **Condicionado / Configurável** | D-12, RT-03, RT-21 |

---

## 3. Algoritmo oficial de apuração (`simulador/src/`)

### Etapa 0 — Apuração preliminar e totalização nacional (`teto_missao.py`, `pipeline.py`)
A apuração preliminar das urnas agrega os sufrágios por candidato, coluna e UF para fornecer $v_{e,c}$, e computa previamente $a_e$ em cada UF via `teto_missao.calcular_taxa_validos_voto4(w_e, w_e^{prot})` a partir das duas telas do Voto 4. De posse dessas entradas pré-computadas, `pipeline.executar_apuracao_nacional` soma diretamente os votos de legenda temática pura recebidos na Zona ZZ (exterior) e em trânsito interestadual ($v_{ext,c}$) ao total nacional de cada coluna:

$$V_c = \sum_{e \in E} v_{e,c} + v_{ext,c}$$

Esse procedimento permite que o eleitorado no exterior e em trânsito influencie a dimensão temática nacional $h_c$ sem distorcer os vetores estaduais $v_{e,c}$ nem as bancadas rígidas $s_e$ (`D-22` / `RT-29`).

### Etapa 1 — Teto nominal e efetivo de missão por UF (`teto_missao.py`)
Para cada unidade federativa $e \in E$:

$$\tau_e = \lfloor \rho \, s_e \rfloor, \qquad a_e = \frac{w_e}{w_e + w_e^{prot}} \; (\text{ou } 0 \text{ se } w_e + w_e^{prot} = 0), \qquad u_e = [\![\tau_e \, a_e]\!] = \lfloor \tau_e \, a_e + 0{,}5 \rfloor$$

O teto nacional efetivo do Bloco 3 é $U = \sum_{e \in E} u_e \le 91$.

> **Correção `RT-01`:** na formulação preliminar (v0.1), o uso de piso duplo $\lfloor \tau_e a_e \rfloor$ zerava o teto de todas as 12 UFs com $\tau_e = 1$ (11 UFs de 8 deputados e AL com 9) diante de um único voto em branco. Com o arredondamento de Sainte-Laguë $[\![\tau_e a_e]\!]$, qualquer UF com $\tau_e = 1$ preserva sua cadeira de missão sempre que $a_e \ge 0{,}50$, mantendo a regra intuitiva de "metade válida = mantém a cadeira" e respeitando exatamente o máximo nacional de 91 assentos.

### Etapa 2 — Dimensionamento nacional de blocos e colunas (`sainte_lague.py`, `pipeline.py`)

**2a. Tamanho global do Bloco 3 e do Bloco 2:**
Sendo $V_{C_3} = \sum_{c \in C_3} V_c$ e $V_{C_2} = \sum_{c \in C_2} V_c$:

$$H_3^{prop} = 333 \cdot \frac{V_{C_3}}{V_{C_2} + V_{C_3}}, \qquad H_3 = \min\left(U, \; [\![H_3^{prop}]\!]\right), \qquad H_2 = 333 - H_3$$

> **Prova analítica (`RT-12`):** seja $a$ a taxa nacional média de votos válidos no Voto 4 e $b$ a taxa média de válidos nos Votos 2 e 3. Desprezando arredondamentos locais e $v_{ext,c}$, tem-se $U \approx 91a$ e $H_3^{prop} \approx 333a / (2b + a)$. Logo:
> $$91a < \frac{333a}{2b + a} \iff 2b + a < \frac{333}{91} \approx 3{,}66$$
> Como $a, b \in [0, 1] \implies 2b + a \le 3 < 3{,}66$, a condição é universalmente satisfeita para quaisquer taxas de abstenção ou protesto: o tamanho do Bloco 3 é governado pelo teto encolhido $U$ (e eventuais efeitos residuais de arredondamento ou heterogeneidade entre UFs continuam estritamente cobertos pelo operador $\min$).

**2b. Divisão interna do Bloco 3:** $H_3$ cadeiras são repartidas entre as colunas ativas $c \in C_3$ (3 a 6 colunas, `D-17`) por Sainte-Laguë sobre $V_c$, utilizando sucessivamente o quociente $Q_c = V_c / (2 h_c + 1)$ com desempate determinístico (maior quociente, maior $V_c$, ordem alfabética do identificador).

**2c. Divisão do Bloco 2 com piso protetor:** $H_2$ é repartido separadamente entre as 6 colunas permanentes $c \in C_2$ por Sainte-Laguë com restrição inferior $f_c = 20$. Cada coluna inicia com $f_c$ assentos e o restante é distribuído passo a passo pelo maior quociente $Q_c$, reajustando exclusivamente as colunas permanentes do Bloco 2, existindo divisor de equilíbrio $D > 0$ tal que:

$$h_c = \max\left(f_c, \; [\![V_c / D]\!]\right), \qquad \sum_{c \in C_2} h_c = H_2$$

Como $H_2 = 333 - H_3 \ge 333 - 91 = 242 > 120 = 6 \times 20$, a viabilidade do piso protetor é matematicamente garantida em qualquer cenário.

**2d. Bloco 1:** para todas as colunas $c \in C_1$, fixa-se $h_c = 60$.

### Etapa 3 — Alocação matricial biproporcional e contingência (`biproporcional.py`)

O núcleo matemático maximiza a função objetivo côncava estritamente separável de Balinski & Demange (1989) e Gaffke & Pukelsheim (2008):

$$\Phi(X) = \sum_{e \in E} \sum_{c} \sum_{k=1}^{x_{e,c}} \ln\left(\frac{\tilde{v}_{e,c}}{k - 0{,}5}\right), \qquad \tilde{v}_{e,c} = \begin{cases} v_{e,c}, & \text{se } v_{e,c} > 0 \\ \epsilon = 10^{-9}, & \text{se } v_{e,c} = 0 \end{cases}$$

A suavização com $\epsilon = 10^{-9}$ materializa a **contingência lexicográfica (`RT-09`)**: células sem votos recebem utilidade marginal fortemente negativa ($\ln 10^{-9}$), garantindo que nenhuma chapa sem votos eleitorais receba mandato, exceto na hipótese extrema de impossibilidade matemática de fechamento das margens constitucionais utilizando apenas células positivas.

O algoritmo `alocar_biproporcional` opera em **duas fases exatas**:
1. **Fase 1 (Escalonamento Alternado — TIES):** alterna ajustes proporcionais de Sainte-Laguë pelas linhas ($\lambda_e$) e pelas colunas ($\mu_c$), até convergência exata de todas as somas de linha e coluna (limite padrão `MAX_ITERACOES_PADRAO = 60`).
2. **Fase 2 (Refinamento Exato por Fluxo de Utilidade Marginal — Bellman–Ford):** caso empates discretos deixem divergência entre somas de linha após o limite da Fase 1, constrói um grafo bipartido direcionado entre UFs superavitárias e deficitárias com arestas ponderadas pela perda marginal $-\Delta \Phi$ (`+ln(v~/(x - 0.5))` na redução e `-ln(v~/(x + 0.5))` na adição) e aplica **Bellman–Ford livre de ciclos** para transferir assentos ao longo do caminho aumentante de menor perda (maior ganho de utilidade $\Delta \Phi$) até zerar todo desvio marginal.

A Etapa 3 executa esse motor em dois estágios sequenciais:
- **Etapa 3a — Matriz de Missão ($E \times C_3$) com teto por linha (`alocar_matriz_missao`):** busca $y_{e,c} \ge 0$ satisfazendo $\sum_e y_{e,c} = h_c$ e $\sum_{c \in C_3} y_{e,c} \le u_e$. Quando $H_3 < U$, aplica-se o teorema da **coluna complementar de folga** (`__FOLGA__`, Gaffke & Pukelsheim 2008) com margem $U - H_3$ e voto neutro `max(1, round(soma_votos / (|E| * |C_3|)))`; após a convergência biproporcional, descarta-se a coluna de folga e definem-se os mandatos estaduais de missão $m_e = \sum_{c \in C_3} y_{e,c}$.
- **Etapa 3b — Matriz Principal ($E \times (C_1 \cup C_2)$):** aloca $x_{e,c}$ com somas de linha iguais à bancada estadual remanescente $s_e - m_e$ e somas de coluna iguais a $h_c$. (Observe-se que nesta etapa utilizam-se apenas os vetores estaduais $v_{e,c}$, mantendo $v_{ext,c}$ exclusivamente na totalização nacional da Etapa 0 e Etapa 2.)

### Etapa 4 — Eleição dos indivíduos e suplência regional (`pipeline.py`)

1. **Alocação intracelular por STV enxuto (`apurar_celula_stv`):** em cada célula $(e, c)$ com $m > 0$ cadeiras:
   - **Cota de Droop:** $q = \lfloor V_{e,c} / (m + 1) \rfloor + 1$, onde $V_{e,c}$ soma os votos nominais de 1ª preferência, os votos de legenda partidária de 2 dígitos na Tela 2 (`votos_confianca_partido`) e os votos em branco/nulo neutros na Tela 2 da coluna (`votos_confianca_coluna`).
   - **Distribuição dos votos da Tela 2 (Bloco 3):** `votos_confianca_coluna` (branco/nulo neutro na Tela 2) é primeiramente rateado proporcionalmente à votação nominal (`votos_primeira`) entre todos os candidatos da célula — com total neutralidade entre partidos; em seguida, `votos_confianca_partido` (legenda de 2 dígitos) completa prioritariamente a pontuação de candidatos daquele partido que ainda precisem atingir $q$.
   - **Transferências (`transferir_votos`, cascata mutuamente exclusiva):** excedentes de eleitos (acima de $q$) e pontuações de candidatos eliminados são redistribuídos seguindo estritamente o primeiro nível aplicável:
     1. Havendo `votos_segunda > 0` agregados nos candidatos ativos da célula, rateia proporcionalmente a `votos_segunda` entre os ativos (regime oficial do **STV enxuto** com 2ª opção estritamente opcional, `D-12` / `RT-16`);
     2. Senão, havendo `votos_terceira > 0` nos ativos, rateia proporcionalmente a `votos_terceira` entre os ativos (mantido no motor por generalidade algorítmica);
     3. Senão, na ausência de preferências subsequentes declaradas, rateia proporcionalmente a `max(1, votos_primeira)` entre os correligionários ativos do **mesmo partido** na célula (`D-12`);
     4. Senão (inexistindo correligionários ativos na célula), rateia proporcionalmente a `max(1, votos_primeira)` entre todos os candidatos ativos restantes.
2. **Suplência regionalizada (`buscar_suplente_regiao`, `D-20` / `RT-11`):**
   - **Nível 1:** próximo não eleito do **mesmo partido na mesma célula** $(e, c)$;
   - **Nível 2:** esgotada a célula local, o candidato não eleito mais bem votado do **mesmo partido na mesma coluna $c$ em outra UF pertencente à mesma macrorregião geográfica oficial do IBGE** (`N`, `NE`, `CO`, `SE` ou `S`).

---

## 4. Invariantes constitucionais e métricas (`metricas.py`)

A função `auditar_invariantes_constitucionais` certifica formalmente a integridade jurídica e aritmética de cada eleição simulada através das **6 invariantes booleanas** do `RelatorioInvariantes` (além da verificação explícita de não-negatividade de todas as células):

| Invariante (`RelatorioInvariantes`) | Definição formal | Finalidade |
|---|---|---|
| 1. `soma_total_513` | $\sum_{e,c} (x_{e,c} + y_{e,c}) = 513$ | Conservação estrita de vagas da Câmara. |
| 2. `pacto_federativo_intacto` | $\sum_{c \in C} (x_{e,c} + y_{e,c}) = s_e \;\; \forall e \in E$ | Garantia integral das bancadas estaduais (Art. 45 CF/88). |
| 3. `fechamento_tematico_intacto` | $\sum_{e \in E} x_{e,c} = h_c \;\; \forall c \in C_1 \cup C_2$; idem $y_{e,c}$ para $C_3$ | Soberania das preferências temáticas nacionais. |
| 4. `nucleo_estado_60_fixo` | $\sum_{e \in E} x_{e,c} = 60 \;\; \forall c \in C_1$ | Estabilidade absoluta da Tríade Generalista (180 vagas). |
| 5. `pisos_permanentes_respeitados` | $\sum_{e \in E} x_{e,c} \ge 20 \;\; \forall c \in C_2$ | Rede de proteção das 6 colunas permanentes. |
| 6. `tetos_missao_respeitados` | $m_e = \sum_{c \in C_3} y_{e,c} \le u_e \;\; \forall e \in E$ | Contenção federativa e eficácia do voto de protesto. |

Adicionalmente, `simulador/src/metricas.py` implementa quatro métricas analíticas:
- **Índice de Gallagher ($LSq$):** $LSq = \sqrt{\frac{1}{2} \sum_i (v_i\% - s_i\%)^2}$, aplicável tanto à desproporcionalidade partidária quanto à desproporcionalidade temática dos Blocos 2+3;
- **Índice de concentração de Herfindahl ($HHI$):** $\sum_i p_i^2$, medindo concentração regional por UF dentro de cada coluna (`D-06`);
- **Número efetivo de partidos ($N_{eff}$):** índice de Laakso–Taagepera ($1 / HHI$);
- **Curva de sobrevivência partidária (`RT-20` / `M-10`):** proporção de partidos com $\ge 1$ assento nas faixas nacionais $[1\%, 3\%)$, $[3\%, 6\%)$ e $[6\%, 10\%)$.

---

## 5. Escopo validado vs. calibração futura com dados reais

| Etapa | Status atual | Descrição |
|---|---|---|
| **Validação algorítmica e invariantes** | **Concluída** | 112 testes unitários e de integração (`simulador/tests/`), incluindo Monte Carlo de 20 sementes aleatórias, testes de monotonicidade, contingência `RT-09`, voto neutro na Tela 2 (`D-15`), cláusula de desempenho individual de 10% da Cota de Droop, exatidão racional em $H_3$, guarda $V_{C_2}=0$ e suíte `RT-19`–`RT-23` (com calibração `72s + 15s = 87s` do STV simplificado). |
| **Calibração intermediária de filas do STV enxuto (`RT-21`)** | **Antes do PLP (Bloco 2)** | Mensurar o impacto de tempo de cabine para 1 número obrigatório + 2ª opção estritamente opcional e rápida (`Q-08`). |
| **Calibração empírica (TSE 2022) e proxy temático** | **Prevista para o Bloco 3** | Classificação temática de candidaturas das eleições de 2022 (Portal de Dados Abertos do TSE) por comissões, ocupação declarada e palavras-chave, comparando sistema atual × distrital misto × RTP no Estudo Técnico. |
| **Conferência cruzada externa (BAZI)** | **Opcional / auditoria complementar** | Confrontação das matrizes geradas pelo solver interno em Python contra o software BAZI (Universidade de Augsburg). |

---

## 6. Implementação oficial (`simulador/`)

Desenvolvido exclusivamente com a **Biblioteca Padrão do Python 3.12** (zero dependências externas) para permitir inspeção independente imediata por parlamentares, pesquisadores, jornalistas e tribunais eleitorais, particionado sob o padrão `BLK-L`:

| Bloco | Arquivo | Responsabilidade |
|---|---|---|
| `BLK-L-001` | [`src/constantes.py`](../simulador/src/constantes.py) | Bancadas das 27 UFs (soma 513), 5 macrorregiões IBGE, 12 colunas e parâmetros constitucionais. |
| `BLK-L-002` | [`src/teto_missao.py`](../simulador/src/teto_missao.py) | Cálculo de $\tau_e$, arredondamento Sainte-Laguë *half-up*, $u_e = [\![\tau_e \cdot a_e]\!]$ (`RT-01`) e lógica das 2 telas do Voto 4 (`RT-04`). |
| `BLK-L-003` | [`src/sainte_lague.py`](../simulador/src/sainte_lague.py) | Sainte-Laguë 1D com pisos protetores, tetos máximos e divisor de equilíbrio $D$. |
| `BLK-L-004` | [`src/biproporcional.py`](../simulador/src/biproporcional.py) | Balinski–Demange 2D (TIES + Bellman–Ford + contingência $\epsilon = 10^{-9}$ `RT-09` + coluna de folga `Gaffke-Pukelsheim`). |
| `BLK-L-005` | [`src/metricas.py`](../simulador/src/metricas.py) | Gallagher ($LSq$), Laakso–Taagepera ($N_{eff}$), Herfindahl ($HHI$), curva de sobrevivência (`RT-20`) e auditoria das 6 invariantes. |
| `BLK-L-006` | [`src/pipeline.py`](../simulador/src/pipeline.py) | Pipeline nacional completo das Etapas 0 a 4, votos do exterior/trânsito (`RT-29`), até 6 missões (`RT-02`), STV enxuto com voto neutro da Tela 2 e suplência regional (`RT-11`). |
| `BLK-L-007` | [`src/estresse_redteam.py`](../simulador/src/estresse_redteam.py) | Os 5 experimentos determinísticos de estresse do Red Team (`RT-19` a `RT-23`). |
| `BLK-L-008` | [`rodar_cenario.py`](../simulador/rodar_cenario.py) | Script CLI de execução ponta a ponta que imprime a matriz $27 \times 12$, invariantes e todos os testes de estresse. |

---

## 7. Laço de iteração (questões resolvidas pelo simulador)

| Questão do Red Team / Desenho | Resposta empírica do simulador | Ref. |
|---|---|---|
| O tamanho do Bloco 3 segue governado pelo teto encolhido $U$ com heterogeneidade entre UFs? | **Sim.** No cenário nacional, $U = 74 \implies H_3 = 74$ e $H_2 = 259$, mantendo desproporcionalidade temática de apenas $4{,}82\text{ p.p.}$ | RT-12, `rodar_cenario.py` |
| O piso de 20 protege colunas minoritárias sem distorcer o restante? | **Sim.** `C09_CIENCIA_TRABALHO` recebe 20 assentos (HHI $0{,}1000$) enquanto as demais colunas refletem os votos com exatidão. | D-08, D-09 |
| O algoritmo biproporcional converge e fecha todas as invariantes? | **Sim.** Matriz de missão: atinge 60 iterações TIES (`MAX_ITERACOES_PADRAO`, resíduo discreto na Fase 1) com fechamento exato via Bellman–Ford na Fase 2; matriz principal: converge em 11 iterações TIES; 6/6 invariantes aprovadas e 0 violações em 20 sementes Monte Carlo. | `metricas.py`, `test_invariantes.py` |
| Como calibrar a interface de urna do STV (`RT-03`) sem criar filas às 17h? | **Simples (1 número/escolha por tela, ~55s):** apenas 1 eleitor residual às 17h; **ranqueamento longo (~130s):** colapsa com 97 eleitores na fila. Orienta a adoção do STV enxuto (até 2ª opção estritamente opcional, a calibrar em tempo intermediário no `RT-21` antes do PLP). | RT-21, D-12 |

---

## 8. Resultados empíricos consolidados (`rodar_cenario.py`)

### 8.1 Cenário demonstrativo nacional ($27 \text{ UFs} \times 12 \text{ Colunas} = 513 \text{ cadeiras}$)
Com taxas simuladas de validade no Voto 4 variando entre $68\%$ e $88\%$ por UF e inclusão de votos no exterior/trânsito (`votos_exterior_transito`):
- **Bloco 1 (Estado):** 180 cadeiras fixas (`C01_ECONOMIA`: 60; `C02_JUSTICA`: 60; `C03_SOCIAL`: 60).
- **Bloco 2 (Permanentes):** 259 cadeiras (`C04_SAUDE`: 62; `C05_EDUCACAO`: 52; `C06_SEGURANCA`: 51; `C07_INFRAESTRUTURA`: 39; `C08_AGRO_AMBIENTE`: 35; `C09_CIENCIA_TRABALHO`: 20 — piso protetor acionado).
- **Bloco 3 (Missões):** 74 cadeiras, igual ao teto encolhido $U = 74$ (`C10_MISSAO_1`: 30; `C11_MISSAO_2`: 25; `C12_MISSAO_3`: 19).
- **Desproporcionalidade temática (Blocos 2 + 3):** Índice de Gallagher $LSq = 4{,}82\text{ p.p.}$
- **Auditoria constitucional:** 6/6 invariantes `True` (`aprovado = True`); matriz de missão: 60 iterações TIES (limite `MAX_ITERACOES_PADRAO`) + fechamento exato via Bellman–Ford na Fase 2 / matriz principal: 11 iterações TIES.

### 8.2 Os 5 experimentos de estresse do Red Team (`RT-19` a `RT-23`)

| Experimento | Cenário estressado (`estresse_redteam.py`) | Achado quantitativo exato (`rodar_cenario.py`) | Implicação institucional |
|---|---|---|---|
| **`RT-19`** (Voto de Enterro, `Q-05`) | 500.000 eleitores estratégicos de Saúde enterram o 2º voto em Ciência (travada no piso de 20). | Ganho estratégico de **+1 cadeira** (Saúde: Sincero = 80 vs. Enterro = 81; Ciência travada no piso = `True`). | Impacto residual baixo sob Sainte-Laguë; mesmo sob coordenação estratégica, a distorção é marginal. |
| **`RT-20`** (Puxador Temático, `RT-16`) | Choque de +2.500.000 votos na coluna de Segurança (`C06_SEGURANCA`) em SP. | Segurança cresce **+5 cadeiras** no país: **+4 em SP** e apenas **+1 transbordada** para outra UF; bancada total de SP permanece travada em **70**. | Confirma contenção espacial satisfatória do efeito puxador sem violar o pacto federativo. |
| **`RT-21`** (Filas de Seção, `U-04`) | Seção de 400 eleitores (80% comparecimento = 320 votantes, 9h = 540 min, +15s biometria). | Sem ranqueamento longo (55s): **1 eleitor na fila às 17h (0,1 min extra)**. Com ranqueamento longo (130s): **97 na fila às 17h (234,1 min extras)**. | Prova necessidade de interface simples por tela, vedando ordenações extensas na urna (base para o STV enxuto de até 2ª opção opcional). |
| **`RT-22`** (Comparecimento Desigual, `U-03`) | 82% de comparecimento nas 12 UFs com 2º turno de Governador vs. 55% nas 15 UFs sem 2º turno. | **Desvio nas bancadas das UFs = 0 cadeiras**; deslocamento líquido entre colunas nacionais = **2 cadeiras** (em 513). | Garante neutralidade federativa absoluta do pleito legislativo no 2º turno. |
| **`RT-23`** (Atraso de Apuração, `U-08`) | Últimos 2% dos votos nacionais ainda pendentes em UFs remotas da Amazônia Legal (`AC`, `AM`, `AP`, `RR`). | **511 / 513 cadeiras (99,6%) já matematicamente definidas**; apenas **2 cadeiras marginais** aguardam fechamento. | Viabiliza proclamação quase integral do Parlamento já na noite da eleição. |

---

## Anexo A — Teto nominal de missão por UF ($\rho = 0{,}20$, $\tau_e = \lfloor \rho \, s_e \rfloor$, bancadas Art. 45)

| UF | $s_e$ | $\tau_e$ | | UF | $s_e$ | $\tau_e$ |
|---|---|---|---|---|---|---|
| SP | 70 | 14 | | SC | 16 | 3 |
| MG | 53 | 10 | | PB | 12 | 2 |
| RJ | 46 | 9 | | ES | 10 | 2 |
| BA | 39 | 7 | | PI | 10 | 2 |
| RS | 31 | 6 | | AL | 9 | 1 |
| PR | 30 | 6 | | AC, AM, AP, DF, MS, MT, RN, RO, RR, SE, TO | 8 cada | 1 cada (11) |
| PE | 25 | 5 | | | | |
| CE | 22 | 4 | | | | |
| MA | 18 | 3 | | | | |
| GO | 17 | 3 | | | | |
| PA | 17 | 3 | | **Total** | **513** | **91** |

*(Observação: nas 12 UFs com $\tau_e = 1$, o teto efetivo $u_e = [\![\tau_e \, a_e]\!]$ resulta em $1$ sempre que $a_e \ge 0{,}50$, e em $0$ quando $a_e < 0{,}50$.)*

## Anexo B — Referências técnicas
- Balinski, M. & Demange, G. (1989). *An axiomatic approach to proportionality between matrices.* Mathematics of Operations Research.
- Balinski, M. & Young, H. P. (1982/2001). *Fair Representation.*
- Gaffke, N. & Pukelsheim, F. (2008). *Vector and matrix apportionment problems and separable convex integer optimization.* Math. Methods of Operations Research.
- Gallagher, M. (1991). *Proportionality, disproportionality and electoral systems.* Electoral Studies.
- Laakso, M. & Taagepera, R. (1979). *"Effective" Number of Parties: A Measure with Application to West Europe.* Comparative Political Studies.
- Pukelsheim, F. (2017). *Proportional Representation: Apportionment Methods and Their Applications.* Springer.
- Taagepera, R. & Shugart, M. (1989). *Seats and Votes.*
