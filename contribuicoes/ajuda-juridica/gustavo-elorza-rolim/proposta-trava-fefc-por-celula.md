# Proposta Experimental: Mínimo de Candidatos e Teto de Desigualdade do FEFC por Célula

**Alvo:** Ataque `ATK-01` ([redteam/ATAQUES_ABERTOS.md](../../../redteam/ATAQUES_ABERTOS.md))
**Status:** Proposta experimental para debate (não incorporada ao `PLP_RTP.md`)

---

## 1. Contexto honesto do problema
Antes de propor qualquer trava nova, vale registrar um ponto de partida importante para a discussão: o controle concentrado dos caciques sobre o Fundo Eleitoral (FEFC) e o Fundo Partidário **não é um defeito criado pela RTP**. Ele já distorce a competição na Lista Aberta atual e se torna ainda mais concentrado na metade em lista fechada do Voto Distrital Misto (onde a cúpula define diretamente a ordem dos eleitos).

Ainda assim, como a RTP divide as vagas estaduais em células menores `(Estado x Tema)`, o poder de direcionar todo o financiamento para um único nome dentro de uma célula de 1 ou 2 vagas fica mais agudo e merece contramedidas específicas.

---

## 2. Desenho da proposta experimental

Em vez de obrigar o partido a financiar todas as 12 a 15 colunas (ideia descartada em `FVER-01` por destruir partidos pequenos), a trava atuaria **apenas dentro de cada célula em que o partido decidir lançar chapa**:

1. **Mínimo de candidaturas por célula disputada (parâmetro inicial sugerido: 5 candidatos):**
   - O partido continua 100% livre para escolher em quais temas e Estados quer competir (preservando a sobrevivência de partidos pequenos e especializados).
   - Porém, em cada célula onde decidir entrar, precisaria registrar um mínimo de candidatos (ex.: 5 nomes, ou patamar proporcional menor em Estados de 8 a 10 vagas).
   - **Benefício colateral importante:** garante um banco local de suplentes na célula, reduzindo drasticamente a necessidade de acionar a suplência macrorregional de 2º nível.
2. **Teto relativo entre o mais financiado e o menos financiado da célula:**
   - Dentro daquela mesma célula, o candidato que mais receber recursos públicos do partido (FEFC + Fundo Partidário) não pode ultrapassar **$X\%$** (ou um fator máximo, como `2x` ou `3x`) do valor recebido pelo candidato da mesma célula que menos recebeu.
   - Assim, se o cacique quiser injetar muito dinheiro no seu candidato favorito, será obrigado a fortalecer também os outros concorrentes da mesma chapa naquela célula, criando competição interna real.

---

## 3. Por que outras saídas não parecem suficientes sozinhas
- **Equiparar tetos entre colunas diferentes (`FVER-01`):** descartada porque dilui os recursos dos partidos pequenos que precisam focar em 1 ou 2 temas.
- **Fundo de contrapartida (*matching funds* por pequenas doações):** apenas atrasa e dá um pouco mais de trabalho, pois a influência direta e a rede política do cacique continuam direcionando muito mais doações para os seus escolhidos, sem resolver a concentração na raiz.

---

## 4. Novos riscos abertos (o que o Red Team precisa atacar nesta proposta!)
Para manter o padrão de transparência do repositório, esta proposta experimental abre pelo menos três perguntas difíceis que precisam ser testadas pela comunidade:
1. **Risco de candidaturas "laranjas" / de fachada:** se a lei exigir 5 nomes por célula e piso relativo de repasse, caciques podem colocar 4 aliados sem campanha real apenas para cumprir a cota e repassar verba de volta de forma indireta (ou em serviços compartilhados).
2. **Barreira de entrada em Estados pequenos (8 a 10 vagas):** um partido pequeno ou emergente conseguiria recrutar 5 candidatos reais em uma única coluna de um Estado pequeno como Roraima ou Acre? Talvez o mínimo precisasse ser calibrado pelo tamanho da bancada estadual (ex.: 2 ou 3 em Estados menores, 5 nos maiores).
3. **Efeito sobre o voto de legenda e o piso de 10% de Droop:** dividir o fundo entre 5 nomes na mesma célula pode ajudar a pulverizar votos e impedir que um único nome domine, mas também pode dificultar que partidos menores façam alguém atingir a cota em células de 1 vaga.

---

## Como criticar ou melhorar esta proposta
Comente na aba **Discussions** ou abra uma Issue com o modelo **Tente Quebrar a RTP** mostrando como um cacique burlaria essa regra de 5 candidatos + teto de $X\%$.
