# APS 2 - IA Aplicada | Canteiro de Obras Inteligente

Projeto academico para a APS 2 de Inteligencia Artificial Aplicada, Engenharia de Software - UniSENAI PR, Campus Londrina, semestre 2026/2.

## Grupo
- **Lider:** Luiz Miguel Rodrigues da Silva Alves
- Fabio Araujo Bruno
- Eduardo Odelon Wagner
- Gustavo Henrique Volso Fernandes
- Mateus Bolotaro Rodrigues

## Objetivo
Prototipos de IA/otimizacao para a obra didatica Torre Europarque: A* e PuLP; algoritmo genetico DEAP e simulacao SimPy; RDF/OWL e SPARQL; MLP implementada com NumPy; Fuzzy Mamdani e Sugeno.

## Estrutura
- `src/etapa1_roteamento/`: malha 8x8, busca A* e modelo inteiro de alocacao.
- `src/etapa2_otimizacao/`: rota por permutacao, DEAP e concretagem em SimPy.
- `src/etapa3_conhecimento/`: grafo RDF e consultas SPARQL.
- `src/etapa4_rede_neural/`: camadas Dense, ReLU, Softmax e Cross-Entropy com NumPy.
- `src/etapa5_fuzzy/`: controladores Mamdani e Sugeno.
- `src/gerar_resultados.py`: executor integrado das cinco etapas.
- `tests/`: testes automatizados e validacoes opcionais por dependencia.
- `data/`, `resultados/`, `docs/`: premissas, evidencias e documentacao do projeto.

## Execucao
Recomenda-se Python 3.11 ou superior:
```bash
python -m venv .venv
python -m pip install -r requirements.txt
python -m pytest -q
python -m src.gerar_resultados
```

O notebook integrado e o relatorio tecnico em DOCX tambem fazem parte do pacote de entrega da APS 2. Para acompanhar as etapas na pratica, abra o notebook no Google Colab e execute tudo em **Ambiente de execucao > Executar tudo**. Quando terminar, salve uma copia com as saidas geradas e use essa versao no ZIP final.

## Premissas e limites
Custos/capacidades das carregadeiras, coordenadas/demandas dos blocos, telemetria e fornecedores sao hipoteticos/sinteticos, pois o enunciado nao fornece dados reais. Os fornecedores RDF sao ficticios e nao ha consulta real a uma base comercial SINAPI/CUB. Os prototipos nao devem ser usados em operacao real sem dados validados, calibracao e aprovacao tecnica.

## Estado de validacao
O notebook integrado registra a execucao das cinco etapas e a conclusao da suite automatizada com **8 testes aprovados**. Nessa execucao, o A* encontrou um caminho de 14 arestas; o PuLP retornou uma solucao otima de 2 unidades A e 2 C (450 t/dia, com custo hipotetico de R$ 2.900/dia); o DEAP alcancou o benchmark exato da rota (23,069 unidades de distancia); e a simulacao SimPy processou 42 das 75 chegadas, apontando a Bomba M2 como gargalo e espera media de 61,5 minutos. O grafo RDF gerou 35 triplas e a consulta retornou dois fornecedores ficticios; a MLP obteve 100% de acuracia no conjunto sintetico de teste; e, para 34 °C e 30% de umidade, as saidas Fuzzy foram 50,000% (Mamdani) e 56,786% (Sugeno). Esses numeros demonstram o funcionamento dos prototipos sob as hipoteses adotadas e nao representam dados ou desempenho de uma obra real.

## Repositorio
https://github.com/LuizMiguelRodriguesdaSilvaAlves/APS2-IA-Aplicada-Torre-Europarque
