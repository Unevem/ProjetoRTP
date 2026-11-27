# Red Team da Comunidade: Tente Quebrar a RTP

> **Como participar:** pense como um político mal-intencionado, cacique partidário, lobista ou estrategista de campanha tentando burlar ou explorar as regras da **Representação Temática Proporcional (RTP)**.
>
> Encontrou uma brecha nova? Abra uma Issue usando o modelo **[Tente Quebrar a RTP (Ataque / Brecha)](../.github/ISSUE_TEMPLATE/ataque-red-team.md)** ou poste em **[Discussions](https://github.com/Unevem/ProjetoRTP/discussions)**. Quem descobre um ataque real recebe crédito aqui.

---

## 1. Ataques e Brechas em Aberto

### ATK-01: Concentração do Fundo Eleitoral (FEFC) por caciques partidários em células pequenas
- **Status:** Em aberto (sem solução fechada ainda)
- **Origem:** Crítica levantada por Fernando Meireles (IESP-UERJ)
- **Ator adversário:** Direção nacional ou estadual de partido político (caciques) durante a campanha eleitoral.
- **Como funciona o ataque:**
  - Na lista aberta atual, um Estado grande disputa dezenas de vagas conjuntas, dando margem para candidatos fora da cúpula partidária se elegerem com votação própria.
  - Na RTP, as vagas estaduais são divididas entre 12 a 15 colunas temáticas, fazendo com que muitas células `(Estado x Tema)` tenham apenas 1 ou 2 vagas.
  - Como as direções partidárias concentram a distribuição discricionária do Fundo Eleitoral (FEFC) e do Fundo Partidário, o cacique pode despejar o máximo de recursos em um único "escolhido" naquela célula de 1 vaga, reduzindo a competição interna e ampliando ainda mais o poder das cúpulas partidárias sobre quem se elege.
- **Contexto comparativo:** vale reconhecer abertamente que o controle das cúpulas partidárias sobre o FEFC é um problema estrutural do modelo de financiamento brasileiro atual (presente na Lista Aberta e ainda mais forte na lista fechada do Voto Distrital Misto), embora células menores na RTP possam amplificar esse efeito localmente.
- **Por que é difícil de resolver:** regras rígidas de distribuição igualitária entre todas as áreas prejudicam justamente os partidos pequenos, que na RTP precisam concentrar esforços em poucas colunas para sobreviver (veja `FVER-01` e `FVER-02` abaixo).
- **Proposta experimental em discussão:** ver [contribuicoes/ajuda-juridica/gustavo-elorza-rolim/proposta-trava-fefc-por-celula.md](../contribuicoes/ajuda-juridica/gustavo-elorza-rolim/proposta-trava-fefc-por-celula.md) (mínimo de candidatos por célula disputada + teto relativo de repasse dentro da célula).

---

### ATK-02: Rigidez constitucional das colunas diante de grandes transformações históricas
- **Status:** Em debate aberto (ver enquete comparativa em [enquetes/01-rigidez-bloco-permanente.md](../enquetes/01-rigidez-bloco-permanente.md))
- **Origem:** Crítica levantada por Fernando Meireles (IESP-UERJ)
- **Ator adversário / Cenário:** Mudanças estruturais de longo prazo (tecnológicas, climáticas, demográficas ou econômicas) que tornem a divisão original de 6 temas permanentes ou os 60 assentos fixos do Bloco de Estado desatualizados.
- **O problema:**
  - Embora o **Bloco de Missão** já funcione por Lei Complementar (permitindo absorver agendas novas sem emenda constitucional) e o **Bloco Permanente** ajuste o tamanho das bancadas pelo voto, os **nomes das 6 colunas permanentes** e o **tamanho fixo de 60 cadeiras do Bloco de Estado** estão gravados na Constituição.
  - Alterar a lista permanente exigiria PEC (três quintos em dois turnos nas duas Casas), o que pode travar adaptações legítimas no futuro. Por outro lado, facilitar demais a mudança por lei simples abre brecha para maiorias circunstanciais redesenharem os temas às vésperas da eleição para prejudicar adversários.

---

## 2. Falhas de Verificação (Contramedidas Testadas e Descartadas)

Esta seção registra ideias de correção que pareciam boas à primeira vista, mas que **quebraram na verificação** por criarem efeitos colaterais piores do que o problema original. Registrar o que *não* funcionou evita que a comunidade perca tempo redescobrindo o mesmo beco sem saída.

### FVER-01: Obrigar o partido a igualar o teto de repasse do FEFC entre todas as colunas
- **Ataque que tentava resolver:** `ATK-01` (concentração do Fundo Eleitoral por caciques em células pequenas).
- **A ideia testada:** impor que o maior financiamento recebido por um candidato em uma área obrigasse o partido a repassar o mesmo valor ao candidato mais financiado das demais áreas (ex.: se o partido deu R$ 300 mil ao seu principal nome em Saúde, teria de dar R$ 300 mil ao principal nome em Educação e nas outras áreas).
- **Por que falhou na verificação:**
  - **Dano assimétrico contra partidos pequenos:** um partido grande tem fundo bilionário para bancar candidatos de ponta em todas as 12 a 15 colunas ao mesmo tempo. Já um partido pequeno ou temático só consegue ser competitivo na RTP se concentrar seus poucos recursos em 1 ou 2 colunas estratégicas.
  - Obrigá-lo a espalhar o mesmo teto pelas demais áreas diluiria o fundo dos partidos pequenos a ponto de inviabilizar suas candidaturas, reforçando ainda mais o oligopólio das grandes legendas.
- **Conclusão:** descartada. Eventual trava contra concentração pelo cacique precisará operar **dentro de cada coluna/célula em que o partido decidir competir**, sem forçar partidos pequenos a financiar áreas onde não têm base.

### FVER-02: Fundo de contrapartida (*matching funds* por pequenas doações) como solução isolada
- **Ataque que tentava resolver:** `ATK-01` (concentração do Fundo Eleitoral por caciques).
- **A ideia testada:** vincular a liberação do FEFC a pequenas doações de pessoas físicas para tirar o monopólio da cúpula partidária.
- **Por que é insuficiente na verificação:** na prática eleitoral brasileira, a influência direta e a rede política do cacique continuam direcionando volume muito maior de doações para seus escolhidos. A medida apenas cria atrito e atraso, sem resolver o problema estrutural de concentração.
