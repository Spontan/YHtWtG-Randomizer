from threading import Thread
from typing import List
from timeit import default_timer as timer

import logic.equivalencegroup as eq

DEFAULT_SPAWN = "You Have to Start the Game Spawn"
DEFAULT_REDORB = "Crimson Aura Pickup"
DEFAULT_BLUEORB = "Cerulean Aura Pickup"
DEFAULT_BOOTS = "Springheel Boots Pickup"
DEFAULT_GLOVES = "Spider Gloves Pickup"
DEFAULT_LOSE = "Consolation Prize Pickup-1"
DEFAULT_WIN = "Eponymous Pickup"
REQUIREMENTS_COUNT = 7
REQUIREMENTS_SIZE = 1 << (REQUIREMENTS_COUNT)
REQUIREMENT_POWERSET_SIZE = 1 << REQUIREMENTS_COUNT * (REQUIREMENTS_COUNT-1) #Number of possible requirement sets
SQUARED_REQUIREMENT_POWERSET_SIZE = REQUIREMENT_POWERSET_SIZE ** 2  #Number of possible combinations of requirement sets
calculateTotalRequirementsDict = {}
reduceReqsDict = {}

class pathfindersettings(object):
    """
    Defines the settings the path-finder should use. Mostly related to optimization. Defaults are set to work best with
    the standard map on benchmark tests
    """
    def __init__(self):
        self.useParallelProcessing: bool = False
        self.useDynamicProgramming: bool = True
        self.groupingSteps: List[int] = [0, 1]
        self.returnFoundPaths: bool = False
        self.verbose: bool = False

    def setParallelProcessingEnabled(self, enabled: bool):
        """
        Enables or disables multi-threading for calculations
        """
        self.useParallelProcessing = enabled

    def setDynamicProgrammingEnabled(self, enabled: bool):
        """
        Enables or disables reusing partial results where possible
        """
        self.useDynamicProgramming = enabled

    def setGroupingSteps(self, groupingSteps: List[int]):
        """
        For each number in the list iterates that many times before grouping states that can reach each other
        for free (no requirements). To disable grouping provide an empty list
        """
        self.groupingSteps = groupingSteps

    def setReturnFoundPaths(self, enabled: bool):
        """
        If enabled the path-finder will also keep track of and return the shortest paths found for each unique set
        of requirements
        """
        self.returnFoundPaths = enabled

    def setVerboseOutputs(self, enabled: bool):
        """
        Gives verbose log outputs if enabled
        """
        self.verbose = enabled
class pathfinder(object):
    def __init__(self, settings: pathfindersettings):
        if settings == None:
            self.settings = pathfindersettings()
        else:
            self.settings = settings

    def reduceRequirementTable(self, matrix, labels, reducedLocations=None):
        """
        Calculates requirements to reach any location on the map from any other location and returns the entries for
        the given set of locations. Can be used to precalculate the connections between all pickup locations + other
        relevant locations (spawn, end, teleporter, etc.)
        :param matrix: Location graph matrix
        :param labels: Full list of Location names
        :param reducedLocations: List of relevant locations
        :param pathsMatrix: Debug option, providing an empty matrix enables debug mode. After returning, the matrix contains
                    all paths the algorithm found.
        """
        if reducedLocations == None:
            reducedLocations = getTreasureLocations(labels)


        reducedIndex = findSubIndex(labels, reducedLocations)
        startTimingBlock = timer()  # Grouping stage start
        processMatrix, startPositions, indexToGroupMapping = self.groupingStage(matrix, reducedIndex)
        endTimingBlock = timer()    # Grouping stage end
        if self.settings.verbose:
            print(f'State grouping took {endTimingBlock - startTimingBlock}s')
            print('Starting path-finding stage')
            print(f'(0/{len(startPositions)})')

        nonEmptyMatrixEntries = calculateNonEmptyMatrixEntries(processMatrix)
        outputTable = [[] for _ in range(len(startPositions))]
        if self.settings.useParallelProcessing:
            threadList: List[WorkerThread] = []
            for i in range(len(startPositions)):
                initialState = processMatrix[startPositions[i]]
                thread = WorkerThread(processMatrix, initialState, nonEmptyMatrixEntries, None)
                thread.start()
                threadList += [thread]
            for i in range(len(startPositions)):
                threadList[i].join()
                outputTable[i] = [threadList[i].finalState[x] for x in startPositions]
                if printProgress:
                    print(f'({i + 1}/{len(startPositions)})')
                if debugMode:
                    pathsMatrix.append(None)
        else:
            for i in range(len(startPositions)):
                initialState = processMatrix[startPositions[i]]
                finalState = findFinalState(processMatrix, initialState, nonEmptyMatrixEntries, None)
                outputTable[i] = [finalState[x] for x in startPositions]
                if printProgress:
                    print(f'({i + 1}/{len(startPositions)})')
                if debugMode:
                    pathsMatrix.append(None)

        reducedTable = [[[] for _ in range(len(reducedLocations))] for _ in range(len(reducedLocations))]
        if groupingDegree > 0:
            for i in range(len(reducedIndex)):
                for j in range(len(reducedIndex)):
                    reducedTable[i][j] = outputTable[indexToGroupMapping[i]][indexToGroupMapping[j]]
        else:
            reducedTable = outputTable

        return reducedTable, reducedLocations

    def groupingStage(self, matrix, reducedIndex):
        processMatrix = matrix
        reducedGroups = reducedIndex
        indexToGroupMapping = [i for i in range(len(reducedIndex))]
        for iterations in self.settings.groupingSteps:
            preprocessedMatrix = [row for row in processMatrix]
            nonEmptyMatrixEntries = calculateNonEmptyMatrixEntries(preprocessedMatrix)
            for _ in range(1, iterations):
                for i in range(len(preprocessedMatrix)):
                    preprocessedMatrix[i] = iterate(matrix, preprocessedMatrix[i], nonEmptyMatrixEntries, None, None)[0]
            processMatrix = preprocessedMatrix

            equivalenceGrouping = eq.EquivalenceGroup(processMatrix)
            newReducedGroups = []
            newIndexToGroupMapping = []
            for i in range(len(reducedGroups)):
                newGroup = equivalenceGrouping.groupMembership[reducedGroups[i]]
                try:
                    newIndexToGroupMapping += [newReducedGroups.index(newGroup)]
                except ValueError:
                    newIndexToGroupMapping += [len(newReducedGroups)]
                    newReducedGroups += [newGroup]
            processMatrix = equivalenceGrouping.groupMatrix
            reducedGroups = newReducedGroups
            indexToGroupMapping = [newIndexToGroupMapping[oldMapping] for oldMapping in indexToGroupMapping]
            if self.settings.verbose:
                print(f'#groups: {len(equivalenceGrouping.groups)}, #start positions: {len(reducedGroups)}')

        return processMatrix, reducedGroups, indexToGroupMapping


def getInitialState(locationList, startLocation):
    """
    Creates an initial state for the iterate function
    """
    return [[] for _ in range(startLocation)] + [[0]] + [[] for _ in range(len(locationList)-startLocation-1)]

def getEmptyPathVector(locationList, startLocation):
    """
    Creates an empty path vector for debugging the iterate function and connection matrix
    """
    return [{} for _ in range(startLocation)] + [{0: -1}] + [{} for _ in range(len(locationList) - startLocation - 1)]

def findPoIs(locations):
    """
    Returns all locations which are not just room edges (Points of interest)
    """
    return [loc for loc in locations if not (loc.endswith("Top") or loc.endswith("Right") or loc.endswith("Bottom") or loc.endswith("Left") or loc.endswith("Middle"))]


def getTreasureLocations(locations):
    """
    Returns all locations where treasures can spawn
    """
    return [loc for loc in locations if loc.startswith("\"Pickup:") or loc.startswith("\"Spawn:")]

def findSubIndex(fullList, subList):
    """
    Helper method to select a subset from a row in the matrix
    """
    return [index for index in range(len(fullList)) if fullList[index] in subList]  # Could be optimized using the assumption that both lists are sorted

def calculateNonEmptyMatrixEntries(matrix):
    return [[j for j in range(len(matrix)) if row[j]] for row in matrix]

class WorkerThread(Thread):
    def __init__(self, matrix, initialState, nonEmptyMatrixEntries, paths):
        super().__init__()
        self.matrix = matrix
        self.initialState = initialState
        self.nonEmptyMatrixEntries = nonEmptyMatrixEntries
        self.paths = paths
    def run(self) -> None:
        self.finalState = findFinalState(self.matrix, self.initialState, self.nonEmptyMatrixEntries, self.paths)
        