"""MLP multiclasses implementada com operações matriciais do NumPy.

O módulo contém as camadas, ativações, função de perda, geração de dados
sintéticos, rotina de treinamento e uma função de diagnóstico. A rede é
um exercício didático e não foi treinada nem validada com telemetria real.
"""
from __future__ import annotations

import numpy as np


# Dez atributos simulados que representam leituras de sensores industriais.
NOMES_SENSORES = [
    "vibracao_rms",
    "curtose",
    "fator_crista",
    "aceleracao_x",
    "aceleracao_y",
    "aceleracao_z",
    "temperatura_mancal_c",
    "temperatura_motor_c",
    "temperatura_redutor_c",
    "temperatura_ambiente_c",
]

# Classes de saída utilizadas pelo classificador multiclasse.
ESTADOS = [
    "Operação normal",
    "Alerta de desgaste",
    "Falha iminente",
]


class Layer_Dense:
    """Camada totalmente conectada com pesos, vieses e retropropagação."""

    def __init__(self, n_inputs, n_neurons, weight_scale=None, seed=7):
        # Gerador local torna a inicialização reproduzível sem alterar
        # o estado aleatório global utilizado em outras partes do projeto.
        rng = np.random.default_rng(seed)

        # A escala padrão segue a inicialização He, apropriada para ReLU.
        scale = (
            weight_scale
            if weight_scale is not None
            else np.sqrt(2.0 / n_inputs)
        )
        self.weights = rng.normal(0.0, scale, (n_inputs, n_neurons))
        self.biases = np.zeros((1, n_neurons))

    def forward(self, inputs):
        """Calcula a combinação linear: entradas x pesos + vieses."""
        self.inputs = np.asarray(inputs, dtype=float)
        self.output = self.inputs @ self.weights + self.biases

    def backward(self, dvalues):
        """Propaga gradientes para pesos, vieses e camada anterior."""
        self.dweights = self.inputs.T @ dvalues
        self.dbiases = np.sum(dvalues, axis=0, keepdims=True)
        self.dinputs = dvalues @ self.weights.T

    def update(self, learning_rate):
        """Aplica uma atualização por descida do gradiente."""
        self.weights -= learning_rate * self.dweights
        self.biases -= learning_rate * self.dbiases


class Activation_ReLU:
    """Ativação ReLU, que zera valores negativos."""

    def forward(self, inputs):
        self.inputs = inputs
        self.output = np.maximum(0, inputs)

    def backward(self, dvalues):
        # A derivada é zero para entradas não positivas e um para positivas.
        self.dinputs = dvalues.copy()
        self.dinputs[self.inputs <= 0] = 0


class Activation_Softmax:
    """Converte os escores da última camada em probabilidades por classe."""

    def forward(self, inputs):
        # Subtrair o máximo de cada linha melhora a estabilidade numérica
        # antes de calcular a exponencial.
        shifted = inputs - np.max(inputs, axis=1, keepdims=True)
        exp_values = np.exp(shifted)
        self.output = exp_values / np.sum(exp_values, axis=1, keepdims=True)

    def backward(self, dvalues):
        """Calcula o gradiente usando a matriz Jacobiana do Softmax."""
        self.dinputs = np.empty_like(dvalues)
        for i, (single_output, single_dvalues) in enumerate(
            zip(self.output, dvalues)
        ):
            jacobian = (
                np.diag(single_output)
                - np.outer(single_output, single_output)
            )
            self.dinputs[i] = jacobian @ single_dvalues


class Loss_CategoricalCrossentropy:
    """Calcula a entropia cruzada para classificação multiclasse."""

    def forward(self, y_pred, y_true):
        samples = len(y_pred)

        # O clipping evita logaritmo de zero e instabilidade por arredondamento.
        clipped = np.clip(y_pred, 1e-7, 1.0 - 1e-7)

        # Aceita rótulos inteiros ou vetores one-hot.
        if np.asarray(y_true).ndim == 1:
            correct = clipped[range(samples), np.asarray(y_true, dtype=int)]
        else:
            correct = np.sum(clipped * y_true, axis=1)

        return float(np.mean(-np.log(correct)))

    def backward(self, y_pred, y_true):
        """Calcula o gradiente da perda, com suporte a rótulos one-hot."""
        samples = len(y_pred)
        labels = np.asarray(y_true)

        if labels.ndim == 1:
            labels = np.eye(y_pred.shape[1])[labels.astype(int)]

        self.dinputs = (
            -labels
            / np.clip(y_pred, 1e-7, 1.0 - 1e-7)
            / samples
        )


def gerar_dados_sinteticos(seed=19, amostras_por_classe=300):
    """Gera um conjunto artificial para testar o fluxo de classificação.

    Cada classe possui médias e desvios próprios para as dez variáveis.
    As distribuições foram criadas apenas para uma demonstração controlada;
    elas não correspondem a medições de equipamentos reais.
    """
    rng = np.random.default_rng(seed)

    # Cada linha representa uma classe e cada coluna uma variável de sensor.
    medias = np.array([
        [0.12, 0.15, 1.3, 0.05, 0.05, 0.05, 55, 52, 50, 25],
        [0.36, 0.35, 2.8, 0.18, 0.16, 0.19, 75, 72, 68, 31],
        [0.73, 0.70, 4.7, 0.42, 0.40, 0.44, 96, 92, 88, 38],
    ])
    desvios = np.array([
        [0.04, 0.05, 0.18, 0.025, 0.025, 0.025, 5, 5, 5, 3],
        [0.08, 0.08, 0.35, 0.05, 0.05, 0.05, 7, 7, 7, 4],
        [0.10, 0.10, 0.45, 0.07, 0.07, 0.07, 8, 8, 8, 4],
    ])

    X, y = [], []

    # Amostras são geradas separadamente para cada estado e depois reunidas.
    for classe in range(3):
        X.append(
            rng.normal(
                medias[classe],
                desvios[classe],
                (amostras_por_classe, 10),
            )
        )
        y.extend([classe] * amostras_por_classe)

    X = np.vstack(X)
    y = np.asarray(y, dtype=int)

    # Embaralha as amostras para evitar que a ordem das classes influencie
    # a divisão posterior entre treino e teste.
    ordem = rng.permutation(len(y))
    return X[ordem], y[ordem]


def treinar_mlp(epochs=180, learning_rate=0.035, seed=7):
    """Treina a MLP e mede a acurácia em uma partição de teste sintética.

    O fluxo inclui divisão treino/teste, padronização baseada somente no
    conjunto de treino, mini-lotes, retropropagação e atualização dos pesos.
    """
    X, y = gerar_dados_sinteticos(seed=19)

    rng = np.random.default_rng(seed)
    indices = rng.permutation(len(y))
    corte = int(0.8 * len(y))
    treino, teste = indices[:corte], indices[corte:]

    # Parâmetros de normalização são calculados apenas com os dados de treino.
    media = X[treino].mean(axis=0)
    desvio = X[treino].std(axis=0)
    desvio[desvio == 0] = 1.0
    Xs = (X - media) / desvio

    # Arquitetura: 10 entradas -> 16 neurônios ReLU -> 3 saídas Softmax.
    d1 = Layer_Dense(10, 16, seed=seed)
    relu = Activation_ReLU()
    d2 = Layer_Dense(16, 3, seed=seed + 1)
    softmax = Activation_Softmax()
    loss = Loss_CategoricalCrossentropy()

    historico = []

    # Em cada época, a ordem dos exemplos de treino é novamente embaralhada.
    for _ in range(epochs):
        ordem = rng.permutation(len(treino))

        # Mini-batches reduzem o custo de cada atualização e permitem
        # acumular gradientes sobre pequenos grupos de amostras.
        for inicio in range(0, len(treino), 64):
            lote = treino[ordem[inicio:inicio + 64]]

            # Forward pass: camada densa, ReLU, camada de saída e Softmax.
            d1.forward(Xs[lote])
            relu.forward(d1.output)
            d2.forward(relu.output)
            softmax.forward(d2.output)

            # Gradiente combinado de Softmax + entropia cruzada.
            grad = (
                softmax.output - np.eye(3)[y[lote]]
            ) / len(lote)

            # Backward pass percorre as camadas na ordem inversa.
            d2.backward(grad)
            relu.backward(d2.dinputs)
            d1.backward(relu.dinputs)

            # Atualização dos parâmetros treináveis das duas camadas densas.
            d1.update(learning_rate)
            d2.update(learning_rate)

        # Registra a perda ao final de cada época usando todo o treino.
        d1.forward(Xs[treino])
        relu.forward(d1.output)
        d2.forward(relu.output)
        softmax.forward(d2.output)
        historico.append(loss.forward(softmax.output, y[treino]))

    # Avaliação final é feita em amostras que não participaram do gradiente.
    d1.forward(Xs[teste])
    relu.forward(d1.output)
    d2.forward(relu.output)
    softmax.forward(d2.output)
    acuracia = float(
        np.mean(np.argmax(softmax.output, axis=1) == y[teste])
    )

    return {
        "layers": (d1, relu, d2, softmax),
        "mean": media,
        "std": desvio,
        "accuracy": acuracia,
        "loss_history": historico,
        "test_size": len(teste),
    }


def lote_teste_exemplo(seed=2026, quantidade=10):
    """Gera amostras sintéticas para demonstrar a função de diagnóstico."""
    X, y = gerar_dados_sinteticos(
        seed=seed,
        amostras_por_classe=quantidade,
    )
    return X[:quantidade], y[:quantidade]


def diagnosticar(X, modelo):
    """Classifica cada linha de entrada e retorna probabilidades por estado."""
    d1, relu, d2, softmax = modelo["layers"]

    # Aplica aos novos dados a mesma padronização ajustada no treino.
    Xn = (
        np.asarray(X, dtype=float) - modelo["mean"]
    ) / modelo["std"]

    # Inferência: propaga os dados pelas camadas já treinadas.
    d1.forward(Xn)
    relu.forward(d1.output)
    d2.forward(relu.output)
    softmax.forward(d2.output)

    classes = np.argmax(softmax.output, axis=1)

    return [
        {
            "equipamento": i + 1,
            "estado": ESTADOS[int(classe)],
            "probabilidades": {
                ESTADOS[j]: float(softmax.output[i, j])
                for j in range(3)
            },
        }
        for i, classe in enumerate(classes)
    ]
