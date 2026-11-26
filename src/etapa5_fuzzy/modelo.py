"""Etapa 5: controle Fuzzy Mamdani via scikit-fuzzy e Sugeno de ordem zero."""
from __future__ import annotations
import numpy as np

def _bibliotecas():
    try:
        import skfuzzy as fuzz
        from skfuzzy import control as ctrl
    except ImportError as exc:
        raise RuntimeError("Instale as dependencias do requirements.txt.") from exc
    return fuzz,ctrl

def construir_mamdani():
    fuzz,ctrl=_bibliotecas()
    temperatura=ctrl.Antecedent(np.arange(0,51,1),"temperatura")
    umidade=ctrl.Antecedent(np.arange(0,101,1),"umidade")
    aditivo=ctrl.Consequent(np.arange(0,101,1),"aditivo")
    aditivo.defuzzify_method="centroid"
    temperatura["baixa"]=fuzz.trimf(temperatura.universe,[0,0,25])
    temperatura["media"]=fuzz.trimf(temperatura.universe,[15,27,39])
    temperatura["alta"]=fuzz.trimf(temperatura.universe,[30,50,50])
    umidade["baixa"]=fuzz.trimf(umidade.universe,[0,0,45])
    umidade["media"]=fuzz.trimf(umidade.universe,[25,50,75])
    umidade["alta"]=fuzz.trimf(umidade.universe,[55,100,100])
    aditivo["baixo"]=fuzz.trimf(aditivo.universe,[0,0,45])
    aditivo["medio"]=fuzz.trimf(aditivo.universe,[25,50,75])
    aditivo["alto"]=fuzz.trimf(aditivo.universe,[55,100,100])
    regras=[
      ctrl.Rule(temperatura["alta"] & umidade["baixa"],aditivo["alto"]),
      ctrl.Rule(temperatura["alta"] & umidade["media"],aditivo["medio"]),
      ctrl.Rule(temperatura["media"] & umidade["baixa"],aditivo["medio"]),
      ctrl.Rule(temperatura["baixa"] | umidade["alta"] | (temperatura["media"] & umidade["media"]),aditivo["baixo"]),
    ]
    return ctrl.ControlSystem(regras)

def _graus_fuzzy(temperatura_c,umidade_pct):
    fuzz,_=_bibliotecas()
    t={"baixa":float(fuzz.trimf(np.asarray([temperatura_c]),[0,0,25])[0]),
       "media":float(fuzz.trimf(np.asarray([temperatura_c]),[15,27,39])[0]),
       "alta":float(fuzz.trimf(np.asarray([temperatura_c]),[30,50,50])[0])}
    u={"baixa":float(fuzz.trimf(np.asarray([umidade_pct]),[0,0,45])[0]),
       "media":float(fuzz.trimf(np.asarray([umidade_pct]),[25,50,75])[0]),
       "alta":float(fuzz.trimf(np.asarray([umidade_pct]),[55,100,100])[0])}
    return t,u

def calcular_sugeno(temperatura_c,umidade_pct):
    """Sugeno de ordem zero: media ponderada dos consequentes constantes."""
    if not (0<=temperatura_c<=50 and 0<=umidade_pct<=100):
        raise ValueError("Temperatura ou umidade fora do universo de discurso.")
    t,u=_graus_fuzzy(temperatura_c,umidade_pct)
    ativacoes=[min(t["alta"],u["baixa"]),min(t["alta"],u["media"]),
               min(t["media"],u["baixa"]),max(t["baixa"],u["alta"],min(t["media"],u["media"]))]
    consequentes=[85.0,60.0,60.0,20.0]
    soma=sum(ativacoes)
    return 20.0 if soma<=1e-12 else float(sum(a*z for a,z in zip(ativacoes,consequentes))/soma)

def calcular_mamdani(temperatura_c=34,umidade_pct=30):
    if not (0<=temperatura_c<=50 and 0<=umidade_pct<=100):
        raise ValueError("Temperatura ou umidade fora do universo de discurso.")
    _,ctrl=_bibliotecas()
    simulacao=ctrl.ControlSystemSimulation(construir_mamdani())
    simulacao.input["temperatura"]=temperatura_c
    simulacao.input["umidade"]=umidade_pct
    simulacao.compute()
    return float(simulacao.output["aditivo"])

def superficie_resposta(resolucao=21):
    """Calcula a malha 3D reutilizando o sistema de controle Mamdani."""
    if resolucao<2:
        raise ValueError("A resolucao da superficie deve ter ao menos dois pontos.")
    _,ctrl=_bibliotecas()
    temperaturas=np.linspace(0,50,resolucao)
    umidades=np.linspace(0,100,resolucao)
    mamdani=np.zeros((resolucao,resolucao))
    sugeno=np.zeros_like(mamdani)
    simulacao=ctrl.ControlSystemSimulation(construir_mamdani(),cache=False)
    for i,t in enumerate(temperaturas):
        for j,u in enumerate(umidades):
            simulacao.input["temperatura"]=float(t)
            simulacao.input["umidade"]=float(u)
            simulacao.compute()
            mamdani[i,j]=float(simulacao.output["aditivo"])
            sugeno[i,j]=calcular_sugeno(float(t),float(u))
    return temperaturas,umidades,mamdani,sugeno
