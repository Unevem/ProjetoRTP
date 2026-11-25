# Base Normativa e Calibração — Etapa 2.1 (Pré-Redação da PEC e do PLP)

> **Finalidade:** Consolidar, antes da redação do articulado da PEC (`pec/PEC_RTP.md`) e do Projeto de Lei Complementar (`pec/PLP_RTP.md`), (1) o texto vigente conferido dos dispositivos constitucionais afetados e da jurisprudência do STF; (2) a calibração empírica do **STV enxuto** no modelo de filas `RT-21`; e (3) a **Matriz Definitiva de Competência Normativa** (fronteira estrita entre CF/88, ADCT, Lei Complementar e Regimento Interno da Câmara).
> **Conformidade:** LC nº 95/1998, Decreto nº 9.191/2017 e skill `legistica-brasil`.

---

## 1. Conferência dos Textos Vigentes da CF/88 e Jurisprudência

### 1.1 Art. 45 da CF/88 (Composição da Câmara dos Deputados)
*Fontes conferidas: repositório `ctresb/leis` (`constituicao.md`) e Portal do Planalto.*

> **Art. 45.** A Câmara dos Deputados compõe-se de representantes do povo, eleitos, pelo sistema proporcional, em cada Estado, em cada Território e no Distrito Federal.
>
> **§ 1º** O número total de Deputados, bem como a representação por Estado e pelo Distrito Federal, será estabelecido por lei complementar, proporcionalmente à população, procedendo-se aos ajustes necessários, no ano anterior às eleições, para que nenhuma daquelas unidades da Federação tenha menos de oito ou mais de setenta Deputados.
>
> **§ 2º** Cada Território elegerá quatro Deputados.

**Impacto na PEC:**
- **Altera o *caput*** para substituir "pelo sistema proporcional" por "pelo sistema de representação temática proporcional".
- **Mantém intactos os §§ 1º e 2º** (representados por linha de pontos `........` na PEC), blindando o pacto federativo de 8 a 70 deputados por UF contra qualquer arguição de violação à cláusula pétrea (Art. 60, § 4º, I).
- **Acrescenta novos parágrafos (§§ 3º a 7º)** fixando: (i) os 3 blocos de colunas temáticas (Estado fixo em 180, Permanentes com piso protetor e Missão sem piso com ativação plural dos finalistas presidenciais); (ii) o mandato temático exclusivo; (iii) o teto estadual de 20% das cadeiras para o Bloco de Missão com encolhimento proporcional por voto em branco ou nulo de protesto na escolha temática; (iv) a titularidade partidário-temática do mandato e suplência regionalizada na mesma coluna; e (v) a cláusula habilitadora da participação de eleitores no exterior (Zona ZZ) e em trânsito interestadual por voto de legenda temática na totalização nacional das colunas, sem alteração das cotas estaduais do § 1º.

---

### 1.2 Art. 58 da CF/88 (Comissões e Processo Legislativo Interno)
*Fontes conferidas: repositório `ctresb/leis` e Portal do Planalto.*

> **Art. 58.** O Congresso Nacional e suas Casas terão comissões permanentes e temporárias, constituídas na forma e com as atribuições previstas no respectivo regimento ou no ato de que resultar sua criação.
>
> **§ 1º** Na constituição das Mesas e de cada Comissão, é assegurada, tanto quanto possível, a representação proporcional dos partidos ou dos blocos parlamentares que participam da respectiva Casa.
>
> **§ 2º** Às comissões, em razão da matéria de sua competência, cabe: I - discutir e votar projeto de lei que dispensar, na forma do regimento, a competência do Plenário, salvo se houver recurso de um décimo dos membros da Casa; II - realizar audiências públicas com entidades da sociedade civil; III - convocar Ministros de Estado para prestar informações sobre assuntos inerentes a suas atribuições; IV - receber petições, reclamações, representações ou queixas de qualquer pessoa contra atos ou omissões das autoridades ou entidades públicas; V - solicitar depoimento de qualquer autoridade ou cidadão; VI - apreciar programas de obras, planos nacionais, regionais e setoriais de desenvolvimento e sobre eles emitir parecer.
>
> **§ 3º** *(CPIs — mantido intacto)*
> **§ 4º** *(Comissão representativa no recesso — mantido intacto)*

