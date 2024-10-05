from dataclasses import dataclass
from random import random
from utils import learp


class NeuralNetwork:
    def __init__(self, neuron_counts):
        self.levels = []
        for i in range(len(neuron_counts) - 1):
            self.levels.append(Level(neuron_counts[i], neuron_counts[i + 1]))

    def feedforward(given_inputs, network):
        # print("nk", network.levels[0].inputs)
        outputs = Level.feedforward(given_inputs, network.levels[0])  # type: ignore
        for i in range(1, len(network.levels)):
            outputs = Level.feedforward(outputs, network.levels[i])  # type: ignore

        return outputs

    def mutate(network, amount=1):
        for level in network.levels:
            for i in range(len(level.biases)):
                level.biases[i] = learp(level.biases[i], random() * 2 - 1, amount)
            for i in range(len(level.weights)):
                for j in range(len(level.weights[i])):
                    level.weights[i][j] = learp(
                        level.weights[i][j], random() * 2 - 1, amount
                    )


class Level:
    def __init__(self, input_count, output_count):
        self.inputs = [0] * input_count
        self.outputs = [0] * output_count
        self.biases = [0] * output_count
        # self.outputs = []
        # self.biases = []

        self.weights = []

        for i in range(input_count):
            self.weights.append([0] * output_count)

        self.randomize()

    def randomize(self):
        for i in range(len(self.inputs)):
            for j in range(len(self.outputs)):
                self.weights[i][j] = random() * 2 - 1

        for i in range(len(self.biases)):
            self.biases[i] = random() * 2 - 1  # type: ignore

    def feedforward(given_inputs: list, level: list):
        for i in range(len(given_inputs)):
            level.inputs[i] = given_inputs[i]

        for i in range(len(level.outputs)):
            sum = 0
            for j in range(len(level.inputs)):
                sum += level.inputs[j] * level.weights[j][i]

            if sum > level.biases[i]:
                level.outputs[i] = 1
            else:
                level.outputs[i] = 0

        return level.outputs


# level = Level(4, 3)

# pp = pprint.PrettyPrinter()

# # print(level.weights)
# pp.pprint(level.biases)
