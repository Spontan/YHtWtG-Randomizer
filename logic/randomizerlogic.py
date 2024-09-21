from enum import Enum
import random
from logic import requirementcalculations as calc

DEFAULT_SPAWN = 27
DEFAULT_END = 43
DEFAULT_BLUE_ORB = 3
DEFAULT_RED_ORB = 63
DEFAULT_BOOTS = 31
DEFAULT_GLOVES = 69
EXCLUDED_SPAWN_LOCATIONS = [9, 14, 19, 21, 23, 28, 42, 47, 57, 65, 66]

class TpShuffleMode(Enum):
    NORMAL = 0
    SHUFFLE_EXITS = 1
    SHUFFLE_ENTRYS = 2
    SHUFFLE_BOTH = 3

class TPShuffleAmount(Enum):
    REGULAR = 0
    MORE = 1
    ALL = 2

class DifficultyOptions(object):
    startWithBlueOrb = False
    startWithRedOrb = False
    startWithBoots = False
    startWithGloves = False
    spikeJumps = False
    tripleJumps = False
    extendedJumps = False

    def __str__(self):
        return (f'Spike Jumps: {self.spikeJumps}\n'
                f'Triple Jumps: {self.tripleJumps}\n'
                f'Extended Jumps: {self.extendedJumps}\n'
                f'Blue Orb: {self.startWithBlueOrb}\n'
                f'Red Orb: {self.startWithRedOrb}\n'
                f'Boots: {self.startWithBoots}\n'
                f'Gloves: {self.startWithGloves}\n')

    def toRequirementValue(self):
        return 1 * self.startWithBlueOrb + \
            2 * self.startWithRedOrb + \
            4 * self.startWithBoots + \
            8 * self.startWithGloves + \
            16 * self.spikeJumps + \
            32 * self.tripleJumps + \
            64 * self.extendedJumps

    def setFromRequirementValue(self, value):
        self.startWithBlueOrb = bool(value & 1)
        self.startWithRedOrb = bool(value & 2)
        self.startWithBoots = bool(value & 4)
        self.startWithGloves = bool(value & 8)
        self.spikeJumps = bool(value & 16)
        self.tripleJumps = bool(value & 32)
        self.extendedJumps = bool(value & 64)


class RandomizerOptions(object):
    shuffleSpawn = False
    requireAllOrbs = False
    tpMode = TpShuffleMode.NORMAL           #TODO: Not supported yet
    tpAmount = TPShuffleAmount.REGULAR      #TODO: Not supported yet
    hideTps = False                         #TODO: Not supported yet
    hidePowerups = False                    #TODO: Not supported yet
    seed = None
    difficultyOptions = DifficultyOptions()


def selectSpawnState(options):
    startRequirements = options.difficultyOptions.toRequirementValue()
    spawnLocation = selectSpawnLocation(options.shuffleSpawn)
    return (spawnLocation, startRequirements)

def selectSpawnLocation(shuffleSpawn, nrLocs=71, excludeLocs=[43]):
    """
    Selects a valid spawn location
    TODO: add spawn shuffle functionality
    :param shuffleSpawn: Whether or not the spawn location should be shuffled with treasures
    :return: The spawn location to use
    """
    if excludeLocs is None:
        excludeLocs = []
    if shuffleSpawn:
        return selectRandomLocation(nrLocs, excludeLocs + EXCLUDED_SPAWN_LOCATIONS)
    else:
        return DEFAULT_SPAWN


def selectOrbLocations(nrLocs=71, excludeLocs=[27, 43], difficultyOptions = DifficultyOptions()):
    """
    Selects a random set of unique locations for the orbs.
    :param nrLocs:
    :param excludeLocs: Locations which should be excluded as orb locations (e.g. spawn and end)
    :param difficultyOptions: Can be used to leave out orbs so they can be given to the player at the spawn location
    :return:
    """
    orbs = [-1, -1, -1, -1]
    if not difficultyOptions.startWithBlueOrb:
        orbs[0] = selectRandomLocation(nrLocs, excludeLocs)
        excludeLocs += [orbs[0]]
    if not difficultyOptions.startWithRedOrb:
        orbs[1] = selectRandomLocation(nrLocs, excludeLocs)
        excludeLocs += [orbs[1]]
    if not difficultyOptions.startWithBoots:
        orbs[2] = selectRandomLocation(nrLocs, excludeLocs)
        excludeLocs += [orbs[2]]
    if not difficultyOptions.startWithGloves:
        orbs[3] = selectRandomLocation(nrLocs, excludeLocs)
        excludeLocs += [orbs[3]]

    return orbs