**Impacto na PEC:**
- **Altera o § 1º** para ressalvar expressamente a lotação originária e exclusiva nas colunas temáticas da Câmara dos Deputados, preservando a proporcionalidade partidária convencional nas Mesas, nas comissões do Senado Federal, nas CPIs e nas comissões mistas (exceto a regra própria da CMO no Art. 166).
- **Mantém intactos os §§ 2º, 3º e 4º** (preservando CPIs e competências fiscalizatórias das comissões).
- **Acrescenta novos parágrafos (§§ 5º a 8º)** exclusivos da Câmara dos Deputados para instituir:
  - As **Assembleias de Projeto** (coluna especialista + generalistas sorteados com impedimento deliberativo por conflito direto de interesses);
  - A competência colegiada de **despacho temático** pela Tríade Generalista (com recurso ao Plenário por maioria simples) e a **expansão de mesa** vedada a autoconvocação e **expressamente vedada ao Poder Judiciário** (STF excluído);
  - O **Veto Setorial Escalonado**: rejeição de 40% a menos de 75% na Assembleia de Projeto → superação no Plenário por **maioria absoluta**; rejeição de 75% ou mais → superação por **três quintos** dos membros da Câmara;
  - O retorno das emendas do Senado Federal à Assembleia de Projeto originária.

---

### 1.3 Art. 77 da CF/88 (Calendário Eleitoral)
*Fontes conferidas: Portal do Planalto (redação dada pela EC nº 16/1997).*

> **Art. 77.** A eleição do Presidente e do Vice-Presidente da República realizar-se-á, simultaneamente, no primeiro domingo de outubro, em primeiro turno, e no último domingo de outubro, em segundo turno, se houver, do ano anterior ao do término do mandato presidencial vigente.
>
> **§§ 1º a 5º** *(mantidos intactos)*

**Impacto na PEC:**
- **Mantém o *caput* e os §§ 1º a 5º intactos** (não mexe nas regras da eleição presidencial).
- **Acrescenta o § 6º** vinculando incondicionalmente a eleição para a Câmara dos Deputados à data fixa do **último domingo de outubro** (data do segundo turno), **independentemente de o Presidente da República ter sido eleito em primeiro turno**, remetendo à lei complementar o calendário defasado de campanha (+15 dias) e propaganda eleitoral.

---

### 1.4 Art. 166 da CF/88 (Comissão Mista de Orçamento — CMO)
*Fontes conferidas: Portal do Planalto.*

> **Art. 166.** Os projetos de lei relativos ao plano plurianual, às diretrizes orçamentárias, ao orçamento anual e aos créditos adicionais serão apreciados pelas duas Casas do Congresso Nacional, na forma do regimento comum.
>
> **§ 1º** Caberá a uma comissão mista permanente de Senadores e Deputados:
> I – examinar e emitir parecer sobre os projetos referidos neste artigo e sobre as contas apresentadas anualmente pelo Presidente da República;
> II – examinar e emitir parecer sobre os planos e programas nacionais, regionais e setoriais previstos nesta Constituição e exercer o acompanhamento e a fiscalização orçamentária, sem prejuízo da atuação das demais comissões do Congresso Nacional e de suas Casas, criadas de acordo com o art. 58.

**Impacto na PEC:**
- **Acrescenta o § 1º-A** (sem renumerar os §§ 2º e seguintes, conforme LC 95/1998) estabelecendo que:
  1. A representação da Câmara dos Deputados na comissão mista do § 1º (CMO) é exercida pelo **Colegiado Orçamentário**, integrado pelos membros da Coluna de Estado de Economia, Finanças e Orçamento (60 deputados) e pelos Presidentes das demais colunas temáticas com representação na legislatura (11 no cenário-base; até 14 com 6 missões ativas);
  2. **Não se aplica o veto setorial** previsto no art. 58 às leis orçamentárias (PPA, LDO, LOA e créditos adicionais) nem às matérias de deliberação em sessão conjunta do Congresso Nacional, evitando risco de paralisação fiscal (*shutdown*).

---

