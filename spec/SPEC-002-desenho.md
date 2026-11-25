# SPEC-002-D — Desenho Institucional do Sistema de Representação Temática Proporcional

| Campo | Valor |
|---|---|
| Versão | 0.2 (consolidada pós-Red Team e Simulador) |
| Substitui | SPEC-001 (`spec.md`, mantido como histórico) e rascunho v0.1 |
| Documento par | [SPEC-002-tecnico.md](SPEC-002-tecnico.md) — modelo matemático e algoritmo |
| Registro de decisões | [decisoes.md](../decisoes.md) — IDs `D-01` a `D-23` |
| Red Team | [RT-01-consolidado.md](../redteam/RT-01-consolidado.md) — itens `RT-01` a `RT-30` |
| Simulador auditável | [simulador/README.md](../simulador/README.md) — código de referência Python 3.12 |

> **Escopo deste documento:** o *quê* e o *porquê*. Regras institucionais, justificativas, trade-offs assumidos e questões em aberto, parametrizadas ou delegadas à regulamentação regimental/infraconstitucional. Fórmulas, algoritmos, métricas e resultados empíricos detalhados ficam no documento técnico par.

---

## 1. Problema e objetivos

### 1.1 Diagnóstico (a fundamentar com dados no Estudo Técnico)
1. **Divórcio entre campanha e trabalho legislativo:** o eleitor vota numa pessoa, mas não sabe em que área ela vai atuar. A lotação em comissões é decidida depois, por acordo partidário.
2. **Transferência opaca de votos:** no sistema proporcional de lista aberta, o voto num "puxador" elege candidatos que o eleitor não conhece nem escolheu para aquela agenda.
3. **Ausência de sinal de prioridade:** a composição temática da Câmara não reflete o que o eleitorado considera prioritário.
4. **Agenda do Executivo negociada fora do voto:** a base de apoio ao programa de governo é montada por barganha pós-eleitoral, e não por mandato popular explícito.

### 1.2 Princípios de desenho
| # | Princípio |
|---|---|
| P1 | **Mandato temático:** o deputado é eleito *para* uma área e atua com exclusividade nela. |
| P2 | **Preferência revelada:** o tamanho das bancadas temáticas é decidido pelo voto. |
| P3 | **Pacto federativo intacto:** o total de cadeiras de cada Unidade Federativa não muda (Art. 45, §1º, CF/88). |
| P4 | **Estabilidade do núcleo de Estado:** as funções fiscal, jurídica e social têm bancadas fixas. |
| P5 | **Poder presidencial limitado, plural e condicionado:** a agenda prioritária do Executivo tem bancada própria, porém limitada em teto (20% por UF), aberta aos temas dos dois finalistas e passível de encolhimento por voto de protesto. |
| P6 | **Voto simples, cálculo rigoroso:** a complexidade fica na apuração auditável em código aberto, não na urna. |

---

## 2. Arquitetura: Colunas Temáticas em 3 Blocos

No cenário-base (3 temas de missão ativos), a Câmara estrutura-se em **12 colunas temáticas**; havendo segundo turno presidencial sem sobreposição total de agendas, o Bloco 3 comporta **até 6 colunas de missão ativas** (totalizando até 15 colunas ativas na legislatura), sempre dentro dos mesmos **513 assentos** federativos (D-17, RT-02).

| Bloco | Colunas | Cadeiras | Regra de tamanho | Ref. |
|---|---|---|---|---|
| **1. Estado (Generalistas)** | 3 | **180 fixas** (60 cada) | Fixo: 60 é piso e teto ao mesmo tempo. O voto define *quem* entra e *de qual UF*, não *quantos*. | D-08 |
| **2. Permanentes (Especialistas)** | 6 | 333 − Bloco 3 | Proporcional aos votos nacionais após definido $H_3$, com **piso protetor de 20** por coluna permanente. | D-08, D-09 |
| **3. Missão (Plano de Governo)** | **3 a 6 ativas** | 0 a $\le 91$ | Proporcional aos votos, **sem piso (piso 0)**, com teto por UF de 20% ($\tau_e = \lfloor 0{,}20 \cdot s_e \rfloor$) que **encolhe conforme os votos de protesto na Tela 1** ($u_e = [\![\tau_e \cdot a_e]\!]$). | D-13, D-15, D-17, RT-01, RT-02 |

