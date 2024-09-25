from enum import Enum
import random
from logic import util, requirementcalculations as calc

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


class Entity(object):
    def __init__(self, room=(0, 0), position=(156, 92)):
        self.room = room
        self.position = position  # Default position is at the center of the screen


class Treasure(Entity):
    def __init__(self, type='cash', room=(0, 0), position=(156, 92)):
        super().__init__(room, position)
        self.type = type


class Teleporter(Entity):
    def __init__(self, id, room=(0, 0), position=(156, 92), destinationRoom=(0, 2), destinationPosition=(160, 112)):
        super().__init__(room, position)
        self.id = id
        self.destinationRoom = destinationRoom
        self.destinationPosition = destinationPosition  # Default destination is at "Which Path Will I Take"


DEFAULT_TELEPORTERS = {'B': Teleporter('B', (-7, 3), (120, 160), (-9, 4), (304, 64)),
                       'F': Teleporter('F', (-6, 4), (192, 32), (-9, 4), (304, 64,)),
                       'A1': Teleporter('A1', (-3, 4), (80, 104), (-3, 4), (176, 104)),
                       'A2': Teleporter('A2', (-3, 4), (160, 103), (-3, 4), (64, 104)),
                       'I': Teleporter('I', (-2, -2), (24, 160), (-1, -3), (200, 104)),
                       'C': Teleporter('C', (-2, 5), (288, 88), (0, 2), (160, 112)),
                       'K': Teleporter('K', (-1, -3), (296, 144), (0, -3), (24, 152)),
                       'J': Teleporter('J',(-1, -2), (296, 144), (0, -2), (24, 152)),
                       'L': Teleporter('L', (0, -3), (296, 144), (-3, 0), (24, 144)),
                       'G': Teleporter('G', (2, 1), (88, 104), (6, 4), (24, 24)),
                       'E': Teleporter('E', (3, 5), (40, 72), (0, 2), (160, 112)),
                       'H': Teleporter('H', (7, 3), (160, 32), (0, 2), (160, 112)),
                       'D': Teleporter('D', (8, 2), (32, 32), (6, 1), (16, 160))}


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


class RandomizedMap(object):
    def __init__(self,spawnState = (DEFAULT_SPAWN, DifficultyOptions().toRequirementValue()),
                 orbLocations=None,
                 teleporters=None):
        if teleporters is None:
            teleporters = DEFAULT_TELEPORTERS
        if orbLocations is None:
            orbLocations = [DEFAULT_BLUE_ORB, DEFAULT_RED_ORB, DEFAULT_BOOTS, DEFAULT_GLOVES]
        self.spawnState = spawnState
        self.orbLocations = orbLocations
        self.teleporters = teleporters




class RandomizerOptions(object):
    shuffleSpawn = False
    requireAllOrbs = False
    tpMode = TpShuffleMode.NORMAL  # TODO: Not supported yet
    tpAmount = TPShuffleAmount.REGULAR  # TODO: Not supported yet
    hideTps = False  # TODO: Not supported yet
    hidePowerups = False  # TODO: Not supported yet
    seed = None
    difficultyOptions = DifficultyOptions()


def selectSpawnState(options):
    startRequirements = options.difficultyOptions.toRequirementValue()
    spawnLocation = selectSpawnLocation(options.shuffleSpawn)
    return (spawnLocation, startRequirements)


def selectSpawnLocation(shuffleSpawn, nrLocs=71, excludeLocs=[43]):
    """
    Selects a valid spawn location
    :param shuffleSpawn: Whether or not the spawn location should be shuffled with treasures
    :return: The spawn location to use
    """
    if excludeLocs is None:
        excludeLocs = []
    if shuffleSpawn:
        return selectRandomLocation(nrLocs, excludeLocs + EXCLUDED_SPAWN_LOCATIONS)
    else:
        return DEFAULT_SPAWN


def selectOrbLocations(nrLocs=71, excludeLocs=[27, 43], difficultyOptions=DifficultyOptions()):
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


def selectRandomLocation(nrLocs=71, excludeLocs=[]):
    while len(excludeLocs) < nrLocs:
        loc = random.randint(0, nrLocs - 1)
        if loc not in excludeLocs:
            return loc
    return -1


def selectEndLocation():
    return DEFAULT_END


def setAllOrbsEndTp(teleporterEntities):
    regularEndRoom = DEFAULT_TELEPORTERS['J'].destinationRoom
    for e in teleporterEntities:
        if e.destinationRoom == regularEndRoom:
            e.destinationRoom = (1, -2)

def getTpEntity(entryId, exitId):
    entry = DEFAULT_TELEPORTERS[entryId]
    exit = DEFAULT_TELEPORTERS[exitId]

    return Teleporter(entryId, entry.room, entry.position, exit.destinationRoom, exit.destinationPosition)

def generateRandomSeed(options):
    if not isinstance(options, RandomizerOptions):
        print(f"options needs to be RandomizerOptions but was {type(options)}, using default options instead")
        options = RandomizerOptions()

    random.seed(options.seed)
    matrix, labels = util.readTable("logic/standard.csv")
    tpEntries = []
    tpExits = []
    for i in range(len(labels)):
        if labels[i].startswith('"TP-Entry'):
            id = labels[i].split(':',1)[0][10:]
            tpEntries += [(id,i)]
        if labels[i].startswith('"TP-Exit'):
            id = labels[i].split(':', 1)[0][9:]
            tpExits += [(id, i)]
    print(f'Entries: {len(tpEntries)}, Exits: {len(tpExits)}')
    for i in tpEntries:
        for j in tpExits:
            util.removeConnection(matrix, i[1], j[1])

    tpExitsCopy = tpExits.copy()

    teleporterEntities = []

    for i in range(len(tpEntries)):
        entry = tpEntries[i]
        j = random.randint(0, len(tpExitsCopy) - 1)
        exit = tpExitsCopy[j]
        util.editConnectionValue(matrix, entry[1], exit[1], [0])
        del(tpExitsCopy[j])

        teleporterEntities += [getTpEntity(entry[0], exit[0])]

    if options.requireAllOrbs:
        setAllOrbsEndTp(teleporterEntities)

    connectionTable, labels = calc.reduceRequirementTable(matrix, labels)

    # connectionTable, labels = util.readTable("logic/reduced_map.csv")
    if options.requireAllOrbs:
        for row in connectionTable:
            row[DEFAULT_END] = [15]

    while True:
        spawnState = selectSpawnState(options)
        endLocation = selectEndLocation()
        orbLocations = selectOrbLocations(excludeLocs=[spawnState[0], endLocation],
                                          difficultyOptions=options.difficultyOptions)

        solution = findSolution(connectionTable, spawnState, orbLocations, endLocation)

        if solution:
            # print(f'spots: {orbLocations}, spawn: {spawnState}')
            # print(f'spotsNames: {[labels[i] for i in orbLocations]}, spawn: {(labels[spawnState[0]],spawnState[1])}')
            break

    return RandomizedMap(spawnState, orbLocations, teleporterEntities)


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
        # print(currentLocations)
        loc = currentLocations.pop()
        visitedLocations += [loc]

        filteredLocs = getLocationRequirements(table[loc[0]], orbs + [end])

        reachableLocs = getReachableLocs(filteredLocs, loc[1])

        currentLocations += updateStates(reachableLocs, orbs, visitedLocations)

    return len(currentLocations) > 0