### 1.5 Marco Numérico do ADCT e Princípio da Anualidade (Art. 16)
*Fontes conferidas: STF / Planalto.*
- O último artigo consolidado no **Ato das Disposições Constitucionais Transitórias (ADCT)** é o **Art. 138** (acrescentado pela EC nº 135, de 20 de dezembro de 2024). As Emendas Constitucionais posteriores de 2025 (EC nº 136/2025 — precatórios; EC nº 138/2025 — acumulação de cargos de professor) alteraram dispositivos existentes sem criar novo artigo ao final do ADCT.
- **Numeração adotada na PEC:** **Art. 139 do ADCT** (com nota de conferência de numeração no momento do protocolo), disciplinando:
  1. Aplicação da RTP a partir da **primeira eleição geral para a Câmara dos Deputados que ocorra após decorrido o prazo do art. 16 da CF/88** (princípio da anualidade eleitoral — mínimo de 1 ano entre a promulgação da Emenda e o pleito, mirando o ciclo de 2030);
  2. Prazo de até **180 dias** após a promulgação para a edição da Lei Complementar regulamentadora e adaptação do Regimento Interno da Câmara;
  3. Regra de transição para a legislatura em curso (permanece sob o regime anterior até o término dos mandatos).

---

### 1.6 Jurisprudência Conferida: ADI 5.081/DF (STF)
- **Julgamento:** Plenário do STF, em **27/05/2015**, Rel. Min. Luís Roberto Barroso (unanimidade).
- **Tese firmada:** A perda de mandato por infidelidade partidária **aplica-se ao sistema proporcional** (onde o mandato pertence ao partido político), mas **não se aplica ao sistema majoritário** (Presidente, Governador, Prefeito e Senador), sob pena de violação à soberania popular.
- **Consequência direta para a PEC/PLP (`D-20` / `RT-11`):** Como a RTP substitui o sistema proporcional tradicional por um sistema proporcional temático-federativo (com transferência intrapartidária e votos de legenda na Tela 2), a PEC deve explicitar no Art. 45 que o mandato na RTP vincula-se **simultaneamente ao partido político e à coluna temática**, legitimando constitucionalmente a **suplência em dois níveis** (1º mesmo partido na célula UF × Coluna; 2º mesmo partido na mesma coluna em outra UF da mesma macrorregião oficial do IBGE) sem atrito com a jurisprudência da ADI 5.081.

---

## 2. Calibração Empírica do STV Enxuto no Modelo de Filas (`RT-21` / `Q-08`)

Em conformidade com `D-12` e o plano da Etapa 2.1, o módulo [`simulador/src/estresse_redteam.py`](../simulador/src/estresse_redteam.py) foi atualizado com o quarto regime operacional (`cenario_rtp_stv_enxuto`) e submetido a varredura de sensibilidade para seção típica de **400 eleitores aptos**, **80% de comparecimento (320 votantes)**, **9h de votação (32.400s)** e **15s de biometria**.

### 2.1 Premissa do STV Enxuto (Votos 1, 2 e 3)
- **Fluxo na urna:** 1 número obrigatório + campo facultativo imediato para **no máximo uma 2ª opção** (quem não deseja indicar 2ª preferência pressiona `CONFIRMA`/`PULAR`, acionando transferência automática intrapartidária).
- **Composição de tempo médio calibrado:**
  - Base uninominal simples (Presidente + Voto 4 em 2 telas + Votos 1–3): `55,0s`.
  - ~65% dos eleitores pulam a 2ª opção (`+2,5s` totais); ~35% digitam a 2ª opção nos 3 votos (`+30,0s` totais) → acréscimo médio ponderado de `~12,1s` a `17,0s` → **calibrado conservadoramente em `72,0s` de votação (`87,0s` totais com biometria)**.

### 2.2 Curva de Sensibilidade Empírica (`simulador/src/estresse_redteam.py`)

| Regime / Tempo de Votação (+15s biometria) | Capacidade Máx. (9h) | Atendidos até 17h | Fila Residual às 17h | Minutos Extras após 17h | Espera Média | Diagnóstico Operacional |
|---|---:|---:|---:|---:|---:|---|
| 55s (70s) — RTP Uninominal Simples | 462 | 319 | 1 | 0,10 min | 0,00 min | Folga máxima (melhor que 1º turno atual: 450) |
| 65s (80s) — STV Enxuto (baixa adesão à 2ª opção) | 405 | 319 | 1 | 0,26 min | 1,27 min | Folga ampla |
| **72s (87s) — STV Enxuto (padrão calibrado)** | **372** | **319** | **1** | **0,38 min** | **4,31 min** | **Operacionalmente seguro (+52 vagas de folga)** |
| 80s (95s) — STV Enxuto (alta adesão à 2ª opção) | 341 | 319 | 1 | 0,51 min | 10,61 min | Seguro, mas margem estreita |
| 85s (100s) — **Teto ergonômico de segurança** | **324** | **319** | **1** | **0,60 min** | **19,25 min** | **Limite crítico (apenas +4 vagas de folga)** |
| 90s (105s) — **Ponto de ruptura / saturação** | **308** | **308** | **12** | **20,77 min** | **32,39 min** | **Colapso inicial (capacidade < 320 votantes)** |
| 100s (115s) — Ordenação parcial (2–3 opções) | 281 | 281 | 39 | 74,10 min | 58,98 min | Inviável |
| 130s (145s) — Ordenação extensa (3+ opções) | 223 | 223 | 97 | 234,10 min | 138,73 min | Colapso severo (+3h54 extras) |

