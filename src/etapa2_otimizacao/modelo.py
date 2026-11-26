"""Etapa 2: algoritmo genetico para rota e simulacao discreta da concretagem."""
from __future__ import annotations
import math, random
from itertools import permutations

DEPOSITO = (0.0,0.0)
BLOCOS = {
 "Bloco 1":{"coordenada":(2.0,1.0),"demanda_t":18.0},
 "Bloco 2":{"coordenada":(4.0,2.0),"demanda_t":22.0},
 "Bloco 3":{"coordenada":(6.0,1.0),"demanda_t":15.0},
 "Bloco 4":{"coordenada":(1.0,5.0),"demanda_t":20.0},
 "Bloco 5":{"coordenada":(4.0,5.0),"demanda_t":17.0},
 "Bloco 6":{"coordenada":(7.0,6.0),"demanda_t":16.0},
}
CAPACIDADE_CAMINHAO_T=120.0

def distancia(a,b): return math.dist(a,b)

def avaliar_percurso(ordem,blocos=BLOCOS,deposito=DEPOSITO,capacidade=CAPACIDADE_CAMINHAO_T,penalidade_por_tonelada=10000.0):
    nomes=list(blocos)
    if sorted(ordem)!=sorted(nomes):
        raise ValueError("A rota deve conter cada bloco exatamente uma vez.")
    pontos=[deposito]+[blocos[n]["coordenada"] for n in ordem]+[deposito]
    km=sum(distancia(a,b) for a,b in zip(pontos,pontos[1:]))
    carga=sum(blocos[n]["demanda_t"] for n in ordem)
    excesso=max(0.0,carga-capacidade)
    return km+excesso*penalidade_por_tonelada,km,carga,excesso

def melhor_rota_exaustiva():
    melhor=None
    for ordem in permutations(BLOCOS):
        v=avaliar_percurso(ordem)
        candidato=(v[0],tuple(ordem),v[1],v[2],v[3])
        if melhor is None or candidato<melhor: melhor=candidato
    return {"fitness":melhor[0],"route":list(melhor[1]),"distance_units":melhor[2],
            "load_t":melhor[3],"overload_t":melhor[4],"permutations_checked":720}

def otimizar_rota(seed=42,populacao=100,geracoes=120):
    try:
        from deap import base,creator,tools,algorithms
    except ImportError as exc:
        raise RuntimeError("Instale as dependencias de requirements.txt.") from exc
    nomes=list(BLOCOS)
    if not hasattr(creator,"FitnessMinAPS2"): creator.create("FitnessMinAPS2",base.Fitness,weights=(-1.0,))
    if not hasattr(creator,"IndividualAPS2"): creator.create("IndividualAPS2",list,fitness=creator.FitnessMinAPS2)
    random.seed(seed)
    toolbox=base.Toolbox()
    toolbox.register("indices",random.sample,range(len(nomes)),len(nomes))
    toolbox.register("individual",tools.initIterate,creator.IndividualAPS2,toolbox.indices)
    toolbox.register("population",tools.initRepeat,list,toolbox.individual)
    toolbox.register("evaluate",lambda ind:(avaliar_percurso([nomes[i] for i in ind])[0],))
    toolbox.register("mate",tools.cxOrdered)
    toolbox.register("mutate",tools.mutShuffleIndexes,indpb=0.2)
    toolbox.register("select",tools.selTournament,tournsize=3)
    pop=toolbox.population(n=populacao); hall=tools.HallOfFame(1)
    algorithms.eaSimple(pop,toolbox,cxpb=0.75,mutpb=0.25,ngen=geracoes,stats=None,halloffame=hall,verbose=False)
    rota=[nomes[i] for i in hall[0]]
    fit,km,carga,excesso=avaliar_percurso(rota)
    return {"route":rota,"distance_units":km,"load_t":carga,"capacity_t":CAPACIDADE_CAMINHAO_T,
            "overload_t":excesso,"fitness":fit,"seed":seed,"population":populacao,"generations":geracoes}

def simular_concretagem(duracao_min=300,intervalo_chegada_min=4,tempo_m1_min=5,tempo_m2_min=7):
    try: import simpy
    except ImportError as exc: raise RuntimeError("Instale as dependencias de requirements.txt.") from exc
    env=simpy.Environment()
    m1,m2=simpy.Resource(env,capacity=1),simpy.Resource(env,capacity=1)
    concluidas,esperas,inicios=[],[],[]
    def lote(numero):
        espera_total=0.0; solicitacao=env.now
        with m1.request() as req:
            yield req
            espera_total += env.now-solicitacao
            inicio_m1=env.now; yield env.timeout(tempo_m1_min); fim_m1=env.now
        solicitacao=env.now
        with m2.request() as req:
            yield req
            espera_total += env.now-solicitacao
            inicio_m2=env.now; yield env.timeout(tempo_m2_min); fim=env.now
        concluidas.append({"lote":numero,"inicio_m1_min":inicio_m1,"fim_m1_min":fim_m1,
                           "inicio_m2_min":inicio_m2,"fim_min":fim,"espera_fila_min":espera_total})
        esperas.append(espera_total)
    def chegadas():
        numero=0
        while True:
            env.process(lote(numero)); inicios.append(env.now); numero+=1
            yield env.timeout(intervalo_chegada_min)
    env.process(chegadas()); env.run(until=duracao_min)
    return {"duration_min":duracao_min,"arrivals":len(inicios),"loads_processed":len(concluidas),
            "average_queue_wait_min":sum(esperas)/len(esperas) if esperas else 0.0,
            "bottleneck":"Bomba M2" if tempo_m2_min>=tempo_m1_min else "Betoneira M1",
            "m1_theoretical_load_ratio":tempo_m1_min/intervalo_chegada_min,
            "m2_theoretical_load_ratio":tempo_m2_min/intervalo_chegada_min,"completed":concluidas}
