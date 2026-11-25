# RT-01 — Relatório Consolidado do Red Team (SPEC-002)

| Campo | Valor |
|---|---|
| Data | 2026-11-11 |
| Objeto | [SPEC-002-desenho.md](../spec/SPEC-002-desenho.md), [SPEC-002-tecnico.md](../spec/SPEC-002-tecnico.md), [decisoes.md](../decisoes.md) |
| Críticos | Jurista (`J-`), Cientista Político (`P-`), Matemático Eleitoral (`M-`), Urna/Eleitor (`U-`) — Gemini Flash, somente leitura |
| Redatores de Decisões | Subagentes especializados (Gemini 3.8 Flash) integrando respostas do usuário |
| Bruto | 41 críticas → **30 itens consolidados** (`RT-xx`) + 8 descartadas ou rebaixadas |

> **Como ler:** cada item traz as críticas de origem, o **veredito do orquestrador** (se a crítica procede, exagera ou erra), a **recomendação** e a **decisão deliberada pelo usuário**, com as respectivas diretrizes institucionais, políticas e matemáticas.
>
> **Fatos não verificados:** os críticos citaram jurisprudência (MS 32.033, ADI 5.081, ADI 3.685, MS 24.831), resoluções do TSE e números (tempo de cabine em 2022, estados com governador decidido no 1º turno, eleitores no exterior). **Nada disso foi conferido ainda.** Antes de entrar em qualquer documento público, cada fato passa pela fonte primária.

---

## 0. As 6 decisões mais importantes (resumo executivo)

| # | Item | Deliberação do Usuário |
|---|---|---|
| 1 | **RT-02** — Voto 4 no dia do 2º turno | **Aprovada a Opção (b):** Temas prioritários de **ambos os finalistas** (até 6 colunas) ficam ativos na urna. Voto 4 expressa a proporção governismo vs. oposição. Opção (a) registrada como descartada por vício de soberania do sufrágio. |
| 2 | **RT-01** — Arredondamento do teto de missão | **Aprovada a Opção (a):** $u_e = [\![\tau_e \cdot a_e]\!]$ (Sainte-Laguë). Em UFs com 8 cadeiras ($\tau_e = 1$), mantém-se 1 cadeira a partir de 50% de votos válidos; estados grandes mantêm bancadas proporcionais saudáveis. |
| 3 | **RT-03** — Voto preferencial / STV | **Adotado STV enxuto nos Votos 1, 2 e 3:** 1 número obrigatório + até uma 2ª opção estritamente opcional e rápida (vedando ordenações longas conforme `RT-21`), com transferência automática intrapartidária na célula na ausência de 2ª opção; tempo intermediário a validar em `RT-21` antes do PLP. |
| 4 | **RT-13** — Veto setorial | **Aprovado modelo de quórum escalonado:** base = Assembleia de Projeto inteira com direito a voto (sem conflito de interesses, D-19). De 40% a menos de 75% de votos contrários $\to$ superação por **Maioria Absoluta** (257 votos); 75% ou mais de votos contrários $\to$ superação por **3/5** (308 votos), refletindo supremacia do mérito técnico. |
| 5 | **RT-04** — Ordem dos votos na urna | **Aprovada a sequência:** Presidente $\to$ Voto 4 (Missão, em 2 telas) $\to$ Voto 1 $\to$ Voto 2 $\to$ Voto 3. Na **Tela 1** (escolha do tema), branco/nulo é voto de protesto que encolhe $u_e$; na **Tela 2** (dentro do tema), 2 dígitos = legenda partidária e branco/nulo = voto de confiança temática neutro, válido nas Etapas 1–3 e rateado proporcionalmente entre partidos/candidatos da coluna na Etapa 4. |
| 6 | **RT-15** — Coluna 8 (Agro e Meio Ambiente) | **Resolvida — Coluna 8 mantida unificada (6 permanentes).** A hipótese de separação em 7 permanentes foi considerada e descartada para forçar deliberação sustentável integrada (evitando guerra de vetos entre duas comissões), preservar o piso agregado em 120 e deixar eventuais pautas climáticas para o Bloco 3 de Missão (aprofundamento comparado no Estudo Técnico). |

---

## 1. 🔧 Mudança de regra

### RT-01 — Arredondamento duplo zera o teto de missão das UFs pequenas
- **Origem:** M-01 (crítica), J-01 (crítica)
- **Problema:** $u_e = \lfloor \tau_e \cdot a_e \rfloor$ com $\tau_e = 1$ dá **zero sempre que houver um único voto em branco**. Isso atinge 12 UFs: as 11 com 8 cadeiras e Alagoas.
- **Veredito:** **Procede. É erro de formulação meu.** O critério de arredondamento não foi pensado para $\tau_e$ pequeno.
- **Opções:**
  - (a) $u_e = [\![\tau_e \cdot a_e]\!]$ (Sainte-Laguë). Uma UF de 8 cadeiras mantém 1 cadeira se tiver pelo menos 50% de Votos 4 válidos.
  - (b) $u_e = [\![\rho \cdot s_e \cdot a_e]\!]$, sem truncar antes. Uma UF de 8 cadeiras tem 1 cadeira a partir de 31% de válidos e 2 a partir de 94%. O teto nacional pode passar levemente de 91.
  - (c) Calcular primeiro o teto nacional $U = \lfloor \rho \cdot S \rfloor \cdot a_{nac}$ e repartir entre as UFs pelos Votos 4 válidos.