### 2.1 Bloco 1 — Colunas de Estado (Tríade Generalista)
1. Economia, Finanças e Orçamento
2. Constituição, Justiça e Cidadania
3. Desenvolvimento Humano, Ética e Direitos Sociais

**Justificativa do tamanho fixo:** impede que uma área estrutural cresça demais ou encolha abaixo do necessário para revisar sistematicamente os projetos, além de constituir o núcleo estável responsável pelo despacho temático (D-18) e pela composição sorteada das Assembleias de Projeto (D-05).

### 2.2 Bloco 2 — Colunas Permanentes
4. Saúde e Saneamento
5. Educação, Cultura e Esporte
6. Segurança Pública e Defesa Nacional
7. Infraestrutura, Logística, Energia e Cidades
8. Agropecuária, Meio Ambiente e Recursos Naturais
9. Ciência, Tecnologia, Indústria e Trabalho

> **Decisão consolidada sobre a Coluna 8 (`D-07` / `RT-15` / `Q-12`):** considerou-se explicitamente desmembrar Agropecuária e Meio Ambiente em duas colunas permanentes autônomas (elevando o Bloco 2 para 7 colunas), hipótese apontada pelo Red Team para aliviar a disputa de legendas ambientalistas na mesma célula. Optou-se, porém, por **manter a Coluna 8 unificada (6 colunas permanentes)** por três motivos: (1) **deliberação sustentável integrada**, evitando uma guerra paralisante de vetos setoriais entre duas comissões antagônicas e forçando a construção de conciliações produtivas e ambientais no mesmo colegiado; (2) **preservação das magnitudes por célula**, pois uma 7ª permanente elevaria o piso mínimo fixo do Bloco 2 de 120 para 140 cadeiras, comprimindo a proporcionalidade; e (3) **flexibilidade programática**, uma vez que agendas climáticas e de transição ecológica urgentes podem ser ativadas temporariamente via Bloco 3 de Missão. O aprofundamento comparado de modelos estrangeiros e impactos partidários será desenvolvido no Estudo Técnico.

**Piso protetor de 20:** é exclusivamente uma **rede de proteção interna do Bloco 2** (D-09). Após definir o tamanho global do Bloco 3 ($H_3$) e o saldo do Bloco 2 ($H_2 = 333 - H_3$), repartem-se separadamente $H_3$ entre as colunas de missão ativas e $H_2$ entre as 6 colunas permanentes pelo método de Sainte-Laguë; na repartição interna do Bloco 2, a coluna permanente que ficar abaixo de 20 sobe para 20 e apenas as demais colunas permanentes se reajustam, garantindo quórum funcional mesmo para temas minoritários.

### 2.3 Bloco 3 — Colunas de Missão Presidencial
- **Catálogo oficial:** rol fixo de 10 a 15 temas estratégicos aprovado pelo Congresso Nacional em Lei Complementar (D-01). Exemplos ilustrativos: Transição Energética; Inteligência Artificial e Soberania Digital; Reindustrialização e Malha Ferroviária; Segurança de Fronteiras e Cibersegurança.
- **Ativação plural dos dois finalistas (D-17 / RT-02):** cada candidato a Presidente registra no TSE 3 temas do catálogo junto com o Plano de Governo. Na eleição legislativa (data do 2º turno), permanecem ativos na urna os temas prioritários de **ambos os finalistas presidenciais** (3 colunas se houver eleição presidencial decidida no 1º turno ou coincidência integral de temas; até 6 colunas distintas se houver 2º turno sem sobreposição).
  - *Regra descartada:* fica expressamente descartado o descarte sumário de votos dados em temas de um finalista derrotado, para evitar violação da soberania do sufrágio por fato externo e insegurança jurídica sobre a elegibilidade de candidatos (RT-02).
  - *Efeito institucional:* a bancada de missão passa a refletir proporcionalmente a força eleitoral de ambas as agendas finalistas (governo e oposição), diluindo riscos de concentração palaciana e dissolvendo a objeção de uma "guarda pretoriana" exclusiva do Presidente (RT-18).
- **Ausência de reserva automática:** o Executivo não reserva cadeiras; escolhe temas de um cardápio legislativo e quem preenche as vagas (ou as deixa em zero) é exclusivamente o voto popular.
- **Teto estadual e arredondamento corrigido (D-13 / RT-01):** o teto nominal por UF é $\tau_e = \lfloor 0{,}20 \cdot s_e \rfloor$, somando **91 cadeiras** em nível nacional (~17,7% da Câmara). O teto efetivo após o escrutínio é obtido pelo **arredondamento de Sainte-Laguë** ($u_e = [\![\tau_e \cdot a_e]\!]$, onde frações $\ge 0{,}5$ sobem), evitando que um único voto em branco zere o teto das 12 UFs com $\tau_e = 1$: nessas UFs (8 ou 9 deputados), mantém-se 1 cadeira de missão desde que os votos válidos na Tela 1 atinjam pelo menos 50% (RT-01).
- **Encolhimento por protesto deliberado (D-15 / RT-04 / RT-14):** no fluxo de 2 telas do Voto 4, os votos em branco ou nulos na **Tela 1** (escolha do tema) são votos de protesto e reduzem a taxa $a_e$, encolhendo $u_e$ em benefício das colunas permanentes do próprio Estado. O protesto organizado contra a agenda de missão é assumido como **trade-off deliberado e freio federativo legítimo (RT-14)**, criando incentivo direto para campanhas presidenciais interiorizadas em todos os Estados.

---

## 3. Calendário eleitoral e campanha (HGPE)

### 3.1 Data fixa do pleito legislativo (D-02, D-14, RT-17)
- **1º turno:** eleições para Presidente da República, Governadores, Senadores e Deputados Estaduais/Distritais, conforme o calendário constitucional vigente.
- **Data fixa do 2º turno (em todo ciclo):** realização incondicional da eleição para a Câmara dos Deputados, **mesmo que o Presidente da República tenha sido eleito no 1º turno**, ocorrendo em conjunto com o 2º turno presidencial e estadual onde houver.
- **Justificativa institucional:** além de garantir que na data do voto legislativo as missões de Bloco 3 já estejam delimitadas aos finalistas presidenciais, a autonomia temporal assegura que o debate parlamentar e programático da Câmara não seja ofuscado pela disputa majoritária presidencial. Eventuais diferenças de comparecimento entre Estados com e sem 2º turno estadual não alteram em nada as bancadas federativas $s_e$ dos Estados (conforme demonstrado no experimento `RT-22`).

### 3.2 Campanha defasada e horário eleitoral (D-23 / RT-08)
- A campanha eleitoral específica para Deputado Federal inicia-se **15 dias após** o início geral das campanhas (por volta de 1º de setembro) e transcorre de modo contínuo até a data fixa do 2º turno (fim de outubro).
- **Efeito operacional:** preserva exatamente a duração total de campanha (~55 a 60 dias), o mesmo teto legal de gastos de campanha e as regras de financiamento (Fundo Eleitoral), enquanto libera o Horário Gratuito de Propaganda Eleitoral (HGPE) em rádio e televisão no mês de outubro para foco exclusivo na Presidência (quando houver 2º turno) e nas colunas temáticas ativas da Câmara dos Deputados (12 no cenário-base; até 15 com 6 missões), sem concorrência com campanhas estaduais e senatoriais já decididas no 1º turno.

### 3.3 Alternativas documentadas (D-03)
Permanecem registradas como alternativas de calendário caso o legislador opte por separação temporal mais ampla:
- (a) Eleições do Executivo e do Legislativo em **anos distintos** (com mandatos-tampão de transição no ADCT);
- (b) Eleição presidencial no **1º semestre** e legislativa no **2º semestre** do mesmo ano.

---

## 4. A cédula eletrônica: ordem na urna, numeração e exterior

### 4.1 Ordem oficial dos votos na urna (D-15 / RT-04)
Para contextualizar politicamente a escolha de missão e impedir que o cansaço de cabine penalize as UFs de menor comparecimento/escolaridade nos votos finais, a sequência oficial na urna passa a ser:

$$\text{Presidente} \;\longrightarrow\; \text{Voto 4 (Missão, em 2 telas)} \;\longrightarrow\; \text{Voto 1 (Estado)} \;\longrightarrow\; \text{Voto 2 (Permanente)} \;\longrightarrow\; \text{Voto 3 (Permanente)}$$

