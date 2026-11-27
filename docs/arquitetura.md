# Arquitetura técnica

## Objetivo

O projeto foi organizado em cinco módulos de domínio independentes e um executor responsável por encadear os experimentos. Cada etapa pode ser importada e utilizada isoladamente, enquanto o executor consolida métricas e artefatos em uma única execução.

## Visão do fluxo

~~~text
                       +----------------------+
                       |  src/gerar_resultados |
                       |  orquestração         |
                       +----------+-----------+
                                  |
          +-----------------------+-----------------------+
          |             |              |          |        |
          v             v              v          v        v
     Etapa 1        Etapa 2        Etapa 3    Etapa 4   Etapa 5
     A* / PuLP      DEAP / SimPy   RDF/SPARQL MLP       Mamdani /
                                                       Sugeno
          |             |              |          |        |
          +-------------+--------------+----------+--------+
                                  |
                                  v
                         Pasta resultados/
                    JSON, Turtle e visualizações
~~~

## Responsabilidade dos módulos

### Etapa 1 — roteamento e alocação

Arquivo: <code>src/etapa1_roteamento/modelo.py</code>

- Constrói um grafo não direcionado a partir de uma malha ortogonal.
- Remove as células configuradas como obstáculos.
- Aplica A* com heurística Manhattan e custo unitário por aresta.
- Define tipos de mini-carregadeira por capacidade, custo e disponibilidade.
- Formula um problema de minimização com variáveis inteiras e restrição de capacidade mínima.

### Etapa 2 — otimização e simulação

Arquivo: <code>src/etapa2_otimizacao/modelo.py</code>

- Calcula a distância euclidiana dos trechos de uma rota fechada.
- Penaliza soluções que ultrapassem a capacidade de carga.
- Compara a busca genética com a enumeração de todas as permutações.
- Representa as operações sequenciais por recursos SimPy com capacidade unitária.
- Registra chegadas, conclusões, tempos de fila e o possível gargalo.

### Etapa 3 — representação de conhecimento

Arquivo: <code>src/etapa3_conhecimento/modelo.py</code>

- Declara classes e relações em um namespace RDF de exemplo.
- Modela projeto, insumos e fornecedores como recursos.
- Armazena atributos como nível de resistência e homologação.
- Consulta os relacionamentos com SPARQL e retorna pares material-fornecedor.

### Etapa 4 — classificação com MLP

Arquivo: <code>src/etapa4_rede_neural/modelo.py</code>

- Gera um conjunto tabular artificial com dez variáveis e três classes.
- Divide os exemplos em treino e teste e padroniza as variáveis.
- Implementa camadas densas, ReLU, Softmax e entropia cruzada.
- Treina com mini-batches e retropropagação.
- Expõe uma rotina de inferência que devolve classe e probabilidades.

### Etapa 5 — controle fuzzy

Arquivo: <code>src/etapa5_fuzzy/modelo.py</code>

- Define universos de discurso para temperatura, umidade e saída.
- Configura funções de pertinência triangulares.
- Aplica regras de inferência Mamdani e defuzzificação pelo centróide.
- Calcula Sugeno de ordem zero com consequentes constantes.
- Amostra uma grade de entradas para produzir superfícies de resposta.

## Orquestração e artefatos

O módulo <code>src/gerar_resultados.py</code> executa as etapas em ordem e consolida os resultados em <code>resultados/resultados_execucao.json</code>. Também exporta:

- PNG do caminho A*;
- PNG com os tempos de serviço da simulação;
- grafo RDF no formato Turtle;
- PNG da curva de perda da MLP;
- superfícies fuzzy Mamdani e Sugeno em PNG.

A pasta de resultados gerados é mantida fora do controle de versão por padrão. Assim, cada pessoa pode reproduzir os artefatos no próprio ambiente sem misturar saídas de execuções diferentes.

## Testes e CI

A suíte em <code>tests/test_etapas_disponiveis.py</code> contém verificações funcionais para os modelos principais. Dependências opcionais são verificadas com <code>pytest.importorskip</code>, permitindo que testes independentes sejam executados mesmo quando um pacote específico não está instalado.

O workflow do GitHub Actions instala o arquivo de dependências completo e executa a suíte em Python 3.12.

## Limites arquiteturais

A arquitetura privilegia a clareza didática em vez de uma aplicação pronta para produção. Os módulos usam dados e parâmetros definidos no próprio código, não persistem em banco de dados, não integram sensores ou sistemas externos e não incluem interface de operação. Para evoluir o protótipo, seria necessário separar configuração de código, validar entradas, introduzir dados versionados e adicionar avaliação sistemática dos modelos.
