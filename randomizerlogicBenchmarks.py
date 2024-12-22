import unittest
from timeit import default_timer as timer
from unittest.mock import patch
import random
from logic import randomizerlogic as logic, requirementcalculations as calc, util


class MyTestCase(unittest.TestCase):

    def test_mapFileReduction_loop(self):
        iterations = 10 ** 3 * 5
        map = "logic/test_loop.csv"
        matrix, labels = util.readTable(map)
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
        matrix, labels = util.readTable(map)
        print("Testing with " + map)
        start = timer()
        for i in range(iterations):
            calc.reduceRequirementTable(matrix, labels, labels, None, False)
        end = timer()
        print("Total run time (" + str(iterations) + " iterations): " + str(end-start) + "s")
        print("Time per execution: " + str((end-start)/iterations) + "s\n\n")

    def test_mapFileReduction_standard(self):
        iterations = 5
        if iterations <= 0:
            return
        map = "logic/standard.csv"
        matrix, labels = util.readTable(map)
        print("Testing with " + map)
        start = timer()
        for i in range(iterations):
            calc.reduceRequirementTable(matrix, labels, None, None, False)
        end = timer()
        print("Total run time (" + str(iterations) + " iterations): " + str(end-start) + "s")
        print("Time per execution: " + str((end-start)/iterations) + "s")

if __name__ == '__main__':
    unittest.main()
