"""Otimização de entregas com algoritmo genético e simulação de eventos discretos.

A etapa compara uma rota produzida por algoritmo genético com um benchmark
exaustivo e modela o fluxo de lotes por dois recursos sequenciais de obra.
As coordenadas, demandas e parâmetros de chegada são sintéticos.
"""
from __future__ import annotations

import math
import random
from itertools import permutations

# Posição do depósito e dados demonstrativos dos seis blocos de destino.
DEPOSITO = (0.0, 0.0)
BLOCOS = {
    "Bloco 1": {"coordenada": (2.0, 1.0), "demanda_t": 18.0},
    "Bloco 2": {"coordenada": (4.0, 2.0), "demanda_t": 22.0},
    "Bloco 3": {"coordenada": (6.0, 1.0), "demanda_t": 15.0},
    "Bloco 4": {"coordenada": (1.0, 5.0), "demanda_t": 20.0},
    "Bloco 5": {"coordenada": (4.0, 5.0), "demanda_t": 17.0},
    "Bloco 6": {"coordenada": (7.0, 6.0), "demanda_t": 16.0},
}
CAPACIDADE_CAMINHAO_T = 120.0


def distancia(a, b):
    """Calcula a distância euclidiana entre dois pontos do plano."""
    return math.dist(a, b)


def avaliar_percurso(
    ordem,
    blocos=BLOCOS,
    deposito=DEPOSITO,
    capacidade=CAPACIDADE_CAMINHAO_T,
    penalidade_por_tonelada=10000.0,
):
    """Avalia uma rota fechada, incluindo o depósito no início e no fim.

    O fitness é a distância percorrida acrescida de uma penalidade elevada
    para qualquer carga acima da capacidade do caminhão. A função retorna
    também as métricas separadas para facilitar a análise dos resultados.
    """
    nomes = list(blocos)

    # Impede rotas com blocos ausentes, repetidos ou não reconhecidos.
    if sorted(ordem) != sorted(nomes):
        raise ValueError("A rota deve conter cada bloco exatamente uma vez.")

    pontos = [deposito] + [blocos[nome]["coordenada"] for nome in ordem] + [deposito]

    # Soma os segmentos consecutivos da rota, do depósito aos blocos e de volta.
    km = sum(
        distancia(ponto_a, ponto_b)
        for ponto_a, ponto_b in zip(pontos, pontos[1:])
    )

    carga = sum(blocos[nome]["demanda_t"] for nome in ordem)
    excesso = max(0.0, carga - capacidade)
    fitness = km + excesso * penalidade_por_tonelada

    return fitness, km, carga, excesso


def melhor_rota_exaustiva():
    """Calcula o melhor percurso verificando todas as permutações possíveis.

    Para seis blocos existem 6! = 720 ordens. Esse método é viável neste
    cenário pequeno e serve como referência exata para comparar o DEAP.
    """
    melhor = None

    for ordem in permutations(BLOCOS):
        avaliacao = avaliar_percurso(ordem)
        candidato = (
            avaliacao[0],
            tuple(ordem),
            avaliacao[1],
            avaliacao[2],
            avaliacao[3],
        )

        # O primeiro campo do tuplo é o fitness; os demais desempatarão
        # de forma determinística caso duas soluções tenham o mesmo valor.
        if melhor is None or candidato < melhor:
            melhor = candidato

    return {
        "fitness": melhor[0],
        "route": list(melhor[1]),
        "distance_units": melhor[2],
        "load_t": melhor[3],
        "overload_t": melhor[4],
        "permutations_checked": 720,
    }


