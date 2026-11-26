# APS 2 - IA Aplicada | Canteiro de Obras Inteligente

Projeto academico para a APS 2 de Inteligencia Artificial Aplicada, Engenharia de Software - UniSENAI PR, Campus Londrina, 2026/2.

## Grupo
- **Lider:** Luiz Miguel Rodrigues da Silva Alves
- Fabio Araujo Bruno
- Eduardo Odelon Wagner
- Gustavo Henrique Volso Fernandes
- Mateus Bolotaro Rodrigues

## Escopo
Cinco prototipos: A* e alocacao PuLP; Algoritmo Genetico DEAP e simulacao SimPy; grafo RDF/SPARQL; MLP implementada com NumPy; controle Fuzzy Mamdani/Sugeno.

## Execucao
Recomenda-se Python 3.11 ou superior:
```bash
python -m venv .venv
python -m pip install -r requirements.txt
python -m pytest -q
python -m src.gerar_resultados
```

O notebook integrado para Google Colab esta em `notebooks/APS2_IA_Aplicada_Torre_Europarque.ipynb`. Abra-o no Colab, execute todas as celulas e salve uma copia com os resultados antes da submissao.

## Premissas
O enunciado nao fornece todos os dados operacionais. Custos/capacidades das carregadeiras, coordenadas/demandas dos blocos, telemetria e fornecedores foram modelados com dados sinteticos, identificados no codigo e no relatorio. Os fornecedores sao ficticios; nao ha consulta real a uma base SINAPI/CUB.

## Validacao
Testes locais de A*, RDF/SPARQL e MLP foram executados. A validacao integral de PuLP, DEAP, SimPy e scikit-fuzzy depende da instalacao das bibliotecas e da execucao completa no Colab. Nao interpretar dados simulados como dados reais da construtora.

Relatorio tecnico: `docs/relatorio_tecnico.docx`.
