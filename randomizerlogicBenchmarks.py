import unittest
from timeit import default_timer as timer
from unittest.mock import patch
import random
from logic import randomizerlogic as logic, requirementcalculations as calc


class MyTestCase(unittest.TestCase):

    def test_mapFileReduction_loop(self):
        iterations = 10 ** 3 * 5
        map = "logic/test_loop.csv"
        matrix, labels = calc.readTable(map)
        print("Testing with " + map)
        start = timer()
        for i in range(iterations):
            calc.reduceRequirementTable(matrix, labels, labels, None, False)
        end = timer()
        print("Total run time (" + str(iterations) + " iterations): " + str(end-start) + "s")
        print("Time per execution: " + str((end-start)/iterations) + "s\n\n")

    def test_mapFileReduction_towers(self):
        iterations = 10 ** 3 * 5
        map = "logic/test_towers.csv"
        matrix, labels = calc.readTable(map)
        print("Testing with " + map)
        start = timer()
        for i in range(iterations):
            calc.reduceRequirementTable(matrix, labels, labels, None, False)
        end = timer()
        print("Total run time (" + str(iterations) + " iterations): " + str(end-start) + "s")
        print("Time per execution: " + str((end-start)/iterations) + "s\n\n")

    def test_mapFileReduction_standard(self):
        iterations = 0
        if iterations <= 0:
            return
        map = "logic/standard.csv"
        matrix, labels = calc.readTable(map)
        print("Testing with " + map)
        start = timer()
        for i in range(iterations):
            calc.reduceRequirementTable(matrix, labels, labels, None, False)
        end = timer()
        print("Total run time (" + str(iterations) + " iterations): " + str(end-start) + "s")
        print("Time per execution: " + str((end-start)/iterations) + "s")

    def test_calculateTotalRequirements(self):

        reqs = generateRandomRequirements(7)
        print(len(reqs))

def generateRandomRequirements(nrRequirements):
    baseSets = [[]]
    for i in range(nrRequirements):
        for j in range(len(baseSets)):
            baseSets += [baseSets[j] + [i+1]]
    resultSets = [[i] for i in baseSets]
    if nrRequirements >= 2:
        currentSets = resultSets
        for i in range(nrRequirements-1):
            print(f"{i+1}/{nrRequirements-1}")
            currentSets = combineSets(currentSets, baseSets)
            newRes = [[]] * len(currentSets)
            counter = 0
            for item in currentSets:
                if not item in newRes:
                    newRes[counter] = item
                    counter += 1
            currentSets = newRes[0:counter]
            resultSets += currentSets

    return resultSets

def combineSets(requirementSets, baseReqs):
    newReqs = [[]] * (len(requirementSets) ** 2)
    counter = 0
    for j in range(len(requirementSets)):
        for m in range(len(baseReqs)):
            testNewReq = requirementSets[j] + [baseReqs[m]]
            testNewReqBits = convertToRequirementBits(testNewReq)
            if sorted(testNewReqBits) == testNewReqBits and (testNewReqBits == calc.reduceReqs(testNewReqBits)[0]):
                newReqs[counter] = testNewReq
                counter += 1

    return newReqs[0:counter]


def convertToRequirementBits(requirementSets):
    if len(requirementSets) == 0 or isinstance(requirementSets[0], int):
        return __convertToRequirementBits(requirementSets)

    ret = []
    for requirementSet in requirementSets:
        ret += [convertToRequirementBits(requirementSet)]

    return ret

def __convertToRequirementBits(requirements):
    value = 0
    for req in requirements:
        value += 2 ** (req-1)

    return value

if __name__ == '__main__':
    unittest.main()