- **Recomendação:** (a). Muda pouco, preserva o teto de 91 e a lógica de "metade válida = mantém a cadeira" é fácil de explicar.
- **Sua decisão:** **Aprovada a Opção (a)** ($u_e = [\![\tau_e \cdot a_e]\!]$ — arredondamento de Sainte-Laguë / inteiro mais próximo). Confirmado o entendimento de que a sensibilidade ao voto em branco afeta pontualmente as bancadas mínimas de 8 cadeiras (onde $\tau_e = 1$, exigindo $\ge 50\%$ de votos válidos para manter a única cadeira de missão), ao passo que estados com maior representação continuam elegendo bancadas proporcionais saudáveis (por exemplo, em uma UF com bancada ampla em que o teto seja de 10 cadeiras de missão, alcançando 80% de válidos obtêm-se $10 \times 0{,}80 = 8$ cadeiras). Preserva-se o teto nacional rígido de 91 cadeiras e a regra simples de comunicação pública ("metade válida = mantém a cadeira").

### RT-02 — Voto 4 no dia do 2º turno: temas do finalista derrotado e logística
- **Origem:** U-02 (crítica), U-01 (crítica), J-05 (alta), J-04 (alta), P-06 (parcial)
- **Problema:** no 2º turno, a urna mostra os temas dos 2 finalistas. Quem votar num tema só do derrotado tem o voto **descartado** (voto que depende do resultado de outra eleição) ou **transferido** para outro tema (fere a vontade do eleitor). Os candidatos registrados nesses temas perdem a candidatura por um fato externo a eles, o que o Jurista trata como problema de elegibilidade (J-05).
- **Veredito:** **Procede no núcleo.** A logística (U-01) está **exagerada**: as listas de candidatos já existem desde o registro em agosto. A urna só precisa *ativar* temas, e o número de combinações possíveis de finalistas é pequeno, então o TSE pode deixar as configurações pré-geradas. É difícil, mas não impossível.
- **Opções:**
  - (a) **Aceitar a perda.** Os votos em temas do derrotado não elegem ninguém e contam como não válidos no encolhimento (D-15). Na prática, o voto 4 da oposição vira protesto automático. O risco jurídico de J-05 continua.
  - (b) **Os temas dos 2 finalistas ficam ativos (até 6).** A bancada de missão passa a refletir as agendas dos dois finalistas, na proporção dos votos. Nenhum voto se perde entre os finalistas e o poder presidencial fica ainda mais diluído. A Q-02 continua valendo só para os temas de candidatos eliminados no 1º turno.
  - (c) **Adotar a alternativa D-03:** o legislativo vota depois de conhecido o Presidente eleito. Elimina o problema, mas cria outro calendário.
- **Recomendação:** (b). Resolve a maior parte do problema sem mudar o calendário e é coerente com o seu objetivo de limitar o poder do Presidente. O custo conceitual: a bancada deixa de ser só a do Presidente.
- **Sua decisão:** **Aprovada a Opção (b):** Ficam ativos na urna os temas prioritários de ambos os finalistas presidenciais (até 6 colunas ativas no total, sendo 3 de cada candidatura). A bancada de missão resultante refletirá a proporção dos votos obtidos por cada agenda, assegurando representação tanto para a base governista quanto para a oposição qualificada e diluindo a concentração monocrática do poder presidencial.
  - *Critério de desempate:* Na alocação intracelular, em caso de empate, prevalece o candidato com maior votação nominal individual de 1ª preferência (e, persistindo o empate, o critério legal de idade do Código Eleitoral).
  - *Registro da Opção (a) como descartada:* A alternativa (a) (descarte sumário dos votos nos temas do candidato derrotado) fica expressamente registrada como descartada por violar a soberania do sufrágio (descarte de votos válidos por fato externo), transformar o voto da oposição em perda automática e gerar grave insegurança jurídica sobre a elegibilidade dos candidatos dessas listas (conforme alertado pelo Jurista em J-05).

