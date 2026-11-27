"""Roteamento em malha com A* e alocação de frota por programação linear inteira.

A etapa combina dois problemas clássicos de Pesquisa Operacional:
1. encontrar um caminho de menor custo em uma malha com obstáculos;
2. selecionar a composição de uma frota que atende à demanda com menor custo.

Os valores de frota são hipóteses sintéticas de demonstração, não cotações reais.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import networkx as nx


# Configuração da malha ortogonal usada no cenário demonstrativo.
TAMANHO = 8
OBSTACULOS = {(3, 3), (3, 4)}
ORIGEM = (0, 0)
DESTINO = (7, 7)


def distancia_manhattan(
    a: tuple[int, int],
    b: tuple[int, int],
) -> int:
    """Calcula a distância Manhattan entre duas células da malha.

    Como o movimento permitido é ortogonal, a heurística soma os
    deslocamentos horizontal e vertical. Com arestas de custo unitário,
    ela é admissível para o A*.
    """
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def construir_grafo(
    tamanho: int = TAMANHO,
    obstaculos: Iterable[tuple[int, int]] = OBSTACULOS,
) -> nx.Graph:
    """Cria um grafo não direcionado representando uma malha quadrada.

    Cada célula livre é um nó. Arestas conectam apenas vizinhos
    horizontais e verticais, com custo igual a uma unidade.
    """
    bloqueados = set(obstaculos)

    # Valida as dimensões e impede obstáculos fora da área representada.
    if tamanho < 2:
        raise ValueError("A malha deve ter pelo menos 2 x 2 células.")
    if any(not (0 <= x < tamanho and 0 <= y < tamanho) for x, y in bloqueados):
        raise ValueError("Há obstáculo fora dos limites da malha.")

    grafo = nx.Graph()

    # Nós são adicionados somente para as células que não estão bloqueadas.
    nos = [
        (x, y)
        for x in range(tamanho)
        for y in range(tamanho)
        if (x, y) not in bloqueados
    ]
    grafo.add_nodes_from(nos)

    # Cada célula é conectada aos quatro vizinhos ortogonais que estiverem livres.
    for x, y in nos:
        vizinhos = ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1))
        for vizinho in vizinhos:
            if vizinho in grafo:
                grafo.add_edge((x, y), vizinho, weight=1)

    return grafo


def calcular_rota(
    origem: tuple[int, int] = ORIGEM,
    destino: tuple[int, int] = DESTINO,
):
    """Executa A* e retorna o grafo, o caminho encontrado e sua distância."""
    grafo = construir_grafo()

    # A busca só pode começar e terminar em células existentes no grafo.
    if origem not in grafo or destino not in grafo:
        raise ValueError("Origem e destino devem estar livres e dentro da malha.")

    # A heurística Manhattan estima o custo restante sem superestimar a rota.
    caminho = nx.astar_path(
        grafo,
        origem,
        destino,
        heuristic=distancia_manhattan,
        weight="weight",
    )
    distancia = nx.path_weight(grafo, caminho, weight="weight")

    return {"graph": grafo, "path": caminho, "distance": distancia}


@dataclass(frozen=True)
class TipoCarregadeira:
    """Parâmetros de um tipo de mini-carregadeira no cenário sintético."""

    capacidade_t_dia: int
    custo_dia_brl: float
    disponibilidade: int


# Hipóteses didáticas: capacidade, custo e disponibilidade não são dados reais.
FROTA = {
    "A": TipoCarregadeira(150, 900.0, 2),
    "B": TipoCarregadeira(100, 700.0, 3),
    "C": TipoCarregadeira(75, 550.0, 3),
}


def otimizar_frota(demanda_minima_t: int = 450):
    """Minimiza o custo diário da frota respeitando a demanda mínima.

    As variáveis de decisão representam quantas unidades de cada tipo
    serão alocadas. Elas são inteiras, não negativas e limitadas pela
    disponibilidade informada em FROTA.
    """
    try:
        import pulp
    except ImportError as exc:
        raise RuntimeError("Instale as dependências de requirements.txt.") from exc

    problema = pulp.LpProblem(
        "Alocacao_de_Mini_Carregadeiras",
        pulp.LpMinimize,
    )

    # Uma variável inteira é criada para cada categoria de equipamento.
    unidades = {
        chave: pulp.LpVariable(
            f"unidades_{chave}",
            lowBound=0,
            upBound=tipo.disponibilidade,
            cat=pulp.LpInteger,
        )
        for chave, tipo in FROTA.items()
    }

    # Função objetivo: minimizar o custo diário total de operação.
    problema += pulp.lpSum(
        unidades[chave] * FROTA[chave].custo_dia_brl
        for chave in FROTA
    )

    # Restrição: a capacidade somada da frota precisa cobrir a demanda.
    problema += pulp.lpSum(
        unidades[chave] * FROTA[chave].capacidade_t_dia
        for chave in FROTA
    ) >= demanda_minima_t

    # CBC resolve o modelo de programação linear inteira.
    status = problema.solve(pulp.PULP_CBC_CMD(msg=False))
    if pulp.LpStatus[status] != "Optimal":
        raise RuntimeError(f"Solução não ótima: {pulp.LpStatus[status]}")

    alocacao = {
        chave: int(round(unidades[chave].value() or 0))
        for chave in FROTA
    }
    capacidade = sum(
        alocacao[chave] * FROTA[chave].capacidade_t_dia
        for chave in FROTA
    )

    return {
        "status": pulp.LpStatus[status],
        "allocation": alocacao,
        "capacity_t_day": capacidade,
        "demand_min_t_day": demanda_minima_t,
        "cost_brl_day": float(pulp.value(problema.objective)),
    }
