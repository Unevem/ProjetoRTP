# Gustavo Elorza Rolim - Proposta Experimental contra Concentração do FEFC por Caciques (`ATK-01`)

> **Nota do autor:** deixei esta proposta fora das minutas principais (`pec/PEC_RTP.md` e `pec/PLP_RTP.md`) propositalmente, usando o mesmo formato de pasta nominal aberto a qualquer colaborador, para que a ideia passe por críticas antes de eventualmente entrar no texto principal.

## 1. O que estou criticando ou como quero ajudar
Esta contribuição tenta responder ao ataque **[ATK-01](../../../redteam/ATAQUES_ABERTOS.md)** (levantado por Fernando Meireles): o risco de caciques partidários ganharem ainda mais poder de campanha na RTP ao concentrar os recursos do Fundo Eleitoral (FEFC) em um único nome dentro de células `(Estado x Tema)` que disputam poucas vagas.

## 2. Resumo da contribuição
A proposta combina duas travas aplicadas **apenas dentro da célula em que o partido decidir lançar chapa** (sem obrigar partidos pequenos a financiar todas as áreas):
1. **Mínimo de candidaturas na célula disputada** (ex.: mínimo de **5 candidatos** na célula em que o partido optar por concorrer), o que também ajuda a formar banco local de suplentes e reduz a chance de acionar a suplência macrorregional de 2º nível.
2. **Teto proporcional de desigualdade interna de repasse:** dentro daquela célula, o candidato mais financiado pelo partido não pode receber mais do que **$X\%$** (ou um múltiplo $K$) acima do candidato da mesma célula que menos recebeu.

A proposta também reconhece com franqueza que o monopólio das cúpulas partidárias sobre o FEFC é um problema estrutural do modelo de financiamento brasileiro atual (presente na Lista Aberta e ainda mais forte na lista fechada do Voto Distrital Misto), e lista os novos riscos que essa trava precisaria superar (como candidaturas de fachada/"laranjas" e dificuldade de partidos pequenos reunirem 5 nomes em Estados menores).

## 3. Organização desta pasta
- `README.md`: resumo da proposta e contexto do problema.
- [`proposta-trava-fefc-por-celula.md`](proposta-trava-fefc-por-celula.md): detalhamento da ideia, benefícios colaterais, riscos abertos para Red Team e comparação com alternativas descartadas.