### RT-03 — "STV" sem ranqueamento não é STV
- **Origem:** M-04 (alta), U-06 (alta), P-08 (alta)
- **Problema:** a cédula tem 1 voto nominal por bloco, mas a Etapa 4 usa cota de Droop e Gregory, que pressupõem preferências ordenadas. A urna de 12 teclas também torna o ranqueamento impraticável (U-06). E em células de 1 cadeira o resultado é majoritário de qualquer jeito.
- **Veredito:** **Procede.** O que a SPEC descreve ("transferência para o mesmo partido") é, na prática, **lista aberta intrapartidária por célula**.
- **Proposta:** renomear e formalizar. Dentro de cada célula (Estado × Coluna), as cadeiras vão aos partidos por Sainte-Laguë sobre os votos somados de seus candidatos. Dentro de cada partido, assumem os mais votados. **Nenhuma ordem é definida pela direção partidária** (como pede P-08).
- **Recomendação:** aceitar. Com isso a urna continua com 1 número por tela e o ranqueamento opcional sai.
- **Sua decisão:** **Adotado STV enxuto nos Votos 1, 2 e 3** (evolução da diretriz inicial do usuário ajustada pela evidência de filas em `RT-21`): o eleitor digita **1 número obrigatório** e conta com até **uma 2ª opção estritamente opcional e rápida**, vedando ordenações longas de 3 ou mais preferências que levariam ao colapso de filas às 17h.
  - *Pontos consolidados e pendências para o PLP (`Q-08`):*
    1. *Interface e tempo de cabine:* Validar o tempo intermediário da 2ª opção estritamente opcional no modelo de filas (`RT-21`) antes da redação do PLP, assegurando viabilidade ergonômica no teclado de 12 teclas da urna;
    2. *Mecanismo de transferência:* Na presença de 2ª opção declarada, transferem-se excedentes e votos de eliminados proporcionalmente conforme a preferência declarada; na ausência de 2ª opção, a transferência opera automaticamente em cascata para correligionários do **mesmo partido na mesma célula** (`D-12`). A modelagem detalhada de cotas, piso individual e exaustão de chapas fica para o PLP (`Q-08`).

### RT-04 — Ordem dos votos na urna: missão logo após o Presidente *(sugestão do orquestrador)*
- **Origem:** U-05 (alta), J-10 (média), P-03 (parcial)
- **Problema:** o branco no último voto mede **cansaço** (mais comum entre idosos e pessoas de baixa escolaridade), e não protesto. Como o encolhimento (D-15) depende desse branco, as UFs mais pobres perdem cadeiras de missão por fadiga.
- **Proposta:** ordem na urna **Presidente → Voto 4 (Missão) → Votos 1, 2, 3**. O voto de missão fica ao lado do voto presidencial, que é o mais lembrado, e o branco nele passa a ser deliberado. O cansaço migra para os Votos 2 e 3, onde os pisos de 20 protegem as colunas.
- **Recomendação:** aceitar. Mantém o D-15 e desarma a crítica mais forte contra ele.
- **Sua decisão:** **Aprovada a nova ordem de votação na urna eletrônica:** Sequência definida como **Presidente → Voto 4 (Missão, em 2 telas) → Voto 1 → Voto 2 → Voto 3**.
  - *Contextualização política:* Ao votar para Presidente da República, o eleitor é imediatamente contextualizado no debate das plataformas governamentais e vota em seguida na bancada de missão (Voto 4), assegurando deliberatividade ao sufrágio.
  - *Fluxo em 2 telas e efeito do voto em branco:* Na **Tela 1** (escolha do tema de missão), o voto em branco ou nulo opera conscientemente como **voto de protesto** e encolhe o teto $u_e$ (entrando no denominador de $a_e$ como não válido). Na **Tela 2** (dentro do tema escolhido na Tela 1), se o eleitor digitar os **2 dígitos de um partido**, configura voto de **legenda partidária** dentro do tema (`votos_confianca_partido`); se votar em **branco ou nulo** (sem candidato nem legenda), opera como **voto de confiança temática neutro** (`votos_confianca_coluna`): conta 100% para o tamanho da coluna nas Etapas 1–3 (não encolhe $u_e$) e, na Etapa 4, é rateado proporcionalmente entre os partidos e candidatos daquela coluna de missão. Os Votos 1, 2 e 3 permanecem salvaguardados, respectivamente, pelas 60 cadeiras fixas do Bloco 1 e pelos pisos constitucionais de 20 cadeiras do Bloco 2.

### RT-05 — Despacho temático vira o maior poder da Casa
- **Origem:** P-04 (alta) · **Q-07**
- **Problema:** com o veto setorial, decidir para qual coluna vai um projeto decide se ele vive. O Presidente da Câmara ganha um poder de barganha ainda maior que o atual.
- **Proposta:** critérios objetivos de classificação definidos em Lei Complementar, despacho pela Tríade Generalista (e não pelo Presidente da Câmara) e recurso ao Plenário por maioria simples.
- **Sua decisão:** **Aprovado:** A competência originária de despacho e distribuição temática dos projetos de lei às colunas setoriais passa a ser atribuída à **Tríade Generalista** desde o início de sua tramitação (afastando a concentração monocrática no Presidente da Câmara).
  - *Rito decisório:* Decisão colegiada tomada por maioria simples dos membros da Tríade Generalista para acolhimento e distribuição, assegurado recurso ao Plenário da Câmara dos Deputados por maioria simples.
  - *Critérios objetivos:* Inclusão de critérios objetivos, exaustivos e parâmetros técnicos de enquadramento temático como recomendação normativa expressa no corpo da futura Lei Complementar de organização do Legislativo.

