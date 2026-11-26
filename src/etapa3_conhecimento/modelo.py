"""Etapa 3: grafo de conhecimento RDF e consulta SPARQL."""
from rdflib import Graph,Namespace,RDF,RDFS,Literal,XSD
EX=Namespace("https://aps2-torre-europarque.example/ontology/")

def construir_grafo():
    g=Graph(); g.bind("ex",EX)
    for classe,nome in [(EX.Projeto,"Projeto"),(EX.Insumo,"Insumo"),(EX.Fornecedor,"Fornecedor")]:
        g.add((classe,RDF.type,RDFS.Class)); g.add((classe,RDFS.label,Literal(nome,lang="pt-BR")))
    projeto=EX.TorreEuroparque
    g.add((projeto,RDF.type,EX.Projeto)); g.add((projeto,RDFS.label,Literal("Torre Europarque",lang="pt-BR")))
    materiais={
      EX.ConcretoFCK30:("Concreto FCK 30","alta","SINAPI/CUB - referencia ilustrativa"),
      EX.AcoCA50:("Aco CA-50","alta","SINAPI/CUB - referencia ilustrativa"),
      EX.Argamassa:("Argamassa","media","SINAPI/CUB - referencia ilustrativa")}
    for uri,(nome,resistencia,ref) in materiais.items():
        g.add((uri,RDF.type,EX.Insumo)); g.add((uri,RDFS.label,Literal(nome,lang="pt-BR")))
        g.add((uri,EX.nivelResistencia,Literal(resistencia))); g.add((uri,EX.referenciaCatalogo,Literal(ref)))
        g.add((projeto,EX.utilizaInsumo,uri))
    fornecedores={EX.FornecedorConcreto:"Fornecedor simulado de concreto",
                  EX.FornecedorAco:"Fornecedor simulado de aco",
                  EX.FornecedorArgamassa:"Fornecedor simulado de argamassa"}
    for uri,nome in fornecedores.items():
        g.add((uri,RDF.type,EX.Fornecedor)); g.add((uri,RDFS.label,Literal(nome,lang="pt-BR")))
        g.add((uri,EX.homologado,Literal(True,datatype=XSD.boolean)))
    g.add((EX.ConcretoFCK30,EX.fornecidoPor,EX.FornecedorConcreto))
    g.add((EX.AcoCA50,EX.fornecidoPor,EX.FornecedorAco))
    g.add((EX.Argamassa,EX.fornecidoPor,EX.FornecedorArgamassa))
    return g

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
    grafo=grafo or construir_grafo()
    return [{"material":str(row.materialNome),"fornecedor":str(row.fornecedorNome)}
            for row in grafo.query(CONSULTA_FORNECEDORES)]
