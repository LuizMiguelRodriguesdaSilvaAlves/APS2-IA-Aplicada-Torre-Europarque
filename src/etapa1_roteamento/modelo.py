"""Etapa 1: roteamento A* e alocacao linear de mini-carregadeiras."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable
import networkx as nx

TAMANHO = 8
OBSTACULOS = {(3, 3), (3, 4)}
ORIGEM = (0, 0)
DESTINO = (7, 7)

def distancia_manhattan(a: tuple[int, int], b: tuple[int, int]) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def construir_grafo(tamanho: int = TAMANHO, obstaculos: Iterable[tuple[int, int]] = OBSTACULOS) -> nx.Graph:
    bloqueados = set(obstaculos)
    if tamanho < 2:
        raise ValueError("A malha deve ter pelo menos 2 x 2 celulas.")
    if any(not (0 <= x < tamanho and 0 <= y < tamanho) for x, y in bloqueados):
        raise ValueError("Ha obstaculo fora dos limites da malha.")
    grafo = nx.Graph()
    nos = [(x, y) for x in range(tamanho) for y in range(tamanho) if (x, y) not in bloqueados]
    grafo.add_nodes_from(nos)
    for x, y in nos:
        for vizinho in ((x+1,y),(x-1,y),(x,y+1),(x,y-1)):
            if vizinho in grafo:
                grafo.add_edge((x,y), vizinho, weight=1)
    return grafo

def calcular_rota(origem: tuple[int,int] = ORIGEM, destino: tuple[int,int] = DESTINO):
    grafo = construir_grafo()
    if origem not in grafo or destino not in grafo:
        raise ValueError("Origem e destino devem estar livres e dentro da malha.")
    caminho = nx.astar_path(grafo, origem, destino, heuristic=distancia_manhattan, weight="weight")
    return {"graph":grafo,"path":caminho,"distance":nx.path_weight(grafo,caminho,weight="weight")}

@dataclass(frozen=True)
class TipoCarregadeira:
    capacidade_t_dia: int
    custo_dia_brl: float
    disponibilidade: int

# Hipoteses didaticas; substituir por dados reais quando disponiveis.
FROTA = {
    "A": TipoCarregadeira(150,900.0,2),
    "B": TipoCarregadeira(100,700.0,3),
    "C": TipoCarregadeira(75,550.0,3),
}

def otimizar_frota(demanda_minima_t: int = 450):
    try:
        import pulp
    except ImportError as exc:
        raise RuntimeError("Instale as dependencias de requirements.txt.") from exc
    problema = pulp.LpProblem("Alocacao_de_Mini_Carregadeiras",pulp.LpMinimize)
    unidades = {k:pulp.LpVariable(f"unidades_{k}",lowBound=0,upBound=v.disponibilidade,cat=pulp.LpInteger) for k,v in FROTA.items()}
    problema += pulp.lpSum(unidades[k]*FROTA[k].custo_dia_brl for k in FROTA)
    problema += pulp.lpSum(unidades[k]*FROTA[k].capacidade_t_dia for k in FROTA) >= demanda_minima_t
    status = problema.solve(pulp.PULP_CBC_CMD(msg=False))
    if pulp.LpStatus[status] != "Optimal":
        raise RuntimeError(f"Solucao nao otima: {pulp.LpStatus[status]}")
    alocacao = {k:int(round(unidades[k].value() or 0)) for k in FROTA}
    capacidade = sum(alocacao[k]*FROTA[k].capacidade_t_dia for k in FROTA)
    return {"status":pulp.LpStatus[status],"allocation":alocacao,
            "capacity_t_day":capacidade,"demand_min_t_day":demanda_minima_t,
            "cost_brl_day":float(pulp.value(problema.objective))}