### RT-06 — STF fora do pedido de expansão
- **Origem:** J-03 (alta) · **Q-06**
- **Problema:** se o STF ajuda a moldar um projeto, depois fica em posição suspeita para julgá-lo numa ação de inconstitucionalidade. Eu já tinha apontado isso.
- **Proposta:** trocar o STF pela PGR ou pela AGU, ou deixar o pedido só com órgãos internos (por exemplo, 1/3 de outra coluna).
- **Sua decisão:** **Aprovada a retirada definitiva do STF** de qualquer iniciativa ou prerrogativa de provocação temática e pedido de expansão de quórum, eliminando o risco de suspeição jurisdicional e preservando a imparcialidade do tribunal constitucional perante posterior controle concentrado ou difuso de constitucionalidade (conforme J-03 e Q-06).
  - *Legitimados fixos e ponto delegado ao PLP:* O **Poder Executivo** e **órgãos regimentais internos da Câmara** (ex.: requerimento subscrito por fração qualificada de outra coluna) permanecem como legitimados fixos para requerer expansão à Tríade Generalista; eventual extensão dessa provocação à Procuradoria-Geral da República (PGR) ou à Advocacia-Geral da União (AGU) fica delegada à definição na Lei Complementar (`Q-06`).

### RT-07 — Numeração de candidatos com prefixo da coluna
- **Origem:** U-09 (média)
- **Problema:** 4 votos seguidos para deputado federal, todos com números de 4 dígitos. Digitar o número de uma coluna na tela de outra gera voto nulo.
- **Proposta:** o primeiro dígito identifica o bloco ou a coluna, e a urna avisa antes de confirmar um número inexistente. É matéria de lei, não de PEC.
- **Sua decisão:** **Aprovado:** A numeração eleitoral dos candidatos conterá prefixo padronizado identificador do bloco e da coluna temática correspondente. A urna eletrônica conterá mecanismo de validação e alerta em tela caso o eleitor digite dígito correspondente a outra coluna antes de computar voto nulo involuntário. Matéria técnica a ser disciplinada em sede de Lei Complementar e resoluções normativas do TSE, sem sobrecarregar a PEC.

### RT-08 — Propaganda gratuita (HGPE) para o legislativo
- **Origem:** U-10 (média)
- **Problema:** o 2º turno tem cerca de 3 semanas e o horário gratuito é dominado pelos finalistas.
- **Proposta:** a propaganda legislativa corre durante o período do 1º turno. Entre os turnos, ficam só inserções curtas e debates temáticos.
- **Sua decisão:** **Aprovado o modelo de campanha defasada/deslocada:** A campanha para Deputado Federal começa 15 dias após o início geral das campanhas (por volta de 1º de setembro) e segue ininterrupta até a data do 2º turno (fim de outubro).
  - *Vantagens consolidadas:* (1) Mantém rigorosamente a mesma duração de campanha (~55 a 60 dias), o mesmo teto legal de gastos de campanha e regras de financiamento (Fundo Eleitoral); (2) Libera o horário eleitoral (HGPE) no rádio e TV em outubro para foco exclusivo na Presidência (quando houver 2º turno) e nas Colunas Temáticas ativas da Câmara (12 no cenário-base; até 15 com 6 missões), sem concorrência com deputados estaduais e senadores (já eleitos no 1º turno). Registrado em D-23.

### RT-09 — Regra de contingência para quando a matriz biproporcional não tem solução
- **Origem:** M-03 (alta → **rebaixado para média**)
- **Problema:** em tese, pode não existir matriz inteira viável (por exemplo, uma coluna com voto zero em muitas UFs). A SPEC não diz o que fazer nesse caso.
- **Veredito:** é improvável com dados reais, porque o Voto 1 é obrigatório e as colunas grandes têm voto em todo lugar. Mas a lei precisa prever o caso.
- **Proposta:** regra de reserva por programação inteira, minimizando o desvio da proporcionalidade com prioridades em ordem fixa, mais uma métrica de frequência no simulador.
- **Sua decisão:** **Aprovada em princípio** a regra de contingência matemática baseada em programação inteira com relaxamento lexicográfico, assegurando alocação inteira ótima e minimização hierárquica dos desvios da proporcionalidade teórica mesmo em cenários extremos de dispersão de votos.
  - *Encaminhamento pedagógico:* Registrado o pedido do usuário para inclusão de uma explicação didática dos fundamentos de otimização inteira e do algoritmo biproporcional no futuro "aulão" técnico do projeto.

### RT-10 — Momento do sorteio dos generalistas
- **Origem:** P-07 (média)
- **Problema:** depois do sorteio, o lobby recebe uma lista exata de alvos.
- **Proposta:** sortear o mais perto possível da votação, registrar publicamente as reuniões dos sorteados com agentes privados e exigir quórum mínimo de presença deles.
- **Sua decisão:** **Aprovado com inclusão de regra de impedimento por conflito de interesse:**
  - *Momento e transparência:* O sorteio dos deputados generalistas ocorrerá na data mais próxima possível da deliberação setorial, com exigência de transparência ativa e publicação obrigatória dos registros de agenda/encontros com agentes setoriais privados;
  - *Regra de conflito de interesses (adicionada pelo usuário):* Deputados generalistas com conflito de interesses manifesto ou vínculos profissionais/econômicos diretos com a matéria pautada (por exemplo, deputados economistas com interesses no setor regulado) serão formalmente impedidos de participar do sorteio de votos deliberativos, resguardando-se apenas sua participação opinativa com voto em caráter simbólico.