def otimizar_rota(seed=42, populacao=100, geracoes=120):
    """Procura uma ordem de visita usando os operadores genéticos do DEAP.

    O cromossomo é uma permutação dos índices dos blocos. A seleção por
    torneio, o cruzamento ordenado e a mutação por embaralhamento preservam
    uma representação válida de rota.
    """
    try:
        from deap import algorithms, base, creator, tools
    except ImportError as exc:
        raise RuntimeError("Instale as dependências de requirements.txt.") from exc

    nomes = list(BLOCOS)

    # O DEAP registra classes no objeto global creator. A verificação
    # evita tentar recriá-las quando a função é executada mais de uma vez.
    if not hasattr(creator, "FitnessMinAPS2"):
        creator.create("FitnessMinAPS2", base.Fitness, weights=(-1.0,))
    if not hasattr(creator, "IndividualAPS2"):
        creator.create(
            "IndividualAPS2",
            list,
            fitness=creator.FitnessMinAPS2,
        )

    random.seed(seed)
    toolbox = base.Toolbox()

    # Cada indivíduo começa como uma permutação aleatória dos blocos.
    toolbox.register(
        "indices",
        random.sample,
        range(len(nomes)),
        len(nomes),
    )
    toolbox.register(
        "individual",
        tools.initIterate,
        creator.IndividualAPS2,
        toolbox.indices,
    )
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)

    # Traduz os índices do cromossomo para nomes e utiliza a função de fitness.
    toolbox.register(
        "evaluate",
        lambda individuo: (
            avaliar_percurso([nomes[i] for i in individuo])[0],
        ),
    )

    # Operadores genéticos adequados a cromossomos representados por permutações.
    toolbox.register("mate", tools.cxOrdered)
    toolbox.register("mutate", tools.mutShuffleIndexes, indpb=0.2)
    toolbox.register("select", tools.selTournament, tournsize=3)

    populacao_inicial = toolbox.population(n=populacao)
    melhores = tools.HallOfFame(1)

    # eaSimple executa seleção, cruzamento, mutação e avaliação por geração.
    algorithms.eaSimple(
        populacao_inicial,
        toolbox,
        cxpb=0.75,
        mutpb=0.25,
        ngen=geracoes,
        stats=None,
        halloffame=melhores,
        verbose=False,
    )

    rota = [nomes[i] for i in melhores[0]]
    fitness, km, carga, excesso = avaliar_percurso(rota)

    return {
        "route": rota,
        "distance_units": km,
        "load_t": carga,
        "capacity_t": CAPACIDADE_CAMINHAO_T,
        "overload_t": excesso,
        "fitness": fitness,
        "seed": seed,
        "population": populacao,
        "generations": geracoes,
    }


def simular_concretagem(
    duracao_min=300,
    intervalo_chegada_min=4,
    tempo_m1_min=5,
    tempo_m2_min=7,
):
    """Simula chegadas de lotes e atendimento por dois recursos em série.

    M1 representa a primeira operação e M2 a segunda. Cada recurso possui
    capacidade igual a um, de modo que apenas um lote pode ocupá-lo por vez.
    O tempo de fila é acumulado nos dois pontos de atendimento.
    """
    try:
        import simpy
    except ImportError as exc:
        raise RuntimeError("Instale as dependências de requirements.txt.") from exc

    env = simpy.Environment()
    m1 = simpy.Resource(env, capacity=1)
    m2 = simpy.Resource(env, capacity=1)

    concluidas, esperas, inicios = [], [], []

    def lote(numero):
        """Representa o ciclo de um único lote ao longo dos dois recursos."""
        espera_total = 0.0
        solicitacao = env.now

        # Primeira etapa do processo: aguardar e utilizar o recurso M1.
        with m1.request() as requisicao:
            yield requisicao
            espera_total += env.now - solicitacao
            inicio_m1 = env.now
            yield env.timeout(tempo_m1_min)
            fim_m1 = env.now

        # Segunda etapa: após M1, o lote solicita o recurso M2.
        solicitacao = env.now
        with m2.request() as requisicao:
            yield requisicao
            espera_total += env.now - solicitacao
            inicio_m2 = env.now
            yield env.timeout(tempo_m2_min)
            fim = env.now

        concluidas.append({
            "lote": numero,
            "inicio_m1_min": inicio_m1,
            "fim_m1_min": fim_m1,
            "inicio_m2_min": inicio_m2,
            "fim_min": fim,
            "espera_fila_min": espera_total,
        })
        esperas.append(espera_total)

    def chegadas():
        """Gera um novo processo de lote em intervalos regulares."""
        numero = 0
        while True:
            env.process(lote(numero))
            inicios.append(env.now)
            numero += 1
            yield env.timeout(intervalo_chegada_min)

    # Inicia o fluxo de chegadas e avança o relógio até o horizonte definido.
    env.process(chegadas())
    env.run(until=duracao_min)

    # O recurso com maior tempo de serviço tende a limitar a vazão do sistema.
    gargalo = "Bomba M2" if tempo_m2_min >= tempo_m1_min else "Betoneira M1"

    return {
        "duration_min": duracao_min,
        "arrivals": len(inicios),
        "loads_processed": len(concluidas),
        "average_queue_wait_min": sum(esperas) / len(esperas) if esperas else 0.0,
        "bottleneck": gargalo,
        "m1_theoretical_load_ratio": tempo_m1_min / intervalo_chegada_min,
        "m2_theoretical_load_ratio": tempo_m2_min / intervalo_chegada_min,
        "completed": concluidas,
    }