**Conclusão normativa para o PLP (`Q-08`):** A calibração comprova que o **STV enxuto (até 2ª opção estritamente opcional)** mantém a seção operando com folga segura (**1 eleitor na fila às 17h, 0,38 min extra**), enquanto qualquer expansão para 3 ou mais preferências cruza o ponto de ruptura de 90s (+15s) e colapsa a seção. O PLP deve, portanto, **limitar expressamente o ranqueamento a no máximo 2 preferências** (1 obrigatória + 1 facultativa rápida).

---

## 3. Matriz Definitiva de Competência Normativa (PEC vs. PLP vs. RICD)

| Tema / Regra | **PEC (CF/88 + ADCT)** | **PLP (Lei Complementar)** | **RICD (Regimento Interno)** |
|---|---|---|---|
| **Nome e natureza do sistema** | Art. 45, *caput*: institui a Representação Temática Proporcional (RTP). | Detalha toda a sistemática eleitoral e de apuração. | Adequação das normas internas da Câmara. |
| **Pacto federativo (513 / 8 a 70)** | Art. 45, § 1º: **intacto** (piso 8, teto 70 por UF). | Reproduz e aplica a tabela vigente de bancadas $s_e$. | — |
| **Arquitetura dos 3 Blocos** | Art. 45, § 3º: define os 3 blocos (Estado fixo em 180 / 3 colunas de 60; Permanentes com piso protetor; Missão sem piso, ativação plural dos finalistas). | Nomeia as 9 colunas fixas/permanentes, fixa o piso protetor de 20 e estabelece o **Catálogo Oficial de 10–15 temas de Missão** + periodicidade de revisão (`Q-10`). | — |
| **Teto de Missão e Protesto Tela 1** | Art. 45, § 4º: teto estadual de 20% ($\lfloor 0{,}20 s_e \rfloor$) com redução proporcional por votos em branco/nulos na escolha temática. | Fórmula exata $u_e = [\![\tau_e \cdot a_e]\!]$, fluxo de **2 telas do Voto 4**, distinção entre protesto (Tela 1) e voto de legenda / confiança neutra (Tela 2). | — |
| **Algoritmo de Alocação** | Art. 45, § 5º: determina distribuição **biproporcional** que respeita simultaneamente bancadas estaduais e totais temáticos nacionais, remetendo o método à LC. | Sainte-Laguë ($H_3$ e $H_2$ separados), Balinski–Demange + coluna de folga Gaffke–Pukelsheim, contingência lexicográfica ($\epsilon = 10^{-9}$), publicação de multiplicadores e código aberto auditável. | — |
| **Escolha individual (STV enxuto)** | Art. 45, § 5º: prevê preenchimento intracelular por voto único transferível simplificado, nos termos da LC. | **STV enxuto** nos Votos 1–3 (1 número obrigatório + no máximo 2ª opção facultativa; vedação a 3+ escolhas), transferência intrapartidária automática, cota de Droop, desempate, prefixo numérico na urna, cumulação Votos 2–3 (`Q-05`), destino de candidatos em temas eliminados no 1º turno (`Q-02`). | — |
| **Voto no Exterior (ZZ) e Trânsito** | Art. 45, § 6º: habilita voto por legenda temática na totalização nacional das colunas, vedada alteração das cotas estaduais do § 1º. | Operacionalização pelo TSE (cédula temática pura, integração em $V_c$). | — |
| **Mandato Temático e Suplência** | Art. 45, § 7º: vinculação exclusiva à coluna e ao partido (alinhado à ADI 5.081), remetendo a suplência regionalizada à LC. | Ordem sucessória em 2 níveis: 1º mesmo partido na célula; 2º mesmo partido na mesma coluna na macrorregião IBGE (`D-20`). | — |
| **Data da Eleição e Campanha** | Art. 77, § 6º: eleição da Câmara sempre no último domingo de outubro (data do 2º turno), mesmo com definição presidencial no 1º turno. | Campanha da Câmara inicia **+15 dias** após início geral (~1º/set), mesmo teto de gastos, foco exclusivo do HGPE em outubro (`D-23`). | — |
| **Comissões, Despacho e Expansão** | Art. 58, §§ 1º, 5º e 6º: lotação exclusiva por coluna, Assembleias de Projeto com generalistas sorteados, despacho pela Tríade Generalista (recurso ao Plenário), proibição de autoconvocação e **exclusão expressa do STF/Judiciário**. | Critérios objetivos de despacho temático; rol complementar de legitimados para requerer expansão (Executivo, órgãos da Câmara e eventual PGR/AGU — `Q-06`). | Quantitativo exato e rito de sorteio dos generalistas (`Q-04`), eleição de Presidentes de Coluna, transparência de agendas, impedimento por conflito de interesses e faltas. |
| **Veto Setorial Escalonado** | Art. 58, § 7º: rejeição na Assembleia de Projeto de **40% a menos de 75%** → superação por maioria absoluta; **75% ou mais** → superação por 3/5. | — | Rito de contagem nominal na Assembleia de Projeto e encaminhamento ao Plenário. |
| **Emendas do Senado** | Art. 58, § 8º: retorno à Assembleia de Projeto originária. | — | Tramitação revisora interna. |
| **Orçamento (CMO / Art. 166)** | Art. 166, § 1º-A: **Colegiado Orçamentário** (Coluna 1 + Presidentes das demais colunas ativas) na CMO; **exclusão expressa do veto setorial** sobre PPA, LDO, LOA e créditos adicionais. | — | Normas internas de funcionamento do Colegiado Orçamentário na CMO. |
| **Transição e Anualidade** | **Art. 139 do ADCT**: vigência imediata, aplicação na 1ª eleição geral que respeite o Art. 16 (anualidade), prazo de 180 dias para o PLP e preservação da legislatura em curso. | Regras de transição operacional para o TSE (adaptação de urnas e simulados públicos). | Prazo de adaptação regimental. |