| Ordem na urna | Voto | Natureza da escolha | Efeito principal |
|---|---|---|---|
| **1º (quando houver)** | Presidente | Executivo nacional | Contextualiza os programas e finalistas no momento do pleito. |
| **2º (2 telas)** | **Voto 4** | **Missão Presidencial** (Tela 1: tema; Tela 2: candidato, legenda ou confiança neutra) | Dimensiona e preenche o Bloco 3; **branco/nulo na Tela 1** = protesto que encolhe $u_e$; **branco/nulo na Tela 2** = confiança temática neutra na coluna (não encolhe $u_e$). |
| **3º** | **Voto 1** | **Coluna de Estado** (Bloco 1) | Define *quem* ocupa as 180 cadeiras fixas (60 por coluna) e sua origem estadual. |
| **4º e 5º** | **Votos 2 e 3** | **Colunas Permanentes** (Bloco 2) | Definem o tamanho proporcional das 6 colunas (protegidas pelo piso de 20) e os eleitos. |

**Funcionamento detalhado do Voto 4 em 2 telas (D-15 / RT-04):**
1. **Tela 1 — Adesão ou Protesto Temático:** o eleitor escolhe uma das colunas de missão ativas para apoiar ou manifesta voto em branco/nulo de protesto contra o bloco. Apenas o branco/nulo nesta Tela 1 é contabilizado como não válido ($w_e^{prot}$) para encolher o teto estadual $u_e$.
2. **Tela 2 — Candidato, Legenda Partidária ou Confiança Neutra:** tendo selecionado uma missão na Tela 1 (sem escolha prévia de partido), o eleitor dispõe de três opções dentro do tema escolhido:
   - *(i) Número completo de candidato:* voto nominal direto;
   - *(ii) Legenda partidária (2 dígitos):* voto na legenda daquele partido dentro da coluna de missão escolhida (`votos_confianca_partido`);
   - *(iii) Branco ou nulo na Tela 2:* opera como **voto de confiança temática neutro** (`votos_confianca_coluna`) — permanece 100% válido para o dimensionamento da coluna de missão nas Etapas 1–3 (não encolhe $u_e$) e, na apuração intracelular da Etapa 4, é **rateado proporcionalmente entre todos os partidos e candidatos daquela coluna** (neutro entre legendas).

### 4.2 Numeração padronizada e ergonomia de cabine (RT-07 / RT-21 / D-12)
- **Prefixo identificador por coluna (RT-07):** a numeração de campanha dos candidatos adota prefixo padronizado que identifica o bloco e a coluna temática. A urna eletrônica exibe validação e alerta em tela caso o eleitor digite prefixo de coluna distinta da tela ativa antes de confirmar, evitando votos nulos involuntários. Trata-se de matéria técnica delegada à Lei Complementar e às resoluções do TSE.
- **Restrição empírica de filas e diretriz do STV enxuto (RT-21 / D-12):** a simulação operacional em seção típica de 400 eleitores (80% de comparecimento) demonstrou que entradas simples de 1 número por tela (~55s de votação + 15s de biometria) encerram às 17h com apenas **1 eleitor residual na fila (0,1 min extra)**, ao passo que interfaces de ranqueamento longo de múltiplas preferências (~130s + 15s) deixariam **97 eleitores na fila às 17h (+234,1 minutos extras)**. Consequentemente, adota-se para os Votos 1, 2 e 3 o modelo de **STV enxuto**: cada tela exige **1 número obrigatório** e faculta no máximo uma **2ª opção estritamente opcional e rápida**, vedando ordenações extensas de 3 ou mais preferências; na ausência de 2ª opção declarada, a transferência opera automaticamente no mesmo partido. O tempo de cabine intermediário dessa 2ª opção será calibrado em `RT-21` antes da redação do PLP (`Q-08`).

### 4.3 Eleitores no exterior (Zona ZZ) e em trânsito interestadual (D-22 / RT-29)
- Eleitores habilitados na Zona Eleitoral do Exterior (ZZ) ou votando em trânsito fora de sua UF de domicílio eleitoral participam da eleição legislativa por meio de **voto em legenda temática pura** (escolhem diretamente uma coluna temática sem indicação nominal estadual).
- Esses sufrágios integram a soma nacional $V_c$ da respectiva coluna, influenciando o dimensionamento nacional dos temas sem alterar as cotas federativas rígidas dos Estados ($s_e$). A viabilidade constitucional da medida foi validada em parecer jurídico específico do projeto (RT-29).

---

## 5. Distribuição das cadeiras e sucessão por suplência

> A formalização integral e as equações estão em [SPEC-002-tecnico.md](SPEC-002-tecnico.md).

