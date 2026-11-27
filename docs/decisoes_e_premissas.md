# Decisões técnicas, premissas e limitações

Este documento registra o que pertence ao cenário proposto e o que foi definido apenas para permitir que os protótipos fossem executados. A distinção é importante: números gerados pelo projeto não devem ser interpretados como medições da Torre Europarque ou de qualquer obra real.

## Parâmetros do cenário didático

A implementação utiliza os seguintes elementos de referência:

- malha ortogonal 8 × 8, com obstáculos nas posições (3, 3) e (3, 4);
- origem (0, 0), destino (7, 7) e heurística Manhattan no A*;
- demanda mínima de 450 toneladas por dia para a frota;
- seis blocos para o problema de roteamento de entregas;
- capacidade máxima de 120 toneladas para o caminhão;
- recursos sequenciais M1 e M2, com tempos de serviço de 5 e 7 minutos;
- horizonte de simulação de 300 minutos;
- MLP com dez variáveis de entrada e três classes de saída;
- entradas fuzzy de temperatura entre 0 e 50 °C, umidade entre 0 e 100% e saída entre 0 e 100%.

## Hipóteses sintéticas adotadas

Os seguintes dados foram criados para completar o cenário computacional:

1. **Frota:** tipo A com capacidade de 150 t/dia, custo de R$ 900/dia e disponibilidade de duas unidades; tipo B com 100 t/dia, R$ 700/dia e três unidades; tipo C com 75 t/dia, R$ 550/dia e três unidades.
2. **Entregas:** demandas de 18, 22, 15, 20, 17 e 16 toneladas para os seis blocos, totalizando 108 toneladas. As coordenadas também são artificiais e estão definidas no módulo da Etapa 2.
3. **Simulação:** uma chegada de lote a cada quatro minutos e uma unidade de cada recurso.
4. **RDF:** fornecedores fictícios e propriedades de materiais simplificadas. As referências a SINAPI/CUB são rótulos ilustrativos, sem integração ou consulta a essas bases.
5. **MLP:** telemetria e rótulos são gerados por distribuições normais artificiais, com médias e desvios escolhidos para a demonstração.
6. **Fuzzy:** funções triangulares e regras foram definidas para permitir comparação entre Mamdani e Sugeno. Não constituem orientação de dosagem ou especificação de engenharia.

## Decisões de implementação

- O A* usa distância Manhattan porque os movimentos são ortogonais e têm custo unitário.
- O problema de frota é formulado com variáveis inteiras e resolvido pelo CBC via PuLP.
- A busca genética é comparada a uma enumeração exata das 720 permutações, viável devido ao número pequeno de blocos.
- A simulação representa duas filas sequenciais com recursos de capacidade unitária.
- A MLP é implementada com NumPy para deixar explícitas as operações de forward pass e backpropagation.
- O modelo fuzzy utiliza os mesmos conjuntos e regras conceituais para permitir comparação dos métodos de inferência.

## Resultados e interpretação

Os resultados registrados no README representam uma execução de referência sob essas hipóteses. A acurácia de 100% da MLP, por exemplo, refere-se exclusivamente a um conjunto de teste sintético derivado das mesmas distribuições artificiais usadas no experimento. Ela não comprova capacidade de detectar falhas em equipamentos reais.

Da mesma forma, o custo da frota, o gargalo da simulação e a saída dos controladores fuzzy dependem diretamente dos parâmetros escolhidos. Alterações nos custos, capacidades, distribuição das chegadas, funções de pertinência ou regras podem modificar os resultados.

## Limitações e requisitos antes de qualquer uso real

Os protótipos não devem ser utilizados para decisões operacionais sem, no mínimo:

- coleta e validação de dados reais de obra e equipamentos;
- calibração dos parâmetros e avaliação por especialistas de cada domínio;
- análise de sensibilidade e validação independente dos resultados;
- tratamento de incerteza, variabilidade operacional e eventos não modelados;
- avaliação de segurança, riscos, rastreabilidade e requisitos regulatórios aplicáveis.

O escopo atual é educacional e exploratório: demonstrar técnicas de computação aplicadas a problemas inspirados no planejamento de obras.
