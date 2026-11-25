# Como Colaborar com o Projeto RTP (`CONTRIBUTING.md`)

A proposta de **Representação Temática Proporcional (RTP)** é aberta a qualquer cidadão, programador, matemático, jurista, cientista político, designer ou comunicador. **Críticas bem fundamentadas têm o mesmo valor que sugestões de melhoria**: o objetivo do repositório é testar se a ideia sobrevive ao escrutínio público e elevar a qualidade do debate sobre reforma política no Brasil.

---

## Como funciona a estrutura de contribuições

Para organizar o trabalho de forma clara e dar crédito direto a cada colaborador, as contribuições ficam separadas em **quatro pastas por área** dentro de `contribuicoes/`:

- `contribuicoes/ajuda-tecnica/`: revisão matemática, auditoria no software BAZI, testes com dados reais do TSE (2022), melhorias no simulador Python ou protótipos web.
- `contribuicoes/ajuda-juridica/`: pareceres constitucionais, críticas eleitorais, revisões de técnica legislativa (LC nº 95/1998) e propostas de emenda aos textos em `pec/`.
- `contribuicoes/ajuda-comunicacao/`: roteiros de vídeo, threads, textos de divulgação para redes sociais ou resumos para o e-Cidadania.
- `contribuicoes/ajuda-design/`: infográficos, diagramas visuais, protótipos de tela da urna eletrônica e layouts para um futuro site interativo no GitHub Pages.

### Regra da pasta com o seu nome

Dentro da categoria escolhida, **crie uma pasta com o seu nome (ou apelido/usuário)** usando letras minúsculas e hífens. Dentro dela, coloque um arquivo `README.md` e os arquivos ou subpastas com suas provas de conceito, códigos, pareceres, planilhas ou mídias.

Exemplo real de estrutura:

```text
contribuicoes/
  ajuda-tecnica/
    TEMPLATE_CONTRIBUICAO/          # Modelo de referência (não apague)
    maria-silva/                    # Pasta criada pela colaboradora
      README.md                     # Obrigatório: o que critica/propõe + resumo + mapa da pasta
      auditoria-bazi/               # Subpasta livre com provas de conceito, scripts, dados etc.
        matriz_exportada.bazi
        comparacao_divisores.py
```

Cada categoria já possui uma pasta `TEMPLATE_CONTRIBUICAO/` pronta para você copiar e renomear com o **seu nome**.

### O que deve constar logo no topo do seu `README.md`

Para facilitar a leitura de qualquer pessoa que abrir sua pasta, comece o seu `README.md` sempre com estes três blocos:

1. **O que estou criticando ou como quero ajudar:** diga em 2 a 4 linhas qual parte do projeto você está analisando (ex.: *"Estou auditando o arredondamento de Sainte-Laguë no simulador"*, *"Discordo da unificação de Agropecuária e Meio Ambiente"* ou *"Criei um protótipo de site estático para visualizar os cálculos"*).
2. **Resumo da contribuição:** explique suas conclusões principais ou o que você construiu, de forma direta.
3. **Organização desta pasta:** liste os arquivos e subpastas que você colocou ali e diga para que serve cada um.

---

## Passo a passo no GitHub (para quem programa e para quem não programa)

### Opção A: Via Pull Request (fluxo padrão GitHub)
1. Faça um **Fork** deste repositório.
2. Copie a pasta `TEMPLATE_CONTRIBUICAO/` dentro da categoria adequada em `contribuicoes/` e renomeie a cópia para `seu-nome` (ex.: `contribuicoes/ajuda-juridica/carlos-souza/`).
3. Preencha o `README.md` da sua pasta e adicione seus arquivos de prova de conceito.
4. Abra um **Pull Request** explicando brevemente o tema da sua contribuição.

### Opção B: Sem mexer com Git (Issues ou Discussions)
Se você não usa Git ou prefere apenas apontar um erro, fazer uma crítica jurídica/política ou sugerir um vídeo/parceria (como ajudar a criar o site no GitHub Pages), basta abrir uma **Issue** no GitHub com o título indicando a área (ex.: `[Jurídico] Questionamento sobre o Art. 45, § 4º` ou `[Comunicação] Ideia de vídeo curto`).

---

## Prioridades atuais de colaboração (`Help Needed`)

1. **Verificação matemática independente (Prioridade 1):** como destacado no [README.md](README.md) e na Seção 4 do [Estudo Técnico](docs/ESTUDO_TECNICO_RTP.md), a modelagem matemática de apuração é a frente em que o autor menos confia na própria revisão individual. Precisamos de validação no **BAZI**, testes de casos extremos e calibração com dados reais das eleições de 2022 do TSE.
2. **Site estático interativo no GitHub Pages:** construção de uma página leve para explicar a ideia visualmente e permitir que visitantes simulem a distribuição de cadeiras direto no navegador.
3. **Revisão jurídica e de ciência política:** análise crítica dos trade-offs assumidos pela proposta, incluindo a manutenção ou separação da coluna de Agropecuária e Meio Ambiente.
4. **Vídeos e divulgação:** se você quiser gravar um vídeo ou escrever uma thread explicando a proposta, consulte o roteiro recomendado em [contribuicoes/ajuda-comunicacao/ROTEIRO_VIDEOS_E_DIVULGACAO.md](contribuicoes/ajuda-comunicacao/ROTEIRO_VIDEOS_E_DIVULGACAO.md).

---

## Diretrizes de tom e estilo para contribuições

- **Honestidade intelectual acima de torcida:** não tente "vender" a RTP como perfeita. Se encontrar uma falha real no modelo, exponha com clareza.
- **Zero invenção de dados:** cite fontes reais (artigos da CF/88, julgados do STF, dados do TSE ou saídas reproduzíveis do simulador).
- **Código Python do simulador:** se enviar alterações em `simulador/`, mantenha compatibilidade com Python 3.12+ usando apenas a biblioteca padrão e garanta que `python -m unittest discover -s simulador/tests` continue passando integralmente.
- **Estilo editorial nos textos principais:** nos documentos oficiais do projeto, evitamos travessão longo e jargão interno não explicado; prefira frases claras com vírgulas, parênteses ou dois-pontos.