### RT-11 — Suplência
- **Origem:** J-08 (média) · **Q-09**
- **Problema:** exigir que o suplente seja ao mesmo tempo da mesma célula e do mesmo partido muitas vezes não deixa ninguém disponível.
- **Proposta:** ordem de preferência: (1) mesmo partido, mesma célula; (2) mesmo partido, mesma coluna, outra UF da região; (3) mesmo partido, mesma UF, outra coluna. A vaga fica sempre com o partido, como prevê a ADI 5.081 (não verificado).
- **Sua decisão:** **Aprovada a Opção 2 para a ordem de sucessão da suplência:**
  1. *1ª prioridade:* Suplente do **mesmo partido na mesma célula** (Estado × Coluna);
  2. *2ª prioridade (caso esgotada a célula):* Suplente do **mesmo partido na mesma coluna temática em outra UF da mesma macrorregião geográfica**.
  - A regra concilia a titularidade partidária do mandato conferido pelo sistema proporcional (em linha com o entendimento atribuído à ADI 5.081, **a verificar na fonte primária** no Bloco 2) com a preservação imperativa da identidade técnica e funcional da bancada setorial temática.

### RT-12 — Correção do texto da Etapa 2a *(técnica, não precisa de decisão)*
- **Origem:** M-05
- **Veredito:** **a conclusão está certa, a justificativa estava errada.** Eu escrevi que $H_3^{prop}$ "só cresce" com a abstenção, o que não vale se a abstenção cair no Voto 4. Mas $H_3 = U$ continua valendo **sempre**. Sendo $a$ a taxa de Votos 4 válidos e $b$ a taxa média de válidos nos Votos 2 e 3:

$$91a < \frac{333\,a}{2b + a} \iff 2b + a < 3{,}66$$

  Como $2b + a \le 3$, a desigualdade vale para quaisquer taxas de abstenção. A normalização sugerida por M-05 é desnecessária. **Vou corrigir o texto da SPEC.**
- **Sua decisão:** **Aprovada a correção matemática** no documento SPEC-002-tecnico. A validade universal da relação decorre diretamente da demonstração analítica ($2b + a \le 3$), dispensando normalizações artificiais.
  - *Demanda pedagógica:* Registrado o compromisso de reservar um momento de "aulão" pedagógico dedicado a explicar detalhadamente todos os passos e demonstrações matemáticas de SPEC-002-tecnico.

---

## 2. ⚖️ Trade-off assumido (decisão já tomada e criticada: documentar ou reabrir)

### RT-13 — Veto setorial com derrubada por 3/5
- **Origem:** P-01 (crítica), J-02 (crítica)
- **Crítica:** com 3/5, é mais difícil derrubar o veto de uma comissão do que um veto presidencial (maioria absoluta) e tão difícil quanto aprovar uma PEC. Abre espaço para captura por grupos organizados.
- **Veredito:** o argumento político é forte. O jurídico ("inconstitucional") é **fraco**: uma PEC pode criar quóruns. A defesa já existe: a base do veto é a **Assembleia inteira, com generalistas sorteados**, e não só a coluna (D-05).
- **Alternativa intermediária:** **quórum escalonado.** Se de 40% a 59% da Assembleia votar contra, a derrubada exige maioria absoluta (257). Se 60% ou mais votar contra, exige 3/5 (308). O veto continua com força, e a força cresce com o consenso técnico.
- **Sua decisão:** **Aprovado o modelo de quórum escalonado com ajuste nos percentuais:**
  - **De 40% a menos de 75% de votos contrários na Assembleia de Projeto:** A rejeição do veto no Plenário da Câmara dos Deputados exige **Maioria Absoluta** (257 votos).
  - **75% ou mais de votos contrários na Assembleia de Projeto:** A rejeição do veto no Plenário exige quórum qualificado de **3/5** (308 votos).
  - *Fundamentação:* Atingir o patamar qualificado de 75% em um colegiado misto — composto pelos parlamentares eleitos da coluna temática correspondente e pelos deputados generalistas sorteados com direito a voto (excluídos os impedidos por conflito de interesses, conforme `D-19`) — demonstra de forma inequívoca que a rejeição decorreu do mérito técnico e setorial prevalecendo sobre polarizações político-partidárias conjunturais. Essa densidade técnica legitima perfeitamente o quórum de 3/5 no Plenário, blindando o dispositivo contra contestações de autoritarismo corporativo, enquanto a faixa de 40% a menos de 75% assegura à maioria absoluta do Plenário a prerrogativa de revisão democrática ordinária.

