"""Executa as cinco etapas e salva resultados e figuras."""
from __future__ import annotations
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import networkx as nx

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"resultados"
OUT.mkdir(exist_ok=True)

def main():
    dados={}
    from src.etapa1_roteamento.modelo import calcular_rota,otimizar_frota
    r=calcular_rota(); frota=otimizar_frota()
    dados["etapa1"]={"astar":{"distance":r["distance"],"path":r["path"]},"pulp":frota}
    pos={n:n for n in r["graph"].nodes}
    fig,ax=plt.subplots(figsize=(7,6))
    nx.draw_networkx(r["graph"],pos=pos,node_size=90,with_labels=False,node_color="#dbeafe",edge_color="#cbd5e1",ax=ax)
    nx.draw_networkx_nodes(r["graph"],pos,nodelist=r["path"],node_color="#16a34a",node_size=120,ax=ax)
    ax.scatter([3,3],[3,4],marker="s",s=150,color="#dc2626",label="Obstaculos")
    ax.set_title("A* na malha 8 x 8"); ax.set_aspect("equal"); ax.grid(True,alpha=.2); ax.legend()
    fig.tight_layout(); fig.savefig(OUT/"etapa1_rota_astar.png",dpi=160); plt.close(fig)

    from src.etapa2_otimizacao.modelo import otimizar_rota,melhor_rota_exaustiva,simular_concretagem
    ga=otimizar_rota(); benchmark=melhor_rota_exaustiva(); sim=simular_concretagem()
    dados["etapa2"]={"deap":ga,"benchmark_exato":benchmark,
                     "simpy":{k:v for k,v in sim.items() if k!="completed"}}
    fig,ax=plt.subplots(figsize=(7,4)); ax.bar(["M1 - preparo","M2 - bombeamento"],[5,7])
    ax.set_ylabel("Tempo medio por carga (min)"); ax.set_title("Tempos de servico"); fig.tight_layout()
    fig.savefig(OUT/"etapa2_tempos_servico.png",dpi=160); plt.close(fig)

    from src.etapa3_conhecimento.modelo import construir_grafo,consultar_fornecedores
    g=construir_grafo(); consulta=consultar_fornecedores(g)
    dados["etapa3"]={"triples":len(g),"suppliers_high_resistance":consulta}
    # O grafo e exportado em Turtle; o notebook exibe os pares da consulta SPARQL.
    (OUT/"grafo_torre_europarque.ttl").write_text(g.serialize(format="turtle"),encoding="utf-8")

    from src.etapa4_rede_neural.modelo import treinar_mlp,lote_teste_exemplo,diagnosticar
    model=treinar_mlp(); X,y=lote_teste_exemplo(); diag=diagnosticar(X,model)
    dados["etapa4"]={"accuracy_holdout_synthetic":model["accuracy"],
                     "final_training_loss":model["loss_history"][-1],"diagnoses":diag}
    fig,ax=plt.subplots(figsize=(8,4)); ax.plot(model["loss_history"])
    ax.set_xlabel("Epocas"); ax.set_ylabel("Cross-entropy"); ax.set_title("Perda de treinamento MLP")
    fig.tight_layout(); fig.savefig(OUT/"etapa4_perda_mlp.png",dpi=160); plt.close(fig)

    from src.etapa5_fuzzy.modelo import calcular_mamdani,calcular_sugeno,superficie_resposta
    mam=calcular_mamdani(34,30); sug=calcular_sugeno(34,30)
    ts,us,zm,zs=superficie_resposta()
    dados["etapa5"]={"temperature_c":34,"humidity_pct":30,
                     "mamdani_centroid_pct":mam,"sugeno_weighted_pct":sug}
    T,U=np.meshgrid(ts,us,indexing="ij")
    for nome,Z in [("mamdani",zm),("sugeno",zs)]:
        fig=plt.figure(figsize=(8,6)); ax=fig.add_subplot(111,projection="3d")
        surf=ax.plot_surface(T,U,Z,cmap="viridis",linewidth=0,antialiased=True)
        ax.set_xlabel("Temperatura (C)"); ax.set_ylabel("Umidade relativa (%)")
        ax.set_zlabel("Taxa de aditivo (%)"); ax.set_title(f"Superficie Fuzzy - {nome.title()}")
        fig.colorbar(surf,shrink=.6); fig.tight_layout()
        fig.savefig(OUT/f"etapa5_superficie_{nome}.png",dpi=160); plt.close(fig)

    (OUT/"resultados_execucao.json").write_text(json.dumps(dados,ensure_ascii=False,indent=2,default=str),encoding="utf-8")
    print(json.dumps(dados,ensure_ascii=False,indent=2,default=str))

if __name__=="__main__": main()