1. **Tamanho dos blocos:** o Bloco 1 tem **180 cadeiras fixas** (60 por coluna). O Bloco 3 recebe $H_3 = \min(U, [\![H_3^{prop}]\!])$, limitado ao menor valor entre sua proporção nos votos e a soma nacional $U = \sum_e u_e$ dos tetos estaduais encolhidos na Tela 1 (teto nominal máximo de 91). O Bloco 2 recebe o saldo restante ($H_2 = 333 - H_3$).
2. **Tamanho nacional de cada coluna:** após fixados $H_3$ e $H_2$, aplicam-se distribuições separadas por **Sainte-Laguë** sobre $V_c$ (já somados os votos do exterior e trânsito): primeiro $H_3$ é repartido entre as colunas de missão ativas ($C_3$); em seguida, $H_2$ é repartido exclusivamente entre as 6 colunas permanentes ($C_2$), aplicando-se o piso protetor de 20 com reajuste restrito às demais colunas permanentes do Bloco 2 (D-09, D-10).
3. **Alocação federativa biproporcional e contingência (D-11 / RT-09):**
   - Primeiro, as cadeiras do Bloco 3 são distribuídas na matriz $(\text{UF} \times C_3)$ sob a restrição superior $u_e$ de cada UF (via formulação de coluna de folga de Gaffke–Pukelsheim);
   - Em seguida, as cadeiras restantes por UF ($s_e - m_e$) e as colunas de Bloco 1 e Bloco 2 são fechadas simultaneamente por **alocação biproporcional de Balinski–Demange** (escalonamento TIES seguido de refinamento exato por caminho aumentante).
   - **Contingência de inviabilidade (RT-09):** aplica-se regularização lexicográfica ($\epsilon = 10^{-9}$) e otimização discreta garantindo que nenhuma célula com zero votos receba mandato, salvo impossibilidade matemática absoluta de fechar as margens constitucionais de outro modo.
   - Estados sem cadeiras em uma coluna específica configuram **preferência federativa legítima** (D-06).
4. **Preenchimento individual nas células (D-12 / RT-03 / RT-16 / D-15):** dentro de cada par $(\text{UF} \times \text{Coluna})$, nos Votos 1, 2 e 3 emprega-se o **STV enxuto** por cota de Droop — computando a escolha obrigatória e, quando informada pelo eleitor, a **2ª opção estritamente opcional** para redistribuição de excedentes e eliminados; na ausência de 2ª opção declarada, a transferência ocorre automaticamente para correligionários do **mesmo partido na mesma célula**. Nas colunas de missão (Voto 4), eventuais votos de legenda de 2 dígitos somam ao respectivo partido no tema e votos em branco/nulo neutros da Tela 2 são rateados proporcionalmente dentro daquela coluna de missão. Em caso de empate individual na célula, prevalece a maior votação nominal direta de 1ª preferência e, persistindo, o critério legal de idade (RT-02). A modelagem detalhada de cotas, piso individual e exaustão de chapas permanece em `Q-08` para o PLP.
5. **Suplência temática regionalizada (D-20 / RT-11):** na vacância de mandato, observa-se ordem sucessória estrita em dois níveis que concilia a titularidade partidária (ADI 5.081, a verificar na fonte primária na fase jurídica) com a integridade técnica da coluna:
   - **1ª prioridade:** suplente do **mesmo partido na mesma célula** $(\text{UF} \times \text{Coluna})$;
   - **2ª prioridade (caso esgotada a célula):** suplente mais votado do **mesmo partido na mesma coluna temática em outra UF da mesma macrorregião geográfica oficial do IBGE**.

---

## 6. Processo legislativo interno e governança

### 6.1 Governança das colunas, despacho e Assembleia de Projeto
- **Lotação exclusiva e presidência própria:** o deputado eleito por uma coluna é membro titular e exclusivo do colegiado temático daquela coluna. Cada coluna temática ativa elege seu próprio **Presidente de Coluna** (D-21). A disciplina de faltas é remetida ao Regimento Interno.
- **Despacho temático colegiado (D-18 / RT-05):** a competência originária para classificar e distribuir os projetos de lei às colunas pertence à **Tríade Generalista** (Bloco 1), por decisão colegiada de maioria simples fundamentada em critérios objetivos fixados em Lei Complementar, assegurado recurso ao Plenário da Câmara dos Deputados também por maioria simples. Retira-se esse poder concentrador do Presidente da Câmara.
- **Assembleia de Projeto, sorteio e conflito de interesses (D-19 / RT-10):** antes de ir a Plenário, toda proposição passa pela Assembleia de Projeto correspondente (bancada da coluna especialista + contingente sorteado de generalistas do Bloco 1). O sorteio dos generalistas é realizado na **data mais próxima possível da deliberação**, com quórum mínimo de presença e transparência ativa obrigatória dos registros de reuniões com agentes setoriais privados. Deputados generalistas com conflito de interesses direto (vínculo econômico ou profissional imediato no setor regulado) são **impedidos de exercer voto deliberativo**, mantendo apenas voz e voto simbólico.

### 6.2 Expansão da Assembleia de Projeto (D-04 / RT-06)
- Nenhuma coluna externa pode se autoindicar para integrar uma Assembleia de Projeto.
- **Exclusão definitiva do STF:** o Supremo Tribunal Federal é expressamente excluído de qualquer iniciativa de provocação ou pedido de expansão temática, preservando sua imparcialidade para eventual controle posterior de constitucionalidade (RT-06).
- **Legitimados e decisão:** podem requerer a inclusão de outra coluna sob alegação de impacto sistêmico o **Poder Executivo** e **órgãos regimentais internos da Câmara** (ex.: fração qualificada de outra coluna), ficando delegada à Lei Complementar eventual extensão à PGR ou à AGU (`Q-06`). Cabe exclusivamente à **Tríade Generalista**, por maioria simples, admitir ou rejeitar o pedido.

### 6.3 Veto Setorial Escalonado (D-05 / RT-13)
- No Plenário da Câmara, todos os 513 deputados têm peso 1.
- **Base de cálculo do veto:** a totalidade da **Assembleia de Projeto** com direito a voto (especialistas da coluna + generalistas sorteados sem conflito de interesses, conforme `D-19`).
- **Quórum escalonado de superação no Plenário (RT-13):**
  - Se a rejeição na Assembleia de Projeto atingir de **40% a menos de 75%** dos votos → o projeto é remetido ao Plenário com bloqueio ordinário, cuja superação exige **Maioria Absoluta (257 votos)**;
  - Se a rejeição na Assembleia de Projeto atingir **75% ou mais** dos votos → configura consenso técnico qualificado, e a superação no Plenário exige **quórum qualificado de 3/5 (308 votos)**.

### 6.4 Orçamento (CMO / Art. 166) e emendas do Senado (D-21 / RT-28)
- **Colegiado Orçamentário da Câmara na CMO:** a representação da Câmara dos Deputados na Comissão Mista de Orçamento passa a ser composta pelos **60 Deputados da Coluna 1 (Economia, Finanças e Orçamento)** somados aos **Presidentes de todas as demais colunas temáticas** com representação na legislatura (**11 presidentes** no cenário-base de 3 missões; **até 14** no cenário de até 6 missões ativas de ambos os finalistas, nos termos de `D-17`). Esse desenho confronta diretamente a capacidade fiscal da Coluna 1 com as necessidades setoriais defendidas pelos presidentes das demais bancadas.
- **Exclusão de veto setorial orçamentário:** o veto setorial **não se aplica** à Lei Orçamentária Anual (LOA) nem às matérias de comissão mista em sessão conjunta do Congresso Nacional, evitando o risco de paralisação do Estado (shutdown).
- **Revisão bicameral de projetos comuns:** emendas aprovadas pelo Senado Federal a projetos de lei ordinários e complementares originários da Câmara retornam à Assembleia de Projeto da coluna temática originária para apreciação.

---

## 7. Trade-offs assumidos e riscos em acompanhamento

