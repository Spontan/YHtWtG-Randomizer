class EquivalenceGroup(object):
    def __init__(self, originalMatrix):
        groupMembership = [-1 for i in range(len(originalMatrix))]
        groups = []
        for i in range(len(originalMatrix)):
            found = False
            for j in range(0, i):
                if originalMatrix[i][j] == originalMatrix[j][i] == [0]:
                    groupMembership[i] = groupMembership[j]
                    found = True
                    break
            if found:
                groups[groupMembership[i]] += [i]
            else:
                groupMembership[i] = len(groups)
                groups += [[i]]

        groupCount = len(groups)
        groupMatrix = [[None for i in range(groupCount)] for j in range(groupCount)]
        for i in range(groupCount):
            for j in range(groupCount):
                groupMatrix[i][j] = self.__collectReqs(originalMatrix, groups[i], groups[j])

        self.originalMatrix = originalMatrix
        self.groups = groups
        self.groupMembership = groupMembership
        self.groupMatrix = groupMatrix

    def __collectReqs(self, matrix, fromIndices, toIndices):
        reqs = []
        for i in fromIndices:
            for j in toIndices:
                reqs += matrix[i][j]
        return self.__reduceReqs(reqs)

    def __reduceReqs(self, reqs):
        """
        Takes a list of requirement sets and removes those which represent a superset of another requirement set.
        Example: [3 (blue orb, red orb),7 (blue orb, red orb, boots)]
              -> [3] (boots are not needed)
        :param reqs: The list of requirement sets to reduce.
        :param paths: Debug parameter to store the paths which the algorithm finds.

        """
        reducedReqs = []
        reqs.sort()
        for i in range(len(reqs)):
            req = reqs[i]
            add = True
            for newReq in reducedReqs:
                if newReq & req == newReq:
                    add = False
                    break
            if add:
                reducedReqs += [req]
        return reducedReqs