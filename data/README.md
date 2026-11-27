# Dados e premissas

Este repositório não contém uma base operacional da construtora nem medições de uma obra real. Os valores usados pelos modelos foram escolhidos para compor um cenário didático reproduzível.

## Dados definidos pelo cenário

- dimensões da malha, obstáculos, origem e destino;
- demanda mínima de capacidade da frota;
- quantidade de blocos, capacidade máxima do caminhão e tempos de serviço M1/M2;
- universos de discurso das variáveis fuzzy;
- quantidade e significado das variáveis e classes da MLP.

## Dados sintéticos definidos na implementação

- custos, capacidades e disponibilidade dos tipos de mini-carregadeira;
- coordenadas e demandas individuais dos blocos;
- intervalo de chegada de lotes na simulação;
- fornecedores e atributos do grafo RDF;
- telemetria artificial usada para treinamento e teste da MLP;
- funções de pertinência, regras e consequentes dos controladores fuzzy.

As referências textuais a SINAPI/CUB são ilustrativas. Não há integração, consulta ou validação com essas bases comerciais. Consulte [decisoes_e_premissas.md](../docs/decisoes_e_premissas.md) para ver os parâmetros e as limitações completos.
