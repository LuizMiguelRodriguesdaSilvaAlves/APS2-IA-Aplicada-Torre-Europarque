# Resultados e artefatos gerados

Os artefatos completos são produzidos localmente pelo executor integrado:

~~~bash
python -m src.gerar_resultados
~~~

Após a execução, esta pasta recebe:

| Arquivo | Conteúdo |
| --- | --- |
| etapa1_rota_astar.png | Grafo da malha com caminho A* e obstáculos destacados |
| etapa2_tempos_servico.png | Comparação dos tempos de serviço M1 e M2 |
| grafo_torre_europarque.ttl | Grafo RDF serializado no formato Turtle |
| etapa4_perda_mlp.png | Histórico da perda durante o treinamento da MLP |
| etapa5_superficie_mamdani.png | Superfície de resposta do controlador Mamdani |
| etapa5_superficie_sugeno.png | Superfície de resposta do controlador Sugeno |
| resultados_execucao.json | Métricas consolidadas das cinco etapas |

Os arquivos acima são saídas locais e são ignorados pelo Git por padrão, pois podem ser regenerados. O arquivo <code>validacao_parcial.json</code> é mantido como registro histórico de uma validação local parcial; ele não substitui o JSON gerado por uma execução completa.

Todos os resultados dependem de dados e parâmetros sintéticos. Consulte a documentação de premissas antes de interpretar os números.
