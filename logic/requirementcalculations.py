DEFAULT_SPAWN = "You Have to Start the Game Spawn"
DEFAULT_REDORB = "Crimson Aura Pickup"
DEFAULT_BLUEORB = "Cerulean Aura Pickup"
DEFAULT_BOOTS = "Springheel Boots Pickup"
DEFAULT_GLOVES = "Spider Gloves Pickup"
DEFAULT_LOSE = "Consolation Prize Pickup-1"
DEFAULT_WIN = "Eponymous Pickup"
REQUIREMENTS_COUNT = 7
calculateTotalRequirementsDict = {}
reduceReqsDict = {}


def prepareReducedMapFile(inFile = "standard.csv", outFile = "reduced_map.csv"):
    table, labels = readTable(inFile)
    writeTable(outFile, reduceRequirementTable(table, labels))

def readTable(file):
    """
    Reads the logic graph matrix and the location labels from a file.
    """
    nrRows = 0
    nrCols = 0
    with open(file) as tableFile:
        nrCols = tableFile.readline().count(";")
        for line in tableFile:
            if line.strip():
                nrRows += 1

    if nrCols != nrRows:
        print("Table has to have the same number of rows and columns")
        return []

    table = [[[] for _ in range(nrRows)] for _ in range(nrCols)]
    labels = ["" for _ in range(nrCols)]

    with open(file) as tableFile:
        tableFile.readline()

        row = 0
        for line in tableFile:
            if not line.strip():
                continue

            lineSplits = line.split(";")
            labels[row] = lineSplits[0]
            lineSplits = lineSplits[1:]
            for col in range(len(lineSplits)):
                entries = lineSplits[col].split(",")
                for entry in entries:
                    if entry.strip() and int(entry) >= 0:
                        table[row][col] += [int(entry)]
            row += 1
    return table, labels


def writeTable(writeFile, matrix, locationNames=None):
    """
    Writes a logic graph matrix to a file. Optionally allows writing location names as well.
    """
    if isinstance(locationNames, str):
        stateNames = getStateListFromFile(locationNames)
    with open(writeFile, 'w') as writeFile:
        if len(locationNames) > 0:
            writeFile.write(";" + getTableLine(locationNames))
            writeFile.write("\n")

        for i in range(len(matrix)):
            if len(locationNames) > i:
                line = [locationNames[i]] + matrix[i]
            else:
                line = [""] + matrix[i]
            writeFile.write(getTableLine(line))
            writeFile.write("\n")


def getTableLine(entries):
    """
    Helper for writing the matrix to a file
    """
    writeLine = ""
    if len(entries) == 0:
        print("no entries to write")
        return ""

    writeLine += getTableEntry(entries[0])
    if len(entries) > 1:
        for entry in entries[1:]:
            writeLine += ";" + getTableEntry(entry)

    return writeLine


def getTableEntry(entry):
    """
    Helper for writing the matrix to a file
    """
    writeReq = ""
    if len(entry) == 0:
        return ""

    if isinstance(entry, str):
        if entry.startswith("\"") and entry.endswith("\""):
            return entry
        else:
            return "\"" + entry + "\""

    writeReq += str(entry[0])
    if len(entry) == 1:
        return writeReq

    for req in entry[1:]:
        writeReq += "," + str(req)

    return writeReq


def getStateListFromFile(stateNameFile):
    """
    Reads the location names from a file (usually a location graph matrix file).
    Probably not needed anymore since readTable also returns the location names
    """
    stateNames = []
    with open(stateNameFile) as readFile:
        firstLineSplits = readFile.readline().split(";")
        while len(firstLineSplits) > 0 and not firstLineSplits[0].strip():
            firstLineSplits = firstLineSplits[1:]
        if not (len(firstLineSplits) > 0 and not firstLineSplits[0].isnumeric()):
            return stateNames

        for split in firstLineSplits:
            stateNames = stateNames + [split.replace("\"", "").replace("\n", "")]


    return stateNames

