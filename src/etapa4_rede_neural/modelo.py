"""Etapa 4: MLP multiclasses implementada do zero com NumPy."""
from __future__ import annotations
import numpy as np

NOMES_SENSORES = [
    "vibracao_rms", "curtose", "fator_crista", "aceleracao_x",
    "aceleracao_y", "aceleracao_z", "temperatura_mancal_c",
    "temperatura_motor_c", "temperatura_redutor_c", "temperatura_ambiente_c"
]
ESTADOS = ["Operacao normal", "Alerta de desgaste", "Falha iminente"]

class Layer_Dense:
    def __init__(self, n_inputs, n_neurons, weight_scale=None, seed=7):
        rng = np.random.default_rng(seed)
        scale = weight_scale if weight_scale is not None else np.sqrt(2.0 / n_inputs)
        self.weights = rng.normal(0.0, scale, (n_inputs, n_neurons))
        self.biases = np.zeros((1, n_neurons))
    def forward(self, inputs):
        self.inputs = np.asarray(inputs, dtype=float)
        self.output = self.inputs @ self.weights + self.biases
    def backward(self, dvalues):
        self.dweights = self.inputs.T @ dvalues
        self.dbiases = np.sum(dvalues, axis=0, keepdims=True)
        self.dinputs = dvalues @ self.weights.T
    def update(self, learning_rate):
        self.weights -= learning_rate * self.dweights
        self.biases -= learning_rate * self.dbiases

class Activation_ReLU:
    def forward(self, inputs):
        self.inputs = inputs
        self.output = np.maximum(0, inputs)
    def backward(self, dvalues):
        self.dinputs = dvalues.copy()
        self.dinputs[self.inputs <= 0] = 0

class Activation_Softmax:
    def forward(self, inputs):
        shifted = inputs - np.max(inputs, axis=1, keepdims=True)
        exp_values = np.exp(shifted)
        self.output = exp_values / np.sum(exp_values, axis=1, keepdims=True)
    def backward(self, dvalues):
        self.dinputs = np.empty_like(dvalues)
        for i, (single_output, single_dvalues) in enumerate(zip(self.output, dvalues)):
            jacobian = np.diag(single_output) - np.outer(single_output, single_output)
            self.dinputs[i] = jacobian @ single_dvalues

class Loss_CategoricalCrossentropy:
    def forward(self, y_pred, y_true):
        samples = len(y_pred)
        clipped = np.clip(y_pred, 1e-7, 1.0 - 1e-7)
        if np.asarray(y_true).ndim == 1:
            correct = clipped[range(samples), np.asarray(y_true, dtype=int)]
        else:
            correct = np.sum(clipped * y_true, axis=1)
        return float(np.mean(-np.log(correct)))
    def backward(self, y_pred, y_true):
        samples = len(y_pred)
        labels = np.asarray(y_true)
        if labels.ndim == 1:
            labels = np.eye(y_pred.shape[1])[labels.astype(int)]
        self.dinputs = -labels / np.clip(y_pred, 1e-7, 1.0 - 1e-7) / samples

def gerar_dados_sinteticos(seed=19, amostras_por_classe=300):
    """Gera telemetria didatica; nao representa sensores reais."""
    rng = np.random.default_rng(seed)
    medias = np.array([
        [0.12,0.15,1.3,0.05,0.05,0.05,55,52,50,25],
        [0.36,0.35,2.8,0.18,0.16,0.19,75,72,68,31],
        [0.73,0.70,4.7,0.42,0.40,0.44,96,92,88,38],
    ])
    desvios = np.array([
        [0.04,0.05,0.18,0.025,0.025,0.025,5,5,5,3],
        [0.08,0.08,0.35,0.05,0.05,0.05,7,7,7,4],
        [0.10,0.10,0.45,0.07,0.07,0.07,8,8,8,4],
    ])
    X,y=[],[]
    for classe in range(3):
        X.append(rng.normal(medias[classe],desvios[classe],(amostras_por_classe,10)))
        y.extend([classe]*amostras_por_classe)
    X=np.vstack(X); y=np.asarray(y,dtype=int); ordem=rng.permutation(len(y))
    return X[ordem],y[ordem]

def treinar_mlp(epochs=180,learning_rate=0.035,seed=7):
    X,y=gerar_dados_sinteticos(seed=19)
    rng=np.random.default_rng(seed); indices=rng.permutation(len(y)); corte=int(0.8*len(y))
    treino,teste=indices[:corte],indices[corte:]
    media,desvio=X[treino].mean(axis=0),X[treino].std(axis=0); desvio[desvio==0]=1.0
    Xs=(X-media)/desvio
    d1, relu, d2, softmax, loss = Layer_Dense(10,16,seed=seed),Activation_ReLU(),Layer_Dense(16,3,seed=seed+1),Activation_Softmax(),Loss_CategoricalCrossentropy()
    historico=[]
    for _ in range(epochs):
        ordem=rng.permutation(len(treino))
        for inicio in range(0,len(treino),64):
            lote=treino[ordem[inicio:inicio+64]]
            d1.forward(Xs[lote]); relu.forward(d1.output); d2.forward(relu.output); softmax.forward(d2.output)
            grad=(softmax.output-np.eye(3)[y[lote]])/len(lote)
            d2.backward(grad); relu.backward(d2.dinputs); d1.backward(relu.dinputs)
            d1.update(learning_rate); d2.update(learning_rate)
        d1.forward(Xs[treino]); relu.forward(d1.output); d2.forward(relu.output); softmax.forward(d2.output)
        historico.append(loss.forward(softmax.output,y[treino]))
    d1.forward(Xs[teste]); relu.forward(d1.output); d2.forward(relu.output); softmax.forward(d2.output)
    acuracia=float(np.mean(np.argmax(softmax.output,axis=1)==y[teste]))
    return {"layers":(d1,relu,d2,softmax),"mean":media,"std":desvio,"accuracy":acuracia,
            "loss_history":historico,"test_size":len(teste)}

def lote_teste_exemplo(seed=2026,quantidade=10):
    X,y=gerar_dados_sinteticos(seed=seed,amostras_por_classe=quantidade)
    return X[:quantidade],y[:quantidade]

def diagnosticar(X,modelo):
    d1,relu,d2,softmax=modelo["layers"]
    Xn=(np.asarray(X,dtype=float)-modelo["mean"])/modelo["std"]
    d1.forward(Xn); relu.forward(d1.output); d2.forward(relu.output); softmax.forward(d2.output)
    classes=np.argmax(softmax.output,axis=1)
    return [{"equipamento":i+1,"estado":ESTADOS[int(c)],
             "probabilidades":{ESTADOS[j]:float(softmax.output[i,j]) for j in range(3)}}
            for i,c in enumerate(classes)]