def selectRandomLocation(nrLocs = 71, excludeLocs = []):
    while len(excludeLocs) < nrLocs:
        loc = random.randint(0, nrLocs-1)
        if loc not in excludeLocs:
            return loc
    return -1

def selectEndLocation():
    return DEFAULT_END

def generateRandomSeed(options):
    if not isinstance(options, RandomizerOptions):
        print(f"options needs to be RandomizerOptions but was {type(options)}, using default options instead")
        options = RandomizerOptions()

    random.seed(options.seed)

    connectionTable, labels = calc.readTable("logic/reduced_map.csv")
    if options.requireAllOrbs:
        for row in connectionTable:
            row[DEFAULT_END] = [15]

    while True:
        spawnState = selectSpawnState(options)
        endLocation = selectEndLocation()
        orbLocations = selectOrbLocations(excludeLocs=[spawnState[0], endLocation], difficultyOptions=options.difficultyOptions)

        solution = findSolution(connectionTable, spawnState, orbLocations, endLocation)

        if solution:
            #print(f'spots: {orbLocations}, spawn: {spawnState}')
            #print(f'spotsNames: {[labels[i] for i in orbLocations]}, spawn: {(labels[spawnState[0]],spawnState[1])}')
            break

    return spawnState, orbLocations

def isLocationInList(locationList, location):
    for loc in locationList:
        if loc[0] == location:
            return True

    return False

def getLocationRequirements(locationList, filterList):
    """
    Retrieves the requirements to reach a subset of locations
    :param locationList: The full location list
    :param filterList: The subset for which the requirements should be returned
    """
    locReqList = []
    for filterIndex in filterList:
        locReqList += [(filterIndex, locationList[filterIndex])]

    return locReqList

def getReachableLocs(locationList, fulfilledRequirements):
    """
    Returns the locations for which the necessary requirements are fulfilled
    :param locationList: List of locations to check
    :param fulfilledRequirements: Requirements which can be fulfilled
    :return: The reachable locations (combined with the fulfilled requirements)
    """
    reachableLocs = []
    for loc in locationList:
        requirements = loc[1]
        if fulfillsRequirements(requirements, fulfilledRequirements):
            reachableLocs += [(loc[0], fulfilledRequirements)]

    return reachableLocs

def fulfillsRequirements(reqList, fulfilledReqs):
    """
    Checks if a requirement value fulfills any of the requirements in a given list
    :param reqList: The list of possible requirements
    :param fulfilledReqs: The requirement value to check against the list
    """
    for req in reqList:
        if not req & ~ fulfilledReqs:
            return True

    return False

def updateStates(locList, orbLocs, excludeLocs):
    """
    For a given list of location states adds the requirement for a powerup if the location is an orb location
    and removes location in the excluded list
    :param locList: The list of location states
    :param orbLocs: The list of orb locations
    :param excludeLocs: The list of excluded locations
    """
    newLocs = []
    for i in range(len(locList)):
        loc = addPower(locList[i], orbLocs)
        if loc not in excludeLocs:
            newLocs += [loc]
    return newLocs

def addPower(loc, orbLocs):
    """
    Adds the requirement fulfilled by a powerup to the given location state and returns it
    :param loc: The location state to check
    :param orbLocs: The list of orb locations
    :return: The updated location state
    """
    for i in range(len(orbLocs)):
        if loc[0] == orbLocs[i]:
            return (loc[0], loc[1] | 2 ** i)
    return loc

def findSolution(table, spawn, orbs, end):
    """
    Tries to find path from the spawn to the end location by checking repeatedly if either the end is reachable directly
    or a new orb can be reached (and the corresponding powerup is picked up). This is done using depth-first search
    through all states which can be reached that way
    TODO: return the path to the end
    :param table: logic graph
    :param spawn: Index of the spawn location
    :param orbs: Indices of the orb locations
    :param end: Index of the end location
    :return: True if the end can be reached from the spawn, False otherwise
    """
    currentLocations = [spawn]
    visitedLocations = []
    solution = None
    while not isLocationInList(currentLocations, end) and len(currentLocations) > 0:
        #print(currentLocations)
        loc = currentLocations.pop()
        visitedLocations += [loc]

        filteredLocs = getLocationRequirements(table[loc[0]], orbs + [end])

        reachableLocs = getReachableLocs(filteredLocs, loc[1])

        currentLocations += updateStates(reachableLocs, orbs, visitedLocations)

    return len(currentLocations) > 0
