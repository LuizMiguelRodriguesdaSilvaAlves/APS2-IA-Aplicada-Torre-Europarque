import pytest
from src.etapa1_roteamento.modelo import calcular_rota, construir_grafo, distancia_manhattan
from src.etapa3_conhecimento.modelo import construir_grafo as construir_rdf, consultar_fornecedores
from src.etapa4_rede_neural.modelo import treinar_mlp, lote_teste_exemplo, diagnosticar

def test_astar_respeita_obstaculos_e_heuristica():
    res=calcular_rota()
    assert res["distance"]==14
    assert (3,3) not in res["path"] and (3,4) not in res["path"]
    assert res["path"][0]==(0,0) and res["path"][-1]==(7,7)
    assert distancia_manhattan((0,0),(7,7))==14
    assert (3,3) not in construir_grafo()

def test_rdf_sparql_retorna_apenas_insumos_alta_resistencia():
    g=construir_rdf()
    assert len(g)>0
    rows=consultar_fornecedores(g)
    assert len(rows)==2
    assert all("Fornecedor simulado" in row["fornecedor"] for row in rows)
    assert {r["material"] for r in rows}=={"Concreto FCK 30","Aco CA-50"}

def test_mlp_formato_e_probabilidades():
    model=treinar_mlp(epochs=30)
    X,_=lote_teste_exemplo()
    result=diagnosticar(X,model)
    assert len(result)==10
    assert all(abs(sum(r["probabilidades"].values())-1.0)<1e-8 for r in result)
    assert 0<=model["accuracy"]<=1

def test_pulp_tem_dependencia_explicita():
    pytest.importorskip("pulp")
    from src.etapa1_roteamento.modelo import otimizar_frota
    r=otimizar_frota()
    assert r["capacity_t_day"]>=450 and r["cost_brl_day"]>0

def test_deap_e_simpy_tem_dependencias_explicitas():
    pytest.importorskip("deap"); pytest.importorskip("simpy")
    from src.etapa2_otimizacao.modelo import otimizar_rota, simular_concretagem
    ga=otimizar_rota(populacao=20,geracoes=10)
    sim=simular_concretagem()
    assert len(ga["route"])==6
    assert sim["loads_processed"]>0 and sim["bottleneck"]=="Bomba M2"

def test_scikit_fuzzy_tem_dependencia_explicita():
    pytest.importorskip("skfuzzy")
    from src.etapa5_fuzzy.modelo import calcular_mamdani, calcular_sugeno
    assert 0<=calcular_mamdani(34,30)<=100
    assert 0<=calcular_sugeno(34,30)<=100

def test_benchmark_exato_da_rota():
    from src.etapa2_otimizacao.modelo import melhor_rota_exaustiva,avaliar_percurso
    r=melhor_rota_exaustiva()
    assert r["permutations_checked"]==720
    assert abs(r["distance_units"]-23.068520619853317)<1e-9
    assert r["load_t"]==108.0 and r["overload_t"]==0.0
    assert avaliar_percurso(r["route"])[0]==r["fitness"]

def test_otimo_da_frota_por_enumeracao():
    from src.etapa1_roteamento.modelo import FROTA
    opcoes=[]
    for a in range(FROTA["A"].disponibilidade+1):
        for b in range(FROTA["B"].disponibilidade+1):
            for c in range(FROTA["C"].disponibilidade+1):
                capacidade=150*a+100*b+75*c
                custo=900*a+700*b+550*c
                if capacidade>=450: opcoes.append((custo,capacidade,a,b,c))
    assert min(opcoes)==(2900,450,2,0,2)