### RT-14 — Campanha organizada pelo voto em branco no Voto 4
- **Origem:** M-02 (crítica), P-03 (alta)
- **Crítica:** a oposição ou as elites regionais podem fazer campanha pelo branco para encolher a bancada de missão. As cadeiras liberadas voltam para as colunas permanentes **do mesmo Estado**.
- **Veredito:** **esse é exatamente o mecanismo de protesto que você desenhou** (D-08, D-15). Não é falha, é a função. Só falta assumir isso por escrito. Com o RT-04 aprovado, o branco passa a ser deliberado.
- **Recomendação:** documentar como trade-off: "o protesto organizado é legítimo e intencional".
- **Sua decisão:** **Aprovado e assumido integralmente como trade-off deliberado.**
  - *Fundamentação:* A eventual orquestração de campanhas de oposição ou de elites regionais pregando o voto em branco **na Tela 1** do Voto 4 (adesão ou protesto contra o bloco de missões) não representa falha de desenho, mas a própria essência do mecanismo de freios e contrapesos federativos. Esse risco gera um incentivo eleitoral direto e virtuoso para que o Presidente da República faça campanha ativa, interiorize seu debate programático e construa alianças substantivas em estados historicamente periféricos ou marginalizados (a exemplo da Região Norte), demonstrando utilidade e relevância concreta de suas missões para essas populações. Caso o chefe do Executivo negligencie essas federações, os eleitores e forças locais exercerão seu contraponto legítimo, devolvendo as cadeiras liberadas para as colunas temáticas permanentes do próprio Estado.

### RT-15 — Perda de proporcionalidade partidária e a contradição da coluna 8
- **Origem:** M-08 (alta), J-06 (alta)
- **Crítica:** a magnitude média é de 513 / 324 ≈ 1,6 cadeira por célula, o que dá um limiar efetivo de 25% a 37%. Partidos de nicho não sobrevivem só por se especializarem: precisam ser **dominantes** na célula.
- **Veredito:** **procede em parte.** A especialização ajuda (um partido concentra seus votos numa coluna), mas o exemplo do Partido Verde **não funciona com Agropecuária e Meio Ambiente na mesma coluna**: o PV disputaria contra o agronegócio. Isso reabre a **Q-12**.
- **Opções:** (a) manter D-07 como está; (b) separar Meio Ambiente da Agropecuária (passam a ser 7 permanentes); (c) criar um nível nacional de compensação partidária.
- **Sua decisão:** **Resolvida — Coluna 8 mantida unificada (6 colunas permanentes).**
  - *Fundamentação da rejeição à separação:* A possibilidade de desmembramento em 7 colunas permanentes (separando Meio Ambiente da Agropecuária) foi explicitamente avaliada e descartada por três motivos: (1) **deliberação sustentável integrada**, evitando que duas comissões permanentes antagônicas bloqueiem mutuamente projetos por guerra de vetos setoriais (`D-05`) em vez de negociar conciliação dentro do mesmo colegiado; (2) **preservação da arquitetura de 6 permanentes**, evitando elevar o piso rígido do Bloco 2 de 120 para 140 assentos e comprimir ainda mais as magnitudes por célula; e (3) **flexibilidade temática**, já que pautas climáticas ou ambientais urgentes podem ser ativadas temporariamente no Bloco 3 de Missão. O aprofundamento comparado de sistemas funcionais e de limiares partidários fica registrado para o Estudo Técnico.

### RT-16 — "Puxador temático" espalha efeito para outras UFs
- **Origem:** M-07 (média)
- **Crítica:** uma celebridade com 2,5 milhões de votos em Segurança, em SP, aumenta o tamanho nacional dessa coluna. Pelo cálculo biproporcional, Segurança ganha cadeiras também no Piauí e em Rondônia.
- **Veredito:** procede. Eu já tinha apontado isso na primeira análise. A atenuação por função côncava (raiz dos votos) é elegante, mas difícil de explicar.
- **Recomendação:** documentar como trade-off e medir no simulador (RT-20).
- **Sua decisão:** **Manter a regra e assumir o trade-off.** O transbordamento interestadual de cadeiras decorrente de puxadores temáticos será documentado e mensurado no simulador (RT-20).
  - *Fundamentação:* Sob a dinâmica do **STV enxuto** (1 número obrigatório + até uma **2ª opção estritamente opcional** nos Votos 1, 2 e 3, com fallback automático intrapartidário na célula), a presença de puxadores de alta densidade eleitoral gera um incentivo estratégico cooperativo para postulantes menores e legendas emergentes. Cria-se o estímulo pragmático para campanhas focadas na segunda preferência ("caso o candidato consagrado da sua escolha já esteja eleito, considere me indicar na 2ª opção") e, quando não declarada a 2ª opção, o excedente fortalece os demais nomes do mesmo partido na célula. Uma vez que o puxador esgota sua cota eleitoral, o excedente redistribui-se proporcionalmente, atenuando a concentração oligopolista e oxigenando o parlamento.

