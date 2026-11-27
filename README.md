# Canteiro Inteligente — IA e Otimização para Planejamento de Obras

[![Testes](https://github.com/LuizMiguelRodriguesdaSilvaAlves/APS2-IA-Aplicada-Torre-Europarque/actions/workflows/tests.yml/badge.svg?branch=main)](https://github.com/LuizMiguelRodriguesdaSilvaAlves/APS2-IA-Aplicada-Torre-Europarque/actions/workflows/tests.yml)
![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Um conjunto de protótipos em Python que explora como algoritmos de busca, otimização, simulação, representação de conhecimento, redes neurais e lógica fuzzy podem apoiar problemas de planejamento em um canteiro de obras.

O projeto foi desenvolvido em equipe a partir de um cenário didático inspirado na Torre Europarque e foi mantido como material de estudo e portfólio. A proposta é demonstrar conceitos e tornar cada etapa reproduzível, com código organizado, testes automatizados e premissas documentadas.

> **Escopo:** trata-se de um protótipo experimental. Custos, capacidades, coordenadas, demandas, fornecedores e telemetria são dados hipotéticos ou sintéticos. Os resultados não representam medições de uma obra real nem devem orientar decisões operacionais.

## Visão geral

O repositório reúne cinco etapas que podem ser estudadas separadamente ou executadas em sequência:

| Etapa | Problema explorado | Técnicas e bibliotecas |
| --- | --- | --- |
| 1. Roteamento e frota | Encontrar caminhos em uma malha com obstáculos e selecionar equipamentos de menor custo | A*, NetworkX, programação linear inteira com PuLP |
| 2. Otimização e fluxo | Organizar entregas e analisar filas em operações sequenciais | Algoritmo genético com DEAP, benchmark exato e SimPy |
| 3. Conhecimento | Representar materiais e fornecedores e consultar relações | RDF, RDFLib e SPARQL |
| 4. Rede neural | Classificar estados simulados de equipamentos | MLP implementada com NumPy, ReLU, Softmax e entropia cruzada |
| 5. Lógica fuzzy | Estimar uma saída ilustrativa a partir de temperatura e umidade | Mamdani, Sugeno de ordem zero e scikit-fuzzy |

## Como cada etapa funciona

### 1. Roteamento e alocação de mini-carregadeiras

A área de trabalho é representada por uma malha ortogonal 8 × 8. Células bloqueadas são removidas do grafo, e o A* procura um caminho entre a origem e o destino usando a distância Manhattan como heurística.

Na segunda parte, um modelo de programação linear inteira escolhe quantas unidades de cada tipo de mini-carregadeira devem ser utilizadas. A função objetivo minimiza o custo diário hipotético, enquanto a restrição principal exige capacidade suficiente para atender à demanda mínima.

### 2. Otimização de entregas e simulação de concretagem

O problema de entregas é modelado como uma rota fechada: o caminhão parte do depósito, visita os seis blocos e retorna à origem. O DEAP procura uma boa ordem de visita por meio de seleção, cruzamento e mutação. Para avaliar a solução em um cenário pequeno, o projeto também enumera todas as 720 permutações possíveis e calcula o melhor resultado exato.

A simulação com SimPy representa a chegada de lotes e o atendimento por dois recursos em série. O modelo registra chegadas, lotes concluídos, espera média em filas e o recurso que tende a limitar o fluxo.

### 3. Grafo de conhecimento RDF

Materiais, projeto e fornecedores são representados como recursos ligados por triplas RDF. A consulta SPARQL demonstra como recuperar materiais classificados com resistência alta e associados a fornecedores marcados como homologados.

Os fornecedores são fictícios. Os rótulos SINAPI/CUB são referências ilustrativas e não representam consulta a uma base comercial.

### 4. Rede neural MLP com NumPy

A rede é construída a partir de operações matriciais, sem utilizar um framework de treinamento de alto nível. A arquitetura demonstrativa possui dez entradas, uma camada oculta com 16 neurônios e três classes de saída.

O fluxo inclui padronização das variáveis, mini-batches, propagação direta, cálculo do gradiente, retropropagação e atualização dos pesos por descida do gradiente. O conjunto é gerado artificialmente para permitir a reprodução do experimento.

### 5. Controladores fuzzy Mamdani e Sugeno

Os controladores recebem temperatura e umidade como entradas e calculam uma taxa ilustrativa de aditivo como saída. O modelo Mamdani utiliza regras linguísticas e defuzzificação pelo centróide; o Sugeno de ordem zero utiliza consequentes constantes e média ponderada.

As funções de pertinência e regras servem para demonstrar os dois métodos, não para recomendar dosagem de concreto.

## Resultados de referência

Na execução de referência registrada no notebook integrado, os protótipos produziram os seguintes resultados:

| Componente | Resultado observado |
| --- | --- |
| A* | Caminho com 14 arestas entre a origem e o destino |
| PuLP | 2 unidades A e 2 unidades C; capacidade de 450 t/dia; custo hipotético de R$ 2.900/dia |
| DEAP | Encontrou a mesma distância do benchmark exato: 23,069 unidades |
| SimPy | 42 lotes concluídos entre 75 chegadas; Bomba M2 identificada como gargalo; espera média de 61,5 min |
| RDF/SPARQL | Grafo com 35 triplas; consulta retornou 2 fornecedores fictícios |
| MLP | 100% de acurácia no conjunto de teste sintético utilizado na execução |
| Fuzzy | Para 34 °C e 30% de umidade: 50,000% (Mamdani) e 56,786% (Sugeno) |

Esses números são resultados do cenário e da execução de referência, não indicadores de desempenho real. Em particular, a acurácia da MLP não permite concluir que o modelo reconheceria falhas em sensores industriais reais.

## Arquitetura do repositório

~~~text
.
├── .github/
│   └── workflows/
│       └── tests.yml
├── data/
│   └── README.md
├── docs/
│   ├── arquitetura.md
│   └── decisoes_e_premissas.md
├── resultados/
│   ├── README.md
│   └── validacao_parcial.json
├── src/
│   ├── etapa1_roteamento/
│   │   └── modelo.py
│   ├── etapa2_otimizacao/
│   │   └── modelo.py
│   ├── etapa3_conhecimento/
│   │   └── modelo.py
│   ├── etapa4_rede_neural/
│   │   └── modelo.py
│   ├── etapa5_fuzzy/
│   │   └── modelo.py
│   └── gerar_resultados.py
├── tests/
│   └── test_etapas_disponiveis.py
├── .gitignore
├── LICENSE
├── README.md
└── requirements.txt
~~~

Para entender o fluxo entre os módulos, consulte [docs/arquitetura.md](docs/arquitetura.md). As escolhas de modelagem e as limitações dos dados estão descritas em [docs/decisoes_e_premissas.md](docs/decisoes_e_premissas.md).

## Tecnologias

- **Python 3.11+** — linguagem principal.
- **NetworkX** — modelagem de grafos e busca A*.
- **PuLP** — formulação e resolução do problema de alocação inteira.
- **DEAP** — operadores e execução do algoritmo genético.
- **SimPy** — simulação de eventos discretos e recursos compartilhados.
- **RDFLib** — grafo RDF e consultas SPARQL.
- **NumPy** — operações matriciais e implementação da MLP.
- **scikit-fuzzy** — conjuntos de pertinência e controle fuzzy.
- **Matplotlib** — geração das visualizações.
- **pytest** — testes automatizados.
- **GitHub Actions** — execução dos testes a cada push ou pull request para a branch principal.

## Como executar

### Requisitos

- Python 3.11 ou superior.
- pip.
- Git, caso queira clonar o repositório.

### 1. Clonar o projeto

~~~bash
git clone https://github.com/LuizMiguelRodriguesdaSilvaAlves/APS2-IA-Aplicada-Torre-Europarque.git
cd APS2-IA-Aplicada-Torre-Europarque
~~~

### 2. Criar e ativar um ambiente virtual

**Windows (PowerShell):**

~~~powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
~~~

**Linux ou macOS:**

~~~bash
python3 -m venv .venv
source .venv/bin/activate
~~~

### 3. Instalar as dependências

~~~bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
~~~

### 4. Executar os testes

~~~bash
python -m pytest -q
~~~

### 5. Gerar os resultados e gráficos

~~~bash
python -m src.gerar_resultados
~~~

O executor percorre as cinco etapas e grava os arquivos gerados na pasta <code>resultados/</code>, incluindo métricas em JSON, o grafo RDF em Turtle e visualizações PNG. Esses artefatos são saídas locais da execução e podem ser regenerados a qualquer momento.

## Testes e integração contínua

A suíte automatizada verifica, entre outros pontos:

- caminho A* e respeito aos obstáculos;
- consistência da consulta RDF/SPARQL;
- formato das probabilidades da MLP;
- resultado de referência da otimização da frota;
- comparação entre a rota exata e o algoritmo genético;
- execução dos componentes que dependem de PuLP, DEAP, SimPy e scikit-fuzzy, quando instalados.

O workflow em <code>.github/workflows/tests.yml</code> instala as dependências e executa o pytest com Python 3.12 em pushes e pull requests direcionados à branch <code>main</code>.

## Dados, premissas e limitações

O cenário foi montado para fins de demonstração. Entre as premissas utilizadas estão:

- capacidade e custo diário hipotéticos para os tipos de mini-carregadeira;
- coordenadas e demandas artificiais para os seis blocos;
- intervalo regular de chegada dos lotes na simulação;
- fornecedores fictícios e propriedades simplificadas no grafo RDF;
- telemetria gerada por distribuições sintéticas para treinar e testar a MLP;
- funções de pertinência e regras fuzzy definidas para ilustrar os métodos.

Antes de qualquer aplicação em ambiente real, seria necessário substituir os dados de exemplo por informações verificadas, validar os modelos com especialistas, avaliar riscos, calibrar parâmetros e realizar testes com dados representativos. A documentação completa está em [docs/decisoes_e_premissas.md](docs/decisoes_e_premissas.md).

## Equipe

Projeto desenvolvido em equipe por:

- **Luiz Miguel Rodrigues da Silva Alves** — liderança do grupo.
- Fábio Araújo Bruno.
- Eduardo Odelon Wagner.
- Gustavo Henrique Volso Fernandes.
- Mateus Bolotaro Rodrigues.

## Licença

Este projeto está distribuído sob a licença [MIT](LICENSE). Consulte o arquivo de licença para conhecer as permissões e condições de uso. As bibliotecas utilizadas mantêm suas próprias licenças.
