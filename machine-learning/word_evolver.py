import random
import string


class WordEvolver:
    def __init__(
        self, targetSpecies, maximumGenerationCount, generationSize, mutationRate
    ):
        self.target = targetSpecies
        self.maxGenerations = maximumGenerationCount
        self.generationSize = generationSize
        self.mutationRate = mutationRate
        self.targetLength = len(self.target)
        self.generationNumber = 1
        self.halt = False
        self.printRange = []
        for b in range(10):
            self.printRange.append(
                (b + 1) * ((self.targetLength ** 2) - ((self.targetLength - 1) ** 2))
            )

        self.createGeneration()

    def createGeneration(self):
        generation = []
        for i in range(self.generationSize):
            individual = ""
            for j in range(len(self.target)):
                individual += string.ascii_lowercase[random.randint(0, 25)]
            generation.append(individual)
        print("first generation: " + str(generation))
        # print('')
        self.evolve(generation)

    def evolve(self, childList):
        while self.halt == False:
            fitnessList = []
            for individual in childList:
                fitness = 0
                for indChar, targChar in zip(individual, self.target):
                    if indChar == targChar:
                        fitness += 1
                individualEval = [individual, fitness]
                fitnessList.append(individualEval)
            # print('fitnessList: '+str(fitnessList))
            # print('')

            # selection
            survivalList = []
            selectionSize = int(self.generationSize / 2)
            targetFitness = len(self.target)
            for i in range(targetFitness + 1):
                for individualEval in fitnessList:
                    fitness = individualEval[1]
                    individual = individualEval[0]
                    if (fitness == targetFitness - i) and (
                        individual not in survivalList
                    ):
                        survivalList.append(individual)
                    if len(survivalList) == selectionSize:
                        break
                if len(survivalList) == selectionSize:
                    break
            # print('survivalList: '+str(survivalList))
            # print('')

            # breed
            childList = []
            for i in range(len(survivalList)):
                parentIndex = 0
                while parentIndex == i:
                    parentIndex = random.randint(0, len(survivalList) - 1)
                mom = survivalList[i]
                dad = survivalList[parentIndex]
                crossoverPoint = random.randint(0, len(self.target) - 1)
                partA_mom = mom[0:crossoverPoint]
                partB_mom = mom[crossoverPoint : len(self.target)]
                partA_dad = dad[0:crossoverPoint]
                partB_dad = dad[crossoverPoint : len(self.target)]
                child1 = partA_mom + partB_dad
                childList.append(child1)
                if len(childList) == self.generationSize:
                    break
                child2 = partA_dad + partB_mom
                childList.append(child2)
                if len(childList) == self.generationSize:
                    break
            # print('breedList: '+str(childList))
            # print('')

            # mutation
            for j in range(int(self.targetLength / 5) + 1):
                for i in range(len(childList)):
                    if self.mutationRate > random.uniform(0.00, 1.00):
                        individual = childList[i]
                        del childList[i]
                        randIndex = random.randint(0, 25)
                        randChar = string.ascii_lowercase[randIndex]
                        characterIndex = random.randint(0, self.targetLength - 1)
                        mutatingCharacter = individual[characterIndex]
                        mutatedIndividual = individual.replace(
                            mutatingCharacter, randChar
                        )
                        childList.append(mutatedIndividual)
            # print('')
            # print('Species list: '+str(childList))

            # terminate Evolution
            self.generationNumber += 1
            if self.generationNumber in self.printRange:
                print("")
                print("generation number: " + str(self.generationNumber))
                print("Species list: " + str(childList))
            if self.generationNumber == self.maxGenerations:
                print("----------------- TERMINATING EVOLUTION -------------------")
                print("")
                print("Species list: " + str(childList))
                print("generation number: " + str(self.generationNumber))
                print("Maximum number of generations reached")
                self.halt = True
            elif self.target in childList:
                print("----------------- TERMINATING EVOLUTION -------------------")
                print("")
                print("generation number: " + str(self.generationNumber))
                print("Target Species Succesfully Evolved: " + self.target)
                self.halt = True


targetSpecies = "gameandmediatechnology"
maximumGenerationCount = 100000
mutationRate = 0.27
generationSize = 20

WordEvolver(targetSpecies.lower(), maximumGenerationCount, generationSize, mutationRate)

"""
bestMutations=[]
bestGenSizes=[]
for a in range(30):
    generationCounts=[]
    generationSizes=[]
    mutationRates=[]
    for k in range(10):
        mutationRate=round(0.05+k*.03,2)
        generationSize=6+k*2
        attempt=WordEvolver(targetSpecies,maximumGenerationCount,generationSize,mutationRate)

        mutationRates.append(mutationRate)
        generationSizes.append(generationSize)
        generationCounts.append(attempt.generationNumber)

    bestCount=min(generationCounts)
    bestIndex=generationCounts.index(bestCount)
    bestMutation=mutationRates[bestIndex]
    bestGenSize=generationSizes[bestIndex]
    
    bestMutations.append(bestMutation)
    bestGenSizes.append(bestGenSize)
    
    #print('mutationRates: '+str(mutationRates))
    #print('generationSizes: '+str(generationSizes))
    print('generationCounts: '+str(generationCounts))

averageMutationRate=sum(bestMutations)/float(len(bestMutations))
averageGenSize=float(sum(bestGenSizes))/float(len(bestGenSizes))

print('best mutationRate: '+str(averageMutationRate))
print('best generation size: '+str(averageGenSize))
"""