---

## 4. Definições Paramétricas para o PLP (Etapa 2.3)

1. **`Q-02` (Candidatos em temas de presidenciáveis eliminados no 1º turno) — `[FECHADA]`:**
   - O candidato inscrito em tema exclusivo de presidenciável eliminado no 1º turno pode migrar para uma das colunas de missão ativas do Presidente eleito no 1º turno ou de um dos finalistas do 2º turno, declarando apoio político direto, **desde que formalmente aceito** pelo respectivo candidato presidencial (ou coligação/federação habilitada). Caso não haja pedido ou aceite dentro do prazo operacional (ex.: 48h após a proclamação do 1º turno), a candidatura perde o objeto, com restituição proporcional de eventual saldo não utilizado do Fundo Eleitoral.
2. **`Q-05` (Cumulação dos Votos 2 e 3 na mesma coluna permanente) — `[FECHADA]`:**
   - **Cumulação proibida.** O eleitor deve escolher **duas colunas permanentes distintas** nos Votos 2 e 3. A repetição da mesma coluna permanente no Voto 3 **anula apenas o segundo voto** (preservando válido o Voto 2, com alerta prévio na urna eletrônica, em analogia operacional à votação para duas vagas ao Senado Federal).
3. **`Q-06` (Extensão do pedido de expansão de mesa à PGR ou AGU) — `[FECHADA]`:**
   - **PGR incluída; AGU excluída; STF 100% vedado.** Podem requerer expansão da Assembleia de Projeto: o Poder Executivo, frações qualificadas das colunas internas da Câmara e a Procuradoria-Geral da República (PGR), decidindo a Tríade Generalista por maioria simples.
4. **`Q-10` (Catálogo Oficial de 10–15 Temas de Missão e sua revisão) — `[FECHADA]`:**
   - O PLP define a estrutura, os parâmetros (10 a 15 temas) e os critérios de instituição/atualização do catálogo, deixando a definição nominal definitiva dos temas para deliberação legislativa específica após a aprovação da PEC. A lista ilustrativa de temas (Transição Energética, IA e Soberania Digital etc.) permanece exclusivamente nos documentos suplementares e na Justificação como exemplo didático.
