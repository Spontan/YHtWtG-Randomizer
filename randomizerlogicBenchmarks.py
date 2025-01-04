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
            calc.reduceRequirementTable(matrix, labels, None, None, False, 0, False)
        end = timer()
        print("Total run time (" + str(iterations) + " iterations): " + str(end-start) + "s")
        print("Time per execution: " + str((end-start)/iterations) + "s")

    def test_mapFileReduction_standard_grouped(self):
        iterations = 5
        if iterations <= 0:
            return
        map = "logic/standard.csv"
        matrix, labels = util.readTable(map)
        print("Testing with " + map)
        start = timer()
        for i in range(iterations):
            calc.reduceRequirementTable(matrix, labels, None, None, False, 1, False)
        end = timer()
        print("Total run time (" + str(iterations) + " iterations): " + str(end-start) + "s")
        print("Time per execution: " + str((end-start)/iterations) + "s")

    def test_mapFileReduction_standard_grouped2(self):
        iterations = 5
        if iterations <= 0:
            return
        map = "logic/standard.csv"
        matrix, labels = util.readTable(map)
        print("Testing with " + map)
        start = timer()
        for i in range(iterations):
            calc.reduceRequirementTable(matrix, labels, None, None, False, 2, False)
        end = timer()
        print("Total run time (" + str(iterations) + " iterations): " + str(end-start) + "s")
        print("Time per execution: " + str((end-start)/iterations) + "s")

    def test_mapFileReduction_standard_parallel(self):
        iterations = 5
        if iterations <= 0:
            return
        map = "logic/standard.csv"
        matrix, labels = util.readTable(map)
        print("Testing with " + map)
        start = timer()
        for i in range(iterations):
            calc.reduceRequirementTable(matrix, labels, None, None, False, 0, True)
        end = timer()
        print("Total run time (" + str(iterations) + " iterations): " + str(end-start) + "s")
        print("Time per execution: " + str((end-start)/iterations) + "s")

    def test_mapFileReduction_standard_grouped_parallel(self):
        iterations = 5
        if iterations <= 0:
            return
        map = "logic/standard.csv"
        matrix, labels = util.readTable(map)
        print("Testing with " + map)
        start = timer()
        for i in range(iterations):
            calc.reduceRequirementTable(matrix, labels, None, None, False, 1, True)
        end = timer()
        print("Total run time (" + str(iterations) + " iterations): " + str(end-start) + "s")
        print("Time per execution: " + str((end-start)/iterations) + "s")

if __name__ == '__main__':
    unittest.main()
