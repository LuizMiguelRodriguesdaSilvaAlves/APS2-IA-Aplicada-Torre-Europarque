"""Testes de regressão e consistência para os módulos do projeto."""

import pytest

from src.etapa1_roteamento.modelo import (
    calcular_rota,
    construir_grafo,
    distancia_manhattan,
)
from src.etapa3_conhecimento.modelo import (
    construir_grafo as construir_rdf,
    consultar_fornecedores,
)
from src.etapa4_rede_neural.modelo import (
    diagnosticar,
    lote_teste_exemplo,
    treinar_mlp,
)


def test_astar_respeita_obstaculos_e_heuristica():
    """Verifica origem, destino, distância esperada e exclusão dos obstáculos."""
    resultado = calcular_rota()

    assert resultado["distance"] == 14
    assert (3, 3) not in resultado["path"]
    assert (3, 4) not in resultado["path"]
    assert resultado["path"][0] == (0, 0)
    assert resultado["path"][-1] == (7, 7)
    assert distancia_manhattan((0, 0), (7, 7)) == 14
    assert (3, 3) not in construir_grafo()


def test_rdf_sparql_retorna_apenas_insumos_alta_resistencia():
    """Confere as triplas e os pares material-fornecedor retornados pela consulta."""
    grafo = construir_rdf()
    assert len(grafo) > 0

    linhas = consultar_fornecedores(grafo)

    assert len(linhas) == 2
    assert all(
        "Fornecedor simulado" in linha["fornecedor"]
        for linha in linhas
    )
    assert {
        linha["material"]
        for linha in linhas
    } == {"Concreto FCK 30", "Aço CA-50"}


def test_mlp_formato_e_probabilidades():
    """Confere o formato da inferência e a soma das probabilidades por classe."""
    modelo = treinar_mlp(epochs=30)
    X, _ = lote_teste_exemplo()
    resultado = diagnosticar(X, modelo)

    assert len(resultado) == 10
    assert all(
        abs(sum(item["probabilidades"].values()) - 1.0) < 1e-8
        for item in resultado
    )
    assert 0 <= modelo["accuracy"] <= 1


def test_pulp_tem_dependencia_explicita():
    """Executa a otimização da frota quando PuLP está instalado."""
    pytest.importorskip("pulp")

    from src.etapa1_roteamento.modelo import otimizar_frota

    resultado = otimizar_frota()
    assert resultado["capacity_t_day"] >= 450
    assert resultado["cost_brl_day"] > 0


def test_deap_e_simpy_tem_dependencias_explicitas():
    """Valida a rota genética e a simulação quando DEAP e SimPy estão disponíveis."""
    pytest.importorskip("deap")
    pytest.importorskip("simpy")

    from src.etapa2_otimizacao.modelo import (
        otimizar_rota,
        simular_concretagem,
    )

    genetico = otimizar_rota(populacao=20, geracoes=10)
    simulacao = simular_concretagem()

    assert len(genetico["route"]) == 6
    assert simulacao["loads_processed"] > 0
    assert simulacao["bottleneck"] == "Bomba M2"


def test_scikit_fuzzy_tem_dependencia_explicita():
    """Confere se os dois controladores retornam valores no universo de saída."""
    pytest.importorskip("skfuzzy")

    from src.etapa5_fuzzy.modelo import (
        calcular_mamdani,
        calcular_sugeno,
    )

    assert 0 <= calcular_mamdani(34, 30) <= 100
    assert 0 <= calcular_sugeno(34, 30) <= 100


def test_benchmark_exato_da_rota():
    """Confere a enumeração completa das 720 ordens possíveis dos blocos."""
    from src.etapa2_otimizacao.modelo import (
        avaliar_percurso,
        melhor_rota_exaustiva,
    )

    resultado = melhor_rota_exaustiva()

    assert resultado["permutations_checked"] == 720
    assert abs(
        resultado["distance_units"] - 23.068520619853317
    ) < 1e-9
    assert resultado["load_t"] == 108.0
    assert resultado["overload_t"] == 0.0
    assert avaliar_percurso(resultado["route"])[0] == resultado["fitness"]


def test_otimo_da_frota_por_enumeracao():
    """Valida a solução esperada da frota por enumeração independente do PuLP."""
    from src.etapa1_roteamento.modelo import FROTA

    opcoes = []

    # Enumera todas as combinações permitidas de unidades A, B e C.
    for quantidade_a in range(FROTA["A"].disponibilidade + 1):
        for quantidade_b in range(FROTA["B"].disponibilidade + 1):
            for quantidade_c in range(FROTA["C"].disponibilidade + 1):
                capacidade = (
                    150 * quantidade_a
                    + 100 * quantidade_b
                    + 75 * quantidade_c
                )
                custo = (
                    900 * quantidade_a
                    + 700 * quantidade_b
                    + 550 * quantidade_c
                )

                if capacidade >= 450:
                    opcoes.append((
                        custo,
                        capacidade,
                        quantidade_a,
                        quantidade_b,
                        quantidade_c,
                    ))

    assert min(opcoes) == (2900, 450, 2, 0, 2)
