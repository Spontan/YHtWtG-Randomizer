from logic import requirementcalculations as calc

def prepareReducedMapFile(inFile = "standard.csv", outFile = "reduced_map.csv"):
    table, labels = readTable(inFile)
    writeTable(outFile, calc.reduceRequirementTable(table, labels))

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

def getConnectionValue(matrix, start, end, labels = None):
    """
    Returns the requirements from an entry in the connection matrix
    :param matrix: The connection matrix to edit
    :param start: The startpoint of the connection, can be either a row index or the label of the startpoint
    :param end: The endpoint of the connection, can be either a column index or the label of the endpoint
    :param labels: The list of location labels, used as reference for finding the correct matrix index. 
    This must be given if either the start of end parameter is a location label
    :return: The value of the specified entry
    """

    if type(start) != int:
        if labels == None:
            raise TypeError('labels was None, but start point was a label')
        start = labels.index(start)
    if type(end) != int:
        if labels == None:
            raise TypeError('labels was None, but end point was a label')
        end = labels.index(end)

    return matrix[start][end]


def editConnectionValue(matrix, start, end, newValue, labels=None):
    """
    Edits the requirements of an entry in the connection matrix
    :param matrix: The connection matrix to edit
    :param start: The startpoint of the connection, can be either a row index or the label of the startpoint
    :param end: The endpoint of the connection, can be either a column index or the label of the endpoint
    :param labels: The list of location labels, used as reference for finding the correct matrix index.
    This must be given if either the start of end parameter is a location label
    :return: The old value of the specified entry
    """

    if type(start) != int:
        if labels == None:
            raise TypeError('labels was None, but start point was a label')
        start = labels.index(start)
    if type(end) != int:
        if labels == None:
            raise TypeError('labels was None, but end point was a label')
        end = labels.index(end)

    oldValue = matrix[start][end]
    matrix[start][end] = newValue
    return oldValue

def removeConnection(matrix, start, end, labels = None):
    """
    Removes the requirements from an entry in the connection matrix, effectively severing that connection in the map graph
    :param matrix: The connection matrix to edit
    :param start: The startpoint of the connection to remove, can be either a row index or the label of the startpoint
    :param end: The endpoint of the connection to remove, can be either a column index or the label of the endpoint
    :param labels: The list of location labels, used as reference for finding the correct matrix index. 
    This must be given if either the start of end parameter is a location label
    :return: The value that was removed
    """

    return editConnectionValue(matrix, start, end, [], labels)