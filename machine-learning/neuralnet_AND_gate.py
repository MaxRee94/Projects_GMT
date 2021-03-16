# AND-gate 2-2-1 neural network
import math
import random


class NeuralNet:
    def __init__(self, theseInputs, theseExpectedOutputs, biases, weights):
        self.biases = biases
        self.weights = weights

        self.learningRate = learningRate

        self.inputLayerLength = inputLayerLength
        self.hiddenLayerLengths = hiddenLayerLengths
        self.hiddenLayerAmount = hiddenLayerAmount
        self.outputLayerLength = outputLayerLength

        self.neuronIndexes = neuronIndexes

        self.biasesPlusWeights = []
        previousConnectionsAmount = 0
        previousLayerLength = len(self.neuronIndexes[0])
        for layerIndex in range(len(self.neuronIndexes) - 1):
            currentLayer = self.neuronIndexes[layerIndex + 1]
            currentLayerLength = len(currentLayer)
            for neuronIndex in currentLayer:
                currentBias = self.biases[neuronIndex]
                neuronInfo = [currentBias]
                for connection in range(previousLayerLength):
                    weightIndex = previousConnectionsAmount
                    neuronInfo.append(self.weights[weightIndex])
                    previousConnectionsAmount += 1
                self.biasesPlusWeights.append(neuronInfo)
            previousLayerLength = currentLayerLength

        print("biasesPlusWeights:", str(self.biasesPlusWeights))
        print("")
        self.runNetwork(self.biasesPlusWeights, theseInputs, theseExpectedOutputs)

    def runNetwork(self, biasesPlusWeights, theseInputs, theseExpectedOutputs):
        # convert local variables to class attributes
        self.inputs = theseInputs
        self.expectedOutputs = theseExpectedOutputs
        self.biasesPlusWeights = biasesPlusWeights

        def updateNeuronOutput(inputs, weights, bias):
            # summation unit
            netValue = bias
            for thisInput, weight in zip(inputs, weights):
                netValue += thisInput * weight

            # transfer function
            neuronOutput = 1 / (1 + math.exp(-netValue))
            return neuronOutput

        # first hidden layer
        firstHiddenLayerOutputs = []
        for neuronIndex in range(hiddenLayerLengths):
            neuronInfo = self.biasesPlusWeights[neuronIndex]
            currentBias = neuronInfo[0]
            weights = neuronInfo[1:-1]
            weights.append(neuronInfo[-1])
            thisNeuronOutput = updateNeuronOutput(self.inputs, weights, currentBias)
            firstHiddenLayerOutputs.append(thisNeuronOutput)
        lastIndex = neuronIndex
        self.hiddenLayer_outputs = [firstHiddenLayerOutputs]

        # other hidden layers
        previousLayer_outputs = firstHiddenLayerOutputs
        for layer in range(hiddenLayerAmount - 1):
            currentLayerOutputs = []
            for neuronIndex in range(lastIndex + 1, hiddenLayerLengths + lastIndex + 1):
                neuronInfo = self.biasesPlusWeights[neuronIndex]
                currentBias = neuronInfo[0]
                weights = neuronInfo[1:-1]
                weights.append(neuronInfo[-1])
                thisNeuronOutput = updateNeuronOutput(
                    previousLayer_outputs, weights, currentBias
                )
                currentLayerOutputs.append(thisNeuronOutput)
            self.hiddenLayer_outputs.append(currentLayerOutputs)
            previousLayer_outputs = currentLayerOutputs
        lastIndex = neuronIndex

        # output layer
        self.outputLayer_outputs = []
        for neuronIndex in range(lastIndex + 1, outputLayerLength + lastIndex + 1):
            neuronInfo = self.biasesPlusWeights[neuronIndex]
            currentBias = neuronInfo[0]
            weights = neuronInfo[1:-1]
            weights.append(neuronInfo[-1])
            thisNeuronOutput = updateNeuronOutput(
                previousLayer_outputs, weights, currentBias
            )
            self.outputLayer_outputs.append(thisNeuronOutput)

    def findDeltas(self):
        # calculate output layer deltas
        self.outputLayerDeltas = []
        for expectedOutput, actualOutput in zip(
            self.expectedOutputs, self.outputLayer_outputs
        ):
            outputDelta = expectedOutput - actualOutput
            self.outputLayerDeltas.append(outputDelta)
        # print('')
        # print('output layer deltas:',str(self.outputLayerDeltas))

        # calculate deltas for all hidden layers
        # --- get neuronOutputs and connectionWeights and calculate deltas
        self.hiddenLayerDeltas = []
        previousIndex = 0
        self.nextLayerDeltas = self.outputLayerDeltas
        nextLayerIndex = -1
        allWeights = []
        for layer_outputs in self.hiddenLayer_outputs:
            self.currentLayerDeltas = []
            nextNeuronIndexes = self.neuronIndexes[nextLayerIndex]
            # print('next neuron layer indexes:',str(neuronIndexes))
            for thisNeuron_output, thisNeuron_index in zip(
                layer_outputs, range(len(layer_outputs))
            ):
                # get weights of each connection between this layer and the next
                for nextNeuronIndex in nextNeuronIndexes:
                    neuronInfo = self.biasesPlusWeights[nextNeuronIndex]
                    newWeights = neuronInfo[1:-1]
                    newWeights.append(neuronInfo[-1])
                    allWeights.append(newWeights)

                # filter for weights of connections to current neuron only
                relevantWeights = []
                nextLayerLength = len(nextNeuronIndexes)
                for k in range(nextLayerLength):
                    for neuronWeights in allWeights:
                        relevantWeights.append(neuronWeights[thisNeuron_index])

                # calculate error factor of the current neuron
                errorFactor = 0
                for j in range(nextLayerLength):
                    nextNeuron_delta = self.nextLayerDeltas[j]
                    weight = relevantWeights[j]
                    errorFactor += nextNeuron_delta * weight

                # calculate the delta of the current neuron
                thisNeuron_delta = (
                    thisNeuron_output * (1 - thisNeuron_output) * errorFactor
                )

                self.currentLayerDeltas.append(thisNeuron_delta)
            nextLayerIndex -= 1
            self.nextLayerDeltas = self.currentLayerDeltas

            # append to the list of hidden layer deltas
            self.hiddenLayerDeltas.append(self.currentLayerDeltas)
        self.update_params()

    def update_params(self):
        # calculate new biases and weights for hidden layer neurons
        oldParams_index = 0
        self.new_biasesPlusWeights = []
        previousLayer_neuronOutputs = self.inputs
        outputs_layerIndex = 0
        for thisLayer_deltas in self.hiddenLayerDeltas:
            for thisNeuron_delta in thisLayer_deltas:
                # get old params
                old_neuronInfo = self.biasesPlusWeights[oldParams_index]
                oldBias = old_neuronInfo[0]
                oldWeights = old_neuronInfo[1:-1]
                oldWeights.append(old_neuronInfo[-1])

                # calculate new params
                newBias = oldBias + self.learningRate * thisNeuron_delta
                new_neuronInfo = [newBias]
                for oldWeight, inputNeuron_output in zip(
                    oldWeights, previousLayer_neuronOutputs
                ):
                    newWeight = (
                        oldWeight
                        + self.learningRate * inputNeuron_output * thisNeuron_delta
                    )
                    new_neuronInfo.append(newWeight)

                # append neuronInfo to biases and weights list
                self.new_biasesPlusWeights.append(new_neuronInfo)

                # next old params index
                oldParams_index += 1

            previousLayer_neuronOutputs = self.hiddenLayer_outputs[outputs_layerIndex]
            outputs_layerIndex += 1

        # calculate new biases and weights for output layer neurons
        for thisNeuron_delta in self.outputLayerDeltas:
            # get old params
            old_neuronInfo = self.biasesPlusWeights[oldParams_index]
            oldBias = old_neuronInfo[0]
            oldWeights = old_neuronInfo[1:-1]
            oldWeights.append(old_neuronInfo[-1])

            # calculate new params
            newBias = oldBias + self.learningRate * thisNeuron_delta
            new_neuronInfo = [newBias]
            for oldWeight, inputNeuron_output in zip(
                oldWeights, previousLayer_neuronOutputs
            ):
                newWeight = (
                    oldWeight
                    + self.learningRate * inputNeuron_output * thisNeuron_delta
                )
                new_neuronInfo.append(newWeight)

            # append neuronInfo to biases and weights list
            self.new_biasesPlusWeights.append(new_neuronInfo)

            # next old params index
            oldParams_index += 1