### RT-17 — Comparecimento quando o Presidente vence no 1º turno
- **Origem:** U-03 (alta), P-06 (alta), J-04 (parcial)
- **Crítica:** sem disputa presidencial, a eleição só para a Câmara no fim de outubro pode ter abstenção muito alta, e desigual entre UFs (onde há 2º turno para governador, o comparecimento é maior).
- **Veredito:** procede como risco. Você considerou isso "até melhor" (D-14). O efeito novo é o próximo item.
- **Efeito derivado (orquestrador):** o comparecimento desigual **não muda o total de cadeiras de cada UF** (que é fixo), mas **muda o tamanho nacional das colunas**, porque as UFs com mais comparecimento pesam mais em $V_c$. Ver RT-22.
- **Sua decisão:** **Manter D-14 (eleição legislativa mantida incondicionalmente na data fixa do 2º turno, mesmo com o Presidente eleito no 1º turno).**
  - *Fundamentação:* A autonomia temporal do pleito legislativo assegura a centralidade do debate parlamentar e programático, evitando que o Congresso Nacional seja ofuscado ou tratado como mero subproduto da disputa majoritária presidencial. Realizar o segundo turno focado estritamente na composição da Câmara dos Deputados mantém o engajamento democrático e o debate público aquecidos em torno das colunas temáticas, das prioridades orçamentárias e dos programas legislativos, descolados da pura polarização executiva. O impacto do comparecimento diferencial sobre o peso nacional das colunas segue endereçado para teste empírico no simulador (RT-22).

### RT-18 — A bancada de missão gera ressentimento na base aliada
- **Origem:** P-10 (média)
- **Crítica:** os 91 deputados de missão viram uma "nobreza palaciana" e o resto da base cobra mais caro.
- **Veredito:** é especulativo, mas plausível. Com RT-02(b), a bancada de missão deixa de ser exclusiva do governo, e o argumento perde força.
- **Sua decisão:** **Risco descartado / desconsiderado como impeditivo relevante.**
  - *Fundamentação:* Não se configura privilégio injustificado que motive ressentimento estrutural da base aliada permanente. Os deputados eleitos para as colunas de missão assumem um risco eleitoral substancialmente mais gravoso: concorrem em mandatos temporários, sem garantia de piso mínimo de representação (piso zero) e diretamente submetidos à validação popular na **Tela 1** do Voto 4 (com o risco de encolhimento da bancada diante de votos brancos ou nulos de protesto **na Tela 1**). Em contrapartida, os parlamentares das colunas permanentes disputam cadeiras consolidadas e institucionalmente resguardadas por pisos mínimos constitucionais (piso de 20 cadeiras). Essa disparidade de risco justifica plenamente a proximidade política da missão e, com o modelo de ativação plural de temas introduzido por RT-02(b), dissolve-se a tese de uma "guarda pretoriana" ou nobreza palaciana exclusiva.

---

## 3. 🧪 Hipóteses para o simulador

| ID | Hipótese a testar | Origem | Decisão / Diretriz do Usuário |
|---|---|---|---|
| RT-19 | **Voto estratégico de "enterro":** votar numa coluna travada no piso para impedir que uma coluna concorrente cresça. Rodar com as duas regras da Q-05. | M-06 | **Aprovado.** Implementar e testar no simulador Python sob os dois cenários de regra da Q-05. |
| RT-20 | **Métricas novas:** taxa de inviabilidade da matriz; sobrevivência de partidos por faixa de votos (1–3%, 3–6%, 6–10%); efeito de transbordamento temático entre UFs; frequência de paradoxos de monotonia entre blocos. | M-10, M-07 | **Aprovado.** Implementar o pacote completo de métricas avançadas (M-10) e sobrevivência partidária na suíte do simulador. |
| RT-21 | **Tempo de cabine e filas** (modelo de filas). *Rebaixado:* o novo 2º turno teria cerca de 5–6 votos, o mesmo que o 1º turno atual, e o 1º turno perde o voto de deputado federal. | U-04 | **Aprovado.** Implementar e testar modelagem de tempo de cabine e dinâmica de filas no simulador. |
| RT-22 | **Comparecimento desigual entre UFs** distorce o tamanho nacional das colunas. | derivado de U-03 | **Aprovado.** Simular cenários de comparecimento heterogêneo entre UFs e mensurar a sensibilidade de $V_c$. |
| RT-23 | **Atraso na totalização nacional:** sensibilidade do resultado a urnas que chegam tarde. | U-08 | **Aprovado.** Implementar teste de estresse de sensibilidade do cálculo biproporcional ao atraso de apuração/totalização por UF. |

---

## 4. ⚠️ Riscos e limitações abertas (admitir no Estudo Técnico)