def getInitialState(locationList, startLocation = DEFAULT_SPAWN, debug = False):
    """
    Creates an initial state for the iterate function
    """
    startLocationPosition = locationList.index(startLocation)
    if debug:
        paths = [{} for _ in range(startLocationPosition)] + [{0: -1}] + [{} for _ in range(len(locationList)-startLocationPosition-1)]
    else:
        paths = None
    return [[] for _ in range(startLocationPosition)] + [[0]] + [[] for _ in range(len(locationList)-startLocationPosition-1)], paths

def findPoIs(locations):
    """
    Returns all locations which are not just room edges
    """
    pois = []
    for loc in locations:

        if not (loc.endswith("Top") or loc.endswith("Right") or loc.endswith("Bottom") or loc.endswith("Left") or loc.endswith("Middle")):
            pois += [loc]

    return pois

def reduceRequirementTable(table, labels, reducedLocations = None, pathsMatrix = None, printProgress = True):
    """
    Calculates requirements to reach any location on the map from any other location and returns the entries for
    the given set of locations. Can be used to precalculate the connections between all pickup locations + other
    relevant locations (spawn, end, teleporter, etc.)
    :param table: Location graph matrix
    :param labels: Full list of Location names
    :param reducedLocations: List of relevant locations
    :param pathsMatrix: Debug option, providing an empty matrix enables debug mode. After returning, the matrix contains
                all paths the algorithm found.
    """
    if reducedLocations == None:
        reducedLocations = []
        for label in labels:
            if label.startswith("\"Pickup:") or label.startswith("\"Spawn:"):
                reducedLocations += [label]

    reducedTable = [[] for _ in range(len(reducedLocations))]
    reducedIndex = findSubIndex(labels, reducedLocations)

    debugMode = pathsMatrix != None
    if printProgress:
        print(f'(0/{len(reducedLocations)})')
    for i in range(len(reducedLocations)):
        startLocation = reducedLocations[i]
        initialState, paths = getInitialState(labels, startLocation, debugMode)
        finalState = findFinalState(table, initialState, paths)
        reducedTable[i] = [finalState[x] for x in reducedIndex]
        if printProgress:
            print(f'({i+1}/{len(reducedLocations)})')
        if debugMode:
            pathsMatrix.append(paths)

    return reducedTable, reducedLocations

def findFinalState(matrix, initialState, paths = None):
    """
    Calculates requirements to reach all locations on the map from an initial state. Repeatedly takes one step along
    all edges of the requirement graph until nothing changes anymore.
    :param matrix: The location graph matrix
    :param initialState: Usually should just have the start location set to [0] and the rest to []
    :param paths: Debug option to retrieve the actual paths found to each location
    :return: The complete list of requirements for all locations
    """
    oldState = initialState
    currentState = iterate(matrix, oldState, paths)

    while getTableLine(oldState) != getTableLine(currentState):
        oldState = currentState
        currentState = iterate(matrix, oldState, paths)

    return currentState

def iterate(matrix, stateVector, paths = None):
    """
    Does one iteration of the requirement calculation for all location. Calculating the requirements to reach all
    locations on the map from a given spawn point can be done by using a stateVector with all locations set to [] or [-1] (impossible)
    except for the start location itself, which should be set to [0] (no requirements). Afterwards repeatedly call
    this method to make one movement along all possible edges in the graph simultaneously.
    :param matrix: The matrix representing the logic graph for the game map
    :param stateVector: The current requirement state. Should be initialized with a (...[],[0],[],...) where the [0]
    represents the spawn location
    :param paths: Debug option. If a vector of paths is provided newly reached locations
    (or locations reached with a new requirement value) will also add a new path to the path vector.
    Can be used to generate a path from the initial location to each of the other locations.
    :return: The updated state vector after moving along the edges of the graph. Feed this back into this method as
    the new state vector to make multiple movements.
    """
    ret = [[] for _ in range(len(stateVector))]
    debugMode = (paths is not None and len(paths) == len(stateVector))

    for i in range(len(matrix)):
        newPaths = []
        for j in range(len(matrix)):
            #print(f'{matrix[j][i]}, {stateVector[i]}')
            newReqs = calculateTotalRequirements(matrix[j][i], stateVector[j])
            ret[i] += newReqs
            if debugMode:
                for req in newReqs:
                    newPaths += [(req, j)]
        #print(ret[i])
        ret[i], newPaths = reduceReqs(ret[i], newPaths)
        if debugMode:
            reducePaths(paths[i], newPaths)

    return ret

