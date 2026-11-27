"""Grafo de conhecimento RDF para insumos e fornecedores com consulta SPARQL.

O grafo é construído com dados fictícios e utiliza um namespace reservado
para exemplos. A consulta demonstra como filtrar insumos de alta resistência
que estejam associados a fornecedores marcados como homologados.
"""
from rdflib import Graph, Literal, Namespace, RDF, RDFS, XSD

# Namespace de exemplo: não representa um domínio ou sistema comercial real.
EX = Namespace("https://aps2-torre-europarque.example/ontology/")


def construir_grafo():
    """Cria e popula um grafo RDF com projeto, materiais e fornecedores."""
    grafo = Graph()
    grafo.bind("ex", EX)

    # Declara as classes básicas da ontologia e seus rótulos em português.
    classes = [
        (EX.Projeto, "Projeto"),
        (EX.Insumo, "Insumo"),
        (EX.Fornecedor, "Fornecedor"),
    ]
    for classe, nome in classes:
        grafo.add((classe, RDF.type, RDFS.Class))
        grafo.add((classe, RDFS.label, Literal(nome, lang="pt-BR")))

    # Instância do projeto utilizada como ponto de partida das relações.
    projeto = EX.TorreEuroparque
    grafo.add((projeto, RDF.type, EX.Projeto))
    grafo.add((
        projeto,
        RDFS.label,
        Literal("Torre Europarque", lang="pt-BR"),
    ))

    # Materiais e atributos demonstrativos; as referências de catálogo
    # são apenas rótulos ilustrativos, sem consulta real ao SINAPI ou CUB.
    materiais = {
        EX.ConcretoFCK30: (
            "Concreto FCK 30",
            "alta",
            "SINAPI/CUB - referência ilustrativa",
        ),
        EX.AcoCA50: (
            "Aço CA-50",
            "alta",
            "SINAPI/CUB - referência ilustrativa",
        ),
        EX.Argamassa: (
            "Argamassa",
            "média",
            "SINAPI/CUB - referência ilustrativa",
        ),
    }

    for uri, (nome, resistencia, referencia) in materiais.items():
        grafo.add((uri, RDF.type, EX.Insumo))
        grafo.add((uri, RDFS.label, Literal(nome, lang="pt-BR")))
        grafo.add((uri, EX.nivelResistencia, Literal(resistencia)))
        grafo.add((uri, EX.referenciaCatalogo, Literal(referencia)))
        grafo.add((projeto, EX.utilizaInsumo, uri))

    # Os fornecedores são entidades simuladas, sem identidade comercial real.
    fornecedores = {
        EX.FornecedorConcreto: "Fornecedor simulado de concreto",
        EX.FornecedorAco: "Fornecedor simulado de aço",
        EX.FornecedorArgamassa: "Fornecedor simulado de argamassa",
    }
    for uri, nome in fornecedores.items():
        grafo.add((uri, RDF.type, EX.Fornecedor))
        grafo.add((uri, RDFS.label, Literal(nome, lang="pt-BR")))
        grafo.add((uri, EX.homologado, Literal(True, datatype=XSD.boolean)))

    # Relaciona cada material ao fornecedor fictício correspondente.
    grafo.add((EX.ConcretoFCK30, EX.fornecidoPor, EX.FornecedorConcreto))
    grafo.add((EX.AcoCA50, EX.fornecidoPor, EX.FornecedorAco))
    grafo.add((EX.Argamassa, EX.fornecidoPor, EX.FornecedorArgamassa))

    return grafo


# Consulta apenas materiais usados pelo projeto, com resistência alta,
# associados a fornecedores cujo atributo de homologação é verdadeiro.
CONSULTA_FORNECEDORES = """
PREFIX ex: <https://aps2-torre-europarque.example/ontology/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT DISTINCT ?materialNome ?fornecedorNome
WHERE {
 ex:TorreEuroparque ex:utilizaInsumo ?material .
 ?material ex:nivelResistencia "alta" ; rdfs:label ?materialNome ; ex:fornecidoPor ?fornecedor .
 ?fornecedor ex:homologado true ; rdfs:label ?fornecedorNome .
}
ORDER BY ?materialNome
"""


def consultar_fornecedores(grafo=None):
    """Executa a consulta SPARQL no grafo informado ou no grafo de exemplo."""
    if grafo is None:
        grafo = construir_grafo()

    return [
        {
            "material": str(linha.materialNome),
            "fornecedor": str(linha.fornecedorNome),
        }
        for linha in grafo.query(CONSULTA_FORNECEDORES)
    ]
