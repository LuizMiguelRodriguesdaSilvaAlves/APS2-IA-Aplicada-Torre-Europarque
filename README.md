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

O notebook integrado e o relatorio DOCX fazem parte do pacote unificado de entrega da APS 2. O notebook deve ser aberto no Google Colab e executado por completo (Ambiente de execucao > Executar tudo), salvando uma copia com as saidas antes de substituir o arquivo no ZIP final.

## Premissas e limites
Custos/capacidades das carregadeiras, coordenadas/demandas dos blocos, telemetria e fornecedores sao hipoteticos/sinteticos, pois o enunciado nao fornece dados reais. Os fornecedores RDF sao ficticios e nao ha consulta real a uma base comercial SINAPI/CUB. Os prototipos nao devem ser usados em operacao real sem dados validados, calibracao e aprovacao tecnica.

## Estado de validacao
A validacao local disponivel foi registrada em `resultados/validacao_parcial.json`. A* (rota), RDF/SPARQL e MLP foram executados localmente. A confirmacao integral de PuLP, DEAP, SimPy e scikit-fuzzy depende da instalacao das bibliotecas e da execucao completa no Colab; nao foram inventados resultados para essas etapas.

## Repositorio
https://github.com/LuizMiguelRodriguesdaSilvaAlves/APS2-IA-Aplicada-Torre-Europarque