def calculateTotalRequirements(newLocationReqs, currentLocationReqs):
    """
    Combines the requirement sets (all possible combinations of powerups and tricks) needed to reach the current location
     with the requirement sets needed to move along an edge in the graph to a new location. This results in a new list of
      requirement sets which contains a combination of each item from the first parameter with each item from the second
      parameter. This new list may contain duplicates and requirement super-sets
      (i.e. requirement sets which contain unnecessary requirements).

    :param newLocationReqs: Requirements for moving from the current location to a new one
    :param currentLocationReqs: Requirements for reaching the current location
    :return:
    """
    if calculateTotalRequirementsDict[getIndexForRequirementOperationDicts(newLocationReqs, currentLocationReqs)] != None:
        pass #ToDo
    nrNewReqs = len(newLocationReqs)
    nrOldReqs = len(currentLocationReqs)
    totalReqs = [0]*(nrNewReqs*nrOldReqs)
    for i in range(nrNewReqs):
        for j in range(nrOldReqs):
            totalReqs[i*nrOldReqs+j] = newLocationReqs[i] | currentLocationReqs[j]
    return totalReqs

def getIndexForRequirementOperationDicts(firstOperand, secondOperand = None):
    i = 0
    for v in firstOperand:
        i *= 128
        i += v

    if secondOperand != None:
        i *= 128 ** (REQUIREMENTS_COUNT-1)
        for v in secondOperand:
            i *= 128
            i += v

    return i

def reduceReqs(reqs, paths = None):
    """
    Takes a list of requirement sets and removes those which represent a superset of another requirement set.
    Example: [3 (blue orb, red orb),7 (blue orb, red orb, boots)]
          -> [3] (boots are not needed)
    :param reqs: The list of requirement sets to reduce.
    :param paths: Debug parameter to store the paths which the algorithm finds.

    """
    if paths is None:
        paths = []
    reducedReqs = []
    reducedPaths = []
    reqs.sort()
    paths.sort()
    debugmode = len(paths) == len(reqs)
    for i in range(len(reqs)):
        req = reqs[i]
        add = True
        for newReq in reducedReqs:
            if newReq & req == newReq:
                add = False
                break
        if add:
            reducedReqs += [req]
            if debugmode:
                reducedPaths += [paths[i]]
    return reducedReqs, reducedPaths

def reducePaths(oldPaths, newPaths):
    """
    Checks existing paths and adds new paths with different requirements or replaces them with new paths having less
    requirements
    :param oldPaths: The existing paths
    :param newPaths: Paths to check for better or different alternatives
    """
    for newPath in newPaths:
        add = True
        deleteList = []
        for oldReq in oldPaths.keys():
            if oldReq & newPath[0] == oldReq:
                add = False
                break
            if oldReq & newPath[0] == newPath[0]:
                deleteList += [oldReq]

        for toDel in deleteList:
            del(oldPaths[toDel])

        if add:
            oldPaths[newPath[0]] = newPath[1]

def findSubIndex(fullList, subList):
    """
    Helper method to select a subset from a row in the matrix
    """
    indices = []

    for i in range(len(fullList)):
        if fullList[i] in subList:
            indices += [i]

    return indices

def printPath(pathMatrix, locationIndex, requirementValue, labels):
    while locationIndex != -1:
        print(labels[locationIndex])
        newLocIndex = -1
        for key in pathMatrix[locationIndex].keys():
            if key & requirementValue == key:
                newLocIndex = pathMatrix[locationIndex][key]

        locationIndex = newLocIndex