"""Executa as cinco etapas e salva métricas, dados e visualizações.

Uso na raiz do repositório:
    python -m src.gerar_resultados

Os arquivos gerados são gravados em resultados/. Como os cenários usam
parâmetros sintéticos, as saídas servem para reprodução e análise didática.
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib

# Seleciona backend sem interface gráfica para permitir execução em CI/servidor.
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "resultados"
OUT.mkdir(exist_ok=True)


def main():
    """Orquestra os módulos em sequência e consolida os resultados em JSON."""
    dados = {}

    # Etapa 1: busca A* e otimização da composição da frota com PuLP.
    from src.etapa1_roteamento.modelo import calcular_rota, otimizar_frota

    rota_astar = calcular_rota()
    frota = otimizar_frota()
    dados["etapa1"] = {
        "astar": {
            "distance": rota_astar["distance"],
            "path": rota_astar["path"],
        },
        "pulp": frota,
    }

    # Desenha todos os nós e destaca o caminho retornado pelo A*.
    posicoes = {no: no for no in rota_astar["graph"].nodes}
    figura, eixo = plt.subplots(figsize=(7, 6))
    nx.draw_networkx(
        rota_astar["graph"],
        pos=posicoes,
        node_size=90,
        with_labels=False,
        node_color="#dbeafe",
        edge_color="#cbd5e1",
        ax=eixo,
    )
    nx.draw_networkx_nodes(
        rota_astar["graph"],
        posicoes,
        nodelist=rota_astar["path"],
        node_color="#16a34a",
        node_size=120,
        ax=eixo,
    )
    eixo.scatter(
        [3, 3],
        [3, 4],
        marker="s",
        s=150,
        color="#dc2626",
        label="Obstáculos",
    )
    eixo.set_title("A* na malha 8 x 8")
    eixo.set_aspect("equal")
    eixo.grid(True, alpha=0.2)
    eixo.legend()
    figura.tight_layout()
    figura.savefig(OUT / "etapa1_rota_astar.png", dpi=160)
    plt.close(figura)

    # Etapa 2: busca genética, benchmark exato e simulação SimPy.
    from src.etapa2_otimizacao.modelo import (
        melhor_rota_exaustiva,
        otimizar_rota,
        simular_concretagem,
    )

    resultado_genetico = otimizar_rota()
    benchmark = melhor_rota_exaustiva()
    simulacao = simular_concretagem()

    # Os detalhes individuais dos lotes ficam na simulação; o JSON principal
    # registra as métricas agregadas para manter o arquivo mais compacto.
    dados["etapa2"] = {
        "deap": resultado_genetico,
        "benchmark_exato": benchmark,
        "simpy": {
            chave: valor
            for chave, valor in simulacao.items()
            if chave != "completed"
        },
    }

    figura, eixo = plt.subplots(figsize=(7, 4))
    eixo.bar(
        ["M1 - preparo", "M2 - bombeamento"],
        [5, 7],
    )
    eixo.set_ylabel("Tempo médio por carga (min)")
    eixo.set_title("Tempos de serviço")
    figura.tight_layout()
    figura.savefig(OUT / "etapa2_tempos_servico.png", dpi=160)
    plt.close(figura)

    # Etapa 3: construção do grafo RDF e consulta SPARQL.
    from src.etapa3_conhecimento.modelo import (
        construir_grafo,
        consultar_fornecedores,
    )

    grafo = construir_grafo()
    consulta = consultar_fornecedores(grafo)
    dados["etapa3"] = {
        "triples": len(grafo),
        "suppliers_high_resistance": consulta,
    }

    # Exporta o conhecimento como Turtle para inspeção em ferramentas RDF.
    (OUT / "grafo_torre_europarque.ttl").write_text(
        grafo.serialize(format="turtle"),
        encoding="utf-8",
    )

    # Etapa 4: treinamento e inferência da MLP com telemetria sintética.
    from src.etapa4_rede_neural.modelo import (
        diagnosticar,
        lote_teste_exemplo,
        treinar_mlp,
    )

    modelo = treinar_mlp()
    X_exemplo, _ = lote_teste_exemplo()
    diagnosticos = diagnosticar(X_exemplo, modelo)
    dados["etapa4"] = {
        "accuracy_holdout_synthetic": modelo["accuracy"],
        "final_training_loss": modelo["loss_history"][-1],
        "diagnoses": diagnosticos,
    }

    figura, eixo = plt.subplots(figsize=(8, 4))
    eixo.plot(modelo["loss_history"])
    eixo.set_xlabel("Épocas")
    eixo.set_ylabel("Cross-entropy")
    eixo.set_title("Perda de treinamento MLP")
    figura.tight_layout()
    figura.savefig(OUT / "etapa4_perda_mlp.png", dpi=160)
    plt.close(figura)

    # Etapa 5: cálculo de um ponto de referência e superfícies dos controladores.
    from src.etapa5_fuzzy.modelo import (
        calcular_mamdani,
        calcular_sugeno,
        superficie_resposta,
    )

    mamdani = calcular_mamdani(34, 30)
    sugeno = calcular_sugeno(34, 30)
    temperaturas, umidades, matriz_mamdani, matriz_sugeno = superficie_resposta()

    dados["etapa5"] = {
        "temperature_c": 34,
        "humidity_pct": 30,
        "mamdani_centroid_pct": mamdani,
        "sugeno_weighted_pct": sugeno,
    }

    # Prepara a grade de coordenadas e exporta um gráfico 3D para cada método.
    T, U = np.meshgrid(temperaturas, umidades, indexing="ij")
    superficies = [
        ("mamdani", matriz_mamdani),
        ("sugeno", matriz_sugeno),
    ]

    for nome, matriz in superficies:
        figura = plt.figure(figsize=(8, 6))
        eixo = figura.add_subplot(111, projection="3d")
        superficie = eixo.plot_surface(
            T,
            U,
            matriz,
            cmap="viridis",
            linewidth=0,
            antialiased=True,
        )
        eixo.set_xlabel("Temperatura (°C)")
        eixo.set_ylabel("Umidade relativa (%)")
        eixo.set_zlabel("Taxa de aditivo (%)")
        eixo.set_title(f"Superfície Fuzzy - {nome.title()}")
        figura.colorbar(superficie, shrink=0.6)
        figura.tight_layout()
        figura.savefig(
            OUT / f"etapa5_superficie_{nome}.png",
            dpi=160,
        )
        plt.close(figura)

    # Salva todas as métricas em um arquivo legível por máquina e imprime
    # o mesmo conteúdo no terminal para facilitar a inspeção após a execução.
    arquivo_json = OUT / "resultados_execucao.json"
    arquivo_json.write_text(
        json.dumps(dados, ensure_ascii=False, indent=2, default=str),
        encoding="utf-8",
    )
    print(json.dumps(dados, ensure_ascii=False, indent=2, default=str))


if __name__ == "__main__":
    main()