### 7.1 Trade-offs explicitamente aceitos
| Trade-off | Posição institucional | Ref. |
|---|---|---|
| Perda de proporcionalidade **partidária** (baixa magnitude por célula UF × Coluna) | Aceita. Partidos especializam-se em áreas; a medir na calibração com dados do TSE e analisar no Estudo Técnico. | D-07, RT-15 |
| Apuração matematicamente complexa (biproporcional) | Aceita. O sistema atual (quocientes/sobras/federações) já é opaco ao público; mitiga-se com código aberto auditável, publicação de multiplicadores e programas de educação cívica. | D-11, RT-25 |
| Estados sem cadeiras em determinados temas | Aceita. Expressa preferência federativa legítima dos eleitores daquela UF. | D-06 |
| Campanhas organizadas pelo voto em branco na Tela 1 (Voto 4) | **Desejada / assumida como função.** Funciona como freio federativo e obriga o Executivo a fazer campanha nacional substantiva nos Estados periféricos. | D-13, D-15, RT-14 |
| Transbordamento de "puxador temático" entre UFs | Aceita e mensurada no simulador (`RT-20`: choque de +2,5M em SP gera +4 cadeiras em SP e apenas +1 em outra UF, mantendo SP fixo em 70). | RT-16, RT-20 |
| Eleição legislativa no 2º turno mesmo sem disputa presidencial | Aceita. Preserva autonomia do debate parlamentar; simulador (`RT-22`) prova 0 de desvio nas bancadas estaduais e apenas 2 cadeiras deslocadas entre temas sob turnout de 82% vs. 55%. | D-14, RT-17, RT-22 |
| Quebra eventual de monotonicidade estrita no STV ou entre blocos | Aceita e documentada na literatura (precedentes na Irlanda e em Malta). | D-12 |
| Risco de "nobreza palaciana" na bancada de missão | **Descartada como impeditivo.** Bancada sem piso mínimo (piso zero), sujeita a encolhimento na Tela 1 e partilhada entre governo e oposição. | RT-18 |

### 7.2 Riscos abertos para endereçamento em etapas posteriores
- **Viabilidade política da aprovação pelos atuais deputados (`RT-24`):** risco principal de qualquer reforma eleitoral; assumido para elevar o debate público nacional em paralelo à pauta do distrital misto.
- **Clientelismo e captura por emendas parlamentares (`RT-26`):** reconhecido como desafio estrutural; endereçável por PEC autônoma ou legislação complementar restritiva de emendas individuais e de comissão.
- **Distinção face a sistemas corporativistas históricos (`RT-27`):** diferenciar no Estudo Técnico frente a modelos como Seanad (Irlanda), Hong Kong e Eslovênia com base na **universalidade integral do sufrágio** (todo cidadão vota em todos os blocos).
- **Fundamentação jurídico-constitucional do efeito de protesto no Voto 4 (`RT-30`):** justificar solidamente na Exposição de Motivos da PEC a legitimidade constitucional do efeito redutor de teto via voto em branco deliberado na Tela 1.

---

## 8. Matriz de status das questões iniciais (`Q-01` a `Q-14`)

| ID | Questão original | Status na v0.2 | Encaminhamento / Ref. |
|---|---|---|---|
| `Q-01` | Temas do finalista derrotado no 2º turno | **Resolvida** | Temas de ambos os finalistas ativos (3 a 6 colunas), repartidos proporcionalmente (`D-17` / `RT-02`). |
| `Q-02` | Destino de candidatos inscritos em tema de candidato eliminado no 1º turno | **Em aberto (PLP)** | A disciplinar em Lei Complementar (opções: transferência para legenda/outro tema de missão ou perda de objeto da candidatura vinculada a tema eliminado). |
| `Q-03` | Limiar do veto setorial com base na Assembleia inteira | **Resolvida** | Quórum escalonado sobre a Assembleia com direito a voto (`D-19`): 40% a menos de 75% $\to$ Maioria Absoluta (257); $\ge 75\%$ $\to$ 3/5 (308) (`D-05` / `RT-13`). |
| `Q-04` | Quantidade exata de generalistas sorteados por Assembleia de Projeto | **Em aberto (Regimento Interno)** | Parâmetro e procedimento de sorteio a definir no Regimento Interno da Câmara (número fixo ou fração da coluna especialista). |
| `Q-05` | Cumulação dos Votos 2 e 3 na mesma coluna ou candidato | **Parametrizada / Em aberto (PLP)** | Simulador `RT-19` provou que, mesmo sob proibição e 500 mil votos de "enterro", o ganho marginal é de apenas +1 cadeira; definição final fica para o PLP. |
| `Q-06` | Substituição do STF no pedido de expansão da Assembleia | **Parcialmente resolvida** | STF **retirado em definitivo** (`D-04` / `RT-06`); Executivo e órgãos internos da Câmara são legitimados fixos, restando definir no PLP eventual inclusão da PGR ou da AGU. |
| `Q-07` | Competência para o despacho temático e recurso | **Resolvida** | Atribuída à Tríade Generalista por maioria simples, com critérios objetivos em LC e recurso ao Plenário (`D-18` / `RT-05`). |
| `Q-08` | Detalhes operacionais do STV (interface de urna, esgotamento e piso individual) | **Condicionada / Em aberto (PLP)** | Adotado **STV enxuto** nos Votos 1–3 (`D-12`: 1 número obrigatório + até uma 2ª opção estritamente opcional e rápida, vedando ordenações longas per `RT-21`). Calibrar tempo intermediário em `RT-21` antes do PLP e fechar piso individual/esgotamento de chapas. |
| `Q-09` | Regra de sucessão e suplência temática | **Resolvida** | 1º mesmo partido na célula; 2º mesmo partido na mesma coluna em outra UF da macrorregião IBGE (`D-20` / `RT-11`). |
| `Q-10` | Periodicidade e quórum de revisão do catálogo de missão | **Em aberto (PLP)** | A fixar na Lei Complementar (ex.: revisão a cada legislatura ou ciclo eleitoral, antes da janela partidária). |
| `Q-11` | Interação com Senado e Comissão Mista de Orçamento (Art. 166) | **Resolvida** | Colegiado Orçamentário na CMO; sem veto setorial na LOA; emendas do Senado retornam à Assembleia originária (`D-21` / `RT-28`). |
| `Q-12` | Convivência de Agropecuária e Meio Ambiente na Coluna 8 | **Resolvida (mantida unificada — 6 permanentes)** | Separação em 7 permanentes descartada para integrar deliberação produtiva/ambiental, preservar pisos em 120 e evitar guerra de vetos; pautas climáticas urgentes ficam no Bloco 3 e a análise comparada vai ao Estudo Técnico (`RT-15`). |
| `Q-13` | Nome oficial do sistema | **Resolvida** | **Representação Temática Proporcional (RTP)**. |
| `Q-14` | Total nacional de cadeiras (513 vs. atualização Censo 2022) | **Parametrizada em 513** | Fixada em 513 nas simulações atuais, mantendo parametrizabilidade para eventual recálculo constitucional. |

---

## 9. Dispositivos constitucionais e legais afetados (mapa para o Bloco 2)

| Instrumento / Dispositivo | Conteúdo previsto para redação legislativa |
|---|---|
| **CF/88 — Art. 45** | Instituição da Representação Temática Proporcional (RTP) na Câmara dos Deputados em 3 blocos, garantia das bancadas federativas estaduais (8 a 70 / 513), mandato temático exclusivo, teto estadual de missão de 20% com redução por protesto na Tela 1 e princípio habilitador da participação do eleitorado no exterior/trânsito por legenda temática. |
| **CF/88 — Art. 58** | Substituição da proporcionalidade partidária convencional nas comissões temáticas pela lotação originária por coluna, Assembleias de Projeto com generalistas sorteados, competência de despacho da Tríade Generalista e regra do **Veto Setorial Escalonado** (40% a <75% / $\ge 75\%$). |
| **CF/88 — Art. 77** | Vinculação incondicional da eleição da Câmara dos Deputados à data fixa do 2º turno presidencial (mesmo em caso de definição presidencial no 1º turno) e marco do calendário de campanha defasada. |
| **CF/88 — Art. 166** | Composição da representação da Câmara na CMO pelo **Colegiado Orçamentário** (Coluna 1 + Presidentes das demais colunas ativas) e exclusão expressa do veto setorial sobre a LOA e matérias orçamentárias mistas. |
| **ADCT** | Regras de transição e vigência observando o princípio da anualidade eleitoral (Art. 16 da CF/88). |
| **Lei Complementar (PLP)** | Algoritmo biproporcional de Balinski–Demange e Sainte-Laguë, contingência lexicográfica, catálogo de 10–15 temas de missão (`Q-10`), destino de candidaturas em temas eliminados no 1º turno (`Q-02`), regra de cumulação dos Votos 2 e 3 (`Q-05`), diretrizes do STV enxuto e calibragem prévia (`Q-08`), numeração e fluxo de 2 telas do Voto 4, detalhamento operacional do voto no exterior/trânsito (`D-22`), critérios objetivos de despacho, eventual inclusão de PGR/AGU na expansão (`Q-06`), calendário de +15 dias / HGPE e suplência regional (`Q-09`). |
| **Regimento Interno da Câmara** | Eleição dos Presidentes de Coluna, quóruns, quantitativo exato e procedimento de sorteio dos generalistas (`Q-04`), registro público de agendas (lobby), impedimentos por conflito de interesses e disciplina de faltas. |