# generate initial values of the biases and weights
def generateInitParams():
    weights = []
    for i in range(amountOfConnections):
        weights.append(random.uniform(-2.00, 2.00))
    biases = []
    for i in range(amountOfNeurons - inputLayerLength):
        biases.append(random.uniform(-2.00, 2.00))
    return [weights, biases]


# set the amount - and lengths of the neuron layers
inputLayerLength = 2
hiddenLayerLengths = 2
hiddenLayerAmount = 1
outputLayerLength = 1

amountOfConnections = (
    inputLayerLength * hiddenLayerLengths
    + hiddenLayerLengths * hiddenLayerLengths * (hiddenLayerAmount - 1)
    + hiddenLayerLengths * outputLayerLength
)

amountOfNeurons = (
    inputLayerLength + hiddenLayerLengths * hiddenLayerAmount + outputLayerLength
)

freeParameters = generateInitParams()
initWeights = freeParameters[0]
initBiases = freeParameters[1]

myInputs = [[0, 0], [0, 1], [1, 0], [1, 1]]
expectedOutputs = [[0], [0], [0], [1]]

learningRate = 0.5

# create neuron indexes
neuronIndexes = []
inLayerIndexes = []
for i in range(inputLayerLength):
    inLayerIndexes.append(0)
neuronIndexes.append(inLayerIndexes)
for i in range(hiddenLayerAmount):
    currentLayerIndexes = []
    for j in range(hiddenLayerLengths):
        index = hiddenLayerLengths * i + j
        currentLayerIndexes.append(index)
    neuronIndexes.append(currentLayerIndexes)
outLayerIndexes = []
previousIndex = index
for i in range(outputLayerLength):
    outLayerIndexes.append(previousIndex + i + 1)
neuronIndexes.append(outLayerIndexes)

print("initWeights:", str(initWeights))
print("initBiases:", str(initBiases))
print("")

# initialize network
net = NeuralNet(myInputs[0], expectedOutputs[0], initBiases, initWeights)
newParams = net.biasesPlusWeights

# train network
trainCycles_amount = 1000
for x in range(trainCycles_amount):
    for inputs, outputs in zip(myInputs, expectedOutputs):
        net.runNetwork(newParams, inputs, outputs)
        net.findDeltas()
        newParams = net.new_biasesPlusWeights

        # retrieve output
        outputLayer_outputs = net.outputLayer_outputs
        print("NEURAL NET OUTPUT:", str(outputLayer_outputs[0]))
        print("correct output:", str(outputs))
        print("")

post_training_params = newParams
print("post-training parameters:", str(post_training_params))