| ID | Risco | Origem | Nota do orquestrador | Decisão / Diretriz do Usuário |
|---|---|---|---|---|
| RT-24 | **Viabilidade política:** os atuais deputados precisam votar contra o próprio modelo de carreira. | P-02 | É o risco nº 1 de qualquer reforma. Exige uma estratégia de transição (assunto para depois). | **Risco assumido.** O objetivo deliberado do projeto é enriquecer o debate nacional e elevar a qualidade da discussão política e institucional sobre o modelo representativo. |
| RT-25 | **Apuração opaca:** o cálculo biproporcional é difícil de explicar e abre espaço para narrativas de fraude. | U-07 | Mitigação: simulador oficial em código aberto e ferramenta pública de auditoria com os multiplicadores. | **Mitigação mantida + Ação legislativa.** Manter mitigação de transparência (código aberto e auditoria). Adicionar recomendação em legislação conexa de programas obrigatórios de educação cívica e letramento eleitoral sobre o sistema de votação em escolas e empresas. |
| RT-26 | **Clientelismo e emendas:** deputados escolhem a coluna mais fácil e usam a comissão para capturar o orçamento do setor. | P-05 | Não dá para simular. Admitir o risco e propor regras sobre emendas de comissão. | **Risco reconhecido + Ação futura.** Reconhecido como desafio intrínseco da democracia brasileira. Decisão: elaborar posteriormente PEC autônoma ou legislação auxiliar regulamentando e restringindo o uso de emendas parlamentares individuais e de comissão. |
| RT-27 | **Precedentes de representação funcional** (Seanad, Hong Kong, Eslovênia). | P-09 | Já estava na análise inicial. Diferenciar pela universalidade do voto. | **Documentar no Working Paper.** Anotado para inclusão detalhada na justificativa/explicação do Working Paper, demonstrando a diferenciação estrutural em relação a sistemas corporativistas fechados pela universalidade do sufrágio (todo eleitor vota em todas as áreas). |
| RT-28 | **Senado e Comissão Mista de Orçamento (Art. 166).** | J-09 | É a Q-11. Ressalvar que o veto setorial não se aplica a matérias de comissão mista. | **Aprovado o modelo de governança orçamentária:** Cada coluna temática ativa elege seu próprio Presidente. A bancada da Câmara na CMO é o **Colegiado Orçamentário (60 da Coluna 1 + os Presidentes de todas as demais colunas com representação na legislatura — 11 no cenário-base de 3 missões; até 14 no cenário de até 6 missões ativas conforme D-17)**, confrontando capacidade fiscal com necessidades setoriais. Veto setorial não se aplica à LOA/Orçamento para evitar paralisação do Estado; emendas do Senado a projetos de lei ordinários e complementares originários da Câmara voltam à Assembleia da Coluna originária. Registrado em D-21. |
| RT-29 | **Eleitores no exterior e em trânsito.** | U-11 | Regra simples: votam só para Presidente, como hoje. | **Rejeitada a restrição; aprovado modelo alternativo (`D-22`).** Eleitores na Zona ZZ (exterior) e em trânsito interestadual votam na **legenda temática pura** (escolhem a coluna temática sem indicação nominal estadual), somando em $V_c$ sem alterar as cotas federativas rígidas dos Estados ($s_e$). Parecer jurídico confirmou 100% de constitucionalidade. |
| RT-30 | **Efeito jurídico do voto em branco.** | J-01 (parte jurídica) | Uma PEC pode atribuir esse efeito. É risco de questionamento, não impedimento. A justificativa tem de ser forte. | **Fundamentação jurídica futura.** Anotar como ponto a ser revisado e fundamentado juridicamente nas próximas etapas (sustentação constitucional do efeito de protesto e encolhimento do voto em branco via PEC). |

---

## 5. 🗑️ Descartadas ou rebaixadas (com motivo)

| Crítica | Motivo |
|---|---|
| **M-09** — UFs pequenas sem nenhum generalista | **Erro do crítico.** O Voto 1 é obrigatório no Bloco 1, então toda UF tem cerca de 1/4 dos votos nas colunas generalistas. O cálculo biproporcional dá a cada UF cerca de 35% das suas cadeiras no Bloco 1: aproximadamente 3 numa UF de 8 cadeiras. Um piso de 1 por UF pode entrar como salvaguarda barata. |
| **M-05** — normalizar o denominador | Desnecessário (ver RT-12). |
| **J-07** — sorteio inconstitucional | Argumento fraco. A composição das comissões é matéria do Regimento. A restrição real é o Art. 58, §1º, que a PEC já vai alterar. |
| **J-02** (parte jurídica) — "jurisprudência firme" contra quórum qualificado | Não verificado e duvidoso. Uma PEC pode criar quóruns. O argumento que vale é o político (RT-13). |
| **J-04** — "subordinação do Legislativo ao Executivo" | Exagerado. O Senado continua no 1º turno. Absorvido em RT-02 e RT-17. |
| **U-01** — "colapso logístico" | Exagerado. As listas de candidatos já existem desde agosto. Absorvido em RT-02. |
| **U-04** — "colapso das filas" | Exagerado (ver RT-21). |
| **P-02 (subponto federativo descartado)** — "4 colunas com zero cadeiras em UF pequena" | Já aceito explicitamente (D-06). |

---

## Anexo — Relatórios brutos
- [Jurista Constitucionalista](conversation://7fac3a75-2c1d-45e7-ac9b-7372f2985197)
- [Cientista Político](conversation://29f7b9b2-1939-4997-a220-17157da8263f)
- [Matemático Eleitoral](conversation://fb197ebc-7bae-40be-ad56-184c7b5cb99f)
- [Urna e Eleitor](conversation://295aa13c-4f70-4a41-b9f2-9cb640b96413)
