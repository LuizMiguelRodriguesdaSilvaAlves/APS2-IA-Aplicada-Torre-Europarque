# Decisoes tecnicas e premissas declaradas

## Dados fornecidos no enunciado
- Malha ortogonal 8x8; obstaculos (3,3) e (3,4).
- A* de (0,0) a (7,7), heuristica Manhattan.
- Demanda minima de 450 t/dia para a frota.
- Seis blocos; capacidade maxima do caminhao: 120 t.
- Concretagem em serie: M1 = 5 min, M2 = 7 min; horizonte = 300 min.
- RDF com projeto, Concreto FCK 30, Aco CA-50, Argamassa e fornecedores homologados.
- MLP com dez variaveis e tres classes.
- Fuzzy com temperatura 0-50 C, umidade 0-100%, saida 0-100%, quatro regras e condicao 34 C / 30%.

## Hipoteses sinteticas
1. Frota: A = 150 t/dia e R$ 900/dia (ate 2); B = 100 t/dia e R$ 700/dia (ate 3); C = 75 t/dia e R$ 550/dia (ate 3).
2. Blocos: demandas [18,22,15,20,17,16] t, total 108 t; coordenadas estao no modulo da Etapa 2.
3. SimPy: chegada a cada 4 min, uma unidade de cada recurso.
4. RDF: fornecedores ficticios; classificacao de resistencia demonstrativa, sem consulta real a SINAPI/CUB.
5. MLP: telemetria e rotulos gerados artificialmente por classe.
6. Fuzzy: termos triangulares e regras projetados para demonstracao; nao sao recomendacao de dosagem.

## Limites
Os prototipos nao devem ser usados em producao sem dados reais, calibracao, validacao e avaliacao de risco. A acuracia da MLP sintetica nao generaliza a sensores reais. O modelo LP depende dos custos e capacidades hipoteticos. A simulacao nao inclui variabilidade operacional nem manutencao.