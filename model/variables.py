import CursusGroups as TFEcursusGroups
import data.io as TFEdata
import docplex.cp.model as cp
import pandas as pd
import math
from collections import defaultdict

def generateIntervalVariables(constants):
    """
    Function creating and placing interval variables in appropriate dictionaries

    An interval variable has 2 unknowns (startTime and endTime) and many parameters (length, intensity function, etc.).
    CP Optimizer supports interesting scheduling constraints with this type of variable
    (more information : https://fr.slideshare.net/PhilippeLaborie/introduction-to-cp-optimizer-for-scheduling)

    Lecture and exercise lessons are short (2h) and thus will have a length of 1 (1 unit of time = 2 hours)
    TP and projects lessons are long (4h) and this will have a length of 2

    lecturesDict, exercisesDict, tpsDict and projectsDict (all called "lessonDict" below) contain interval variables and information about the AA :
    A lessonDict is a dictionary which has :
        - key = code of AA (i.e. "I-MARO-020")
        - value = a dictionary with 3 key-values:
            - 1 = "weekBounds" : (tuple) (weekStart,weekEnd) #week number of start and end of the AA (from 1 to constants["weeks"])
            - 2 = "divisions" : (list) #list of interval variables per division
            - 3 = "cursus" : (list) #list of cursus following the AA

    groupsIntervalVariables, teachersIntervalVariables and roomsIntervalVariables are defaultdict(list)
    The structure is :
        - key = name of the resource
        - value = all interval variables where the resource is needed
    A defaultdict(list) means that a new entry will be initialised with a list

    cursusGroups is an object of the CursusGroups class with useful information about groups and divisions
    AAset is a set with all AA encountered during the creation of interval variables

    :param constants: (dict) dictionary with information about the model to build. Mandatory keys are :
        - fileDataset
        - weeks
        - days
        - slots
        - segmentSize
        - quadri
        - cursus
        - roundUp
        - groupAuto
    :return: lecturesDict,exercisesDict,tpsDict,projectsDict,
                groupsIntervalVariables,teachersIntervalVariables,roomsIntervalVariables,
                cursusGroups,AAset
    """
    lecturesDict = {}
    exercisesDict = {}
    tpsDict = {}
    projectsDict = {}

    groupsIntervalVariables = defaultdict(list)
    teachersIntervalVariables = defaultdict(list)
    roomsIntervalVariables = defaultdict(list)

    cursusGroups = TFEcursusGroups.CursusGroups(constants["fileDataset"])
    AAset = set()

    totalSlots = int(constants["weeks"] * constants["days"] * constants["slots"] / constants["segmentSize"])

    # count the number of added/deleted lessons in order to fit weeks in segments
    delta = 0

    datasetAA = TFEdata.loadData(constants["fileDataset"],constants["quadri"], "TFE")
    for rowAA in datasetAA.itertuples():

        # the AA is skipped if there is no cursus in the AA present in constants["cursus"]
        listOfCursus = rowAA.cursus.split(",")
        if not any(constants["cursus"][cursus] is True for cursus in listOfCursus):
            continue

        # the AA is skipped if it has been already processed
        if rowAA.id in AAset:
            continue
        AAset.add(rowAA.id)

        # creating interval variables for lectures
        if not pd.isna(rowAA.lectureHours):
            # since a lecture is given once, all the groups belong to the same and unique division
            listOfGroups = cursusGroups.getGroups(listOfCursus)
            lecturesDict[rowAA.id] = {
                "weekBounds": (rowAA.lectureWeekStart,rowAA.lectureWeekEnd),
                "divisions": [
                    []
                ],
                "cursus": listOfCursus
            }

            # computing the number of lessons in regards to the size of a segment
            # assumption : a lecture lasts for 2 hours
            trueNumberOfLessons = math.ceil(rowAA.lectureHours / 2)
            if constants["roundUp"]:
                modelNumberOfLessons = math.ceil(trueNumberOfLessons / constants["segmentSize"])
                delta += modelNumberOfLessons * constants["segmentSize"] - trueNumberOfLessons
            else:
                modelNumberOfLessons = math.floor(trueNumberOfLessons / constants["segmentSize"])
                delta -= trueNumberOfLessons - modelNumberOfLessons * constants["segmentSize"]

            # cp.interval_var_list creates a list of "asize" interval variables
            # the length of a lecture interval variable is 1
            lectureIntervalVariables = cp.interval_var_list(asize=modelNumberOfLessons,
                                                    start=(0, totalSlots - 1),
                                                    end=(1, totalSlots),
                                                    size=1,
                                                    length=1,
                                                    name=rowAA.id + "_lec")

            # all the interval variables are added to the first and only division for the AA
            lecturesDict[rowAA.id]["divisions"][0].extend(lectureIntervalVariables)

            # all the interval variables are added to corresponding groups, teachers and rooms dictionaries
            for group in listOfGroups:
                groupsIntervalVariables[group].extend(lectureIntervalVariables)
            for teacher in rowAA.lectureTeachers.split(","):
                teachersIntervalVariables[teacher].extend(lectureIntervalVariables)
            for room in rowAA.lectureRooms.split(","):
                roomsIntervalVariables[room].extend(lectureIntervalVariables)

        # creating interval variables for lectures
        if not pd.isna(rowAA.exerciseHours):
            # an exercise can be multiplied and thus creates divisions
            # the following function generates balanced divisions (automatically or not)
            listOfDivisions = cursusGroups.generateBalancedDivisions(listOfCursus, rowAA.exerciseDivisions, constants["groupAuto"])
            exercisesDict[rowAA.id] = {
                "weekBounds": (rowAA.exerciseWeekStart,rowAA.exerciseWeekEnd),
                "divisions": [
                    [] for d in range(rowAA.exerciseDivisions) # several divisions
                ],
                "cursus": listOfCursus
            }

            # computing the number of lessons in regards to the size of a segment (a doubled lesson is counted twice)
            # assumption : a lecture lasts for 2 hours
            trueNumberOfLessons = math.ceil(rowAA.exerciseHours / 2)
            if constants["roundUp"]:
                modelNumberOfLessons = math.ceil(trueNumberOfLessons / constants["segmentSize"])
                delta += (modelNumberOfLessons * constants["segmentSize"] - trueNumberOfLessons) * rowAA.exerciseDivisions
            else:
                modelNumberOfLessons = math.floor(trueNumberOfLessons / constants["segmentSize"])
                delta -= (trueNumberOfLessons - modelNumberOfLessons * constants["segmentSize"]) * rowAA.exerciseDivisions

            listOfTeachers = rowAA.exerciseTeachers.split(",")
            listOfRooms = rowAA.exerciseRooms.split(",")
            # each multiplied exercise is an interval variable
            # i.e. for 6 exercises and 2 divisions, 12 interval variables must be created
            for currentDivisionIndex in range(rowAA.exerciseDivisions):
                for l in range(modelNumberOfLessons):
                    # cp.interval_var creates one interval variable
                    # the length of an exercise interval variable is 1
                    exerciseIntervalVariable = cp.interval_var(start=(0, totalSlots - 1),
                                                       end=(1, totalSlots),
                                                       size=1,
                                                       length=1,
                                                       name=rowAA.id + "_ex_" + str(l) + "_d_" + str(currentDivisionIndex))

                    # the interval variable is added to the right division
                    exercisesDict[rowAA.id]["divisions"][currentDivisionIndex].append(exerciseIntervalVariable)

                    # the currentDivisionIndex refers to the loop
                    # listOfDivisions contains index of division with all groups within this division
                    # the interval variable is thus placed in the right list of group intervals when currentDivisionIndex == divisionIndex
                    for group,divisionIndex in listOfDivisions.items():
                        if divisionIndex == currentDivisionIndex:
                            groupsIntervalVariables[group].append(exerciseIntervalVariable)

                    # when an exercise must be "split", it means that only a subset of teachers and rooms are planified for this lesson
                    # rowAA.exerciseSplit = n : n teachers and n rooms per multiplied lesson
                    # the teachers and rooms affected in lessons are determined in a cyclic way
                    # i.e. for 5 multiplied lessons and 2 rooms :
                    #   - the first room will be planified for the first, third and fifth multiplication
                    #   - the second room will be planified for the second and fourth multiplication
                    if rowAA.exerciseSplit != 0:
                        numberCycles = math.ceil(len(listOfTeachers) / rowAA.exerciseSplit)
                        sizeLastCycle = len(listOfTeachers) % rowAA.exerciseSplit if rowAA.exerciseSplit != 1 else 1
                        currentCycle = currentDivisionIndex % numberCycles
                        sizeCurrentCycle = rowAA.exerciseSplit if currentCycle != numberCycles - 1 else sizeLastCycle
                        for c in range(sizeCurrentCycle):
                            teachersIntervalVariables[listOfTeachers[currentCycle * rowAA.exerciseSplit + c]].append(
                                exerciseIntervalVariable)
                        numberCycles = math.ceil(len(listOfRooms) / rowAA.exerciseSplit)
                        sizeLastCycle = len(listOfRooms) % rowAA.exerciseSplit if rowAA.exerciseSplit != 1 else 1
                        currentCycle = currentDivisionIndex % numberCycles
                        sizeCurrentCycle = rowAA.exerciseSplit if currentCycle != numberCycles - 1 else sizeLastCycle
                        for c in range(sizeCurrentCycle):
                            roomsIntervalVariables[listOfRooms[currentCycle * rowAA.exerciseSplit + c]].append(
                                exerciseIntervalVariable)

                    # rowAA.exerciseSplit = 0 : no split (all teachers and rooms are planified for all interval variables)
                    else:
                        for teacher in listOfTeachers:
                            teachersIntervalVariables[teacher].append(exerciseIntervalVariable)
                        for room in listOfRooms:
                            roomsIntervalVariables[room].append(exerciseIntervalVariable)

        # creating interval variables for tp
        if not pd.isna(rowAA.tpHours):
            # a tp can be multiplied and thus creates divisions
            # the following function generates balanced divisions (automatically or not)
            listOfDivisions = cursusGroups.generateBalancedDivisions(listOfCursus, rowAA.tpDivisions, constants["groupAuto"])
            tpsDict[rowAA.id] = {
                "weekBounds": (rowAA.tpWeekStart,rowAA.tpWeekEnd),
                "divisions": [
                    [] for d in range(rowAA.tpDivisions)
                ],
                "cursus": listOfCursus
            }

            # computing the number of lessons in regards to the size of a segment (a doubled lesson is counted twice)
            # a tp lasts for 3 or 4 hours (rowAA.tpDuration)
            trueNumberOfLessons = int(rowAA.tpHours / rowAA.tpDuration)
            if constants["roundUp"]:
                modelNumberOfLessons = math.ceil(trueNumberOfLessons / constants["segmentSize"])
                delta += (modelNumberOfLessons * constants["segmentSize"] - trueNumberOfLessons) * rowAA.tpDivisions
            else:
                modelNumberOfLessons = math.floor(trueNumberOfLessons / constants["segmentSize"])
                delta -= (trueNumberOfLessons - modelNumberOfLessons * constants["segmentSize"]) * rowAA.tpDivisions

            # each multiplied tp is an interval variable
            # i.e. for 6 exercises and 2 divisions, 12 interval variables must be created
            for currentDivisionIndex in range(rowAA.tpDivisions):
                for l in range(modelNumberOfLessons):
                    # cp.interval_var creates one interval variable
                    # the length of a tp interval variable is 2
                    tpIntervalVariable = cp.interval_var(start=(0, totalSlots - 2),
                                                 end=(2, totalSlots),
                                                 size=2,
                                                 length=2,
                                                 name=rowAA.id + "_tp_" + str(l) + "_d_" + str(currentDivisionIndex))

                    # the interval variable is added to the right division
                    tpsDict[rowAA.id]["divisions"][currentDivisionIndex].append(tpIntervalVariable)

                    # the currentDivisionIndex refers to the loop
                    # listOfDivisions contains index of division with all groups within this division
                    # the interval variable is thus placed in the right list of group intervals when currentDivisionIndex == divisionIndex
                    for group, divisionIndex in listOfDivisions.items():
                        if divisionIndex == currentDivisionIndex:
                            groupsIntervalVariables[group].append(tpIntervalVariable)

                    # all the interval variables are added to corresponding teachers and rooms dictionaries
                    for teacher in rowAA.tpTeachers.split(","):
                        teachersIntervalVariables[teacher].append(tpIntervalVariable)
                    for room in rowAA.tpRooms.split(","):
                        roomsIntervalVariables[room].append(tpIntervalVariable)

        # creating interval variables for lectures
        if not pd.isna(rowAA.projectHours):
            # since a lecture is given once, all the groups belong to the same and unique division
            listOfGroups = cursusGroups.getGroups(listOfCursus)
            projectsDict[rowAA.id] = {
                "weekBounds": (rowAA.projectWeekStart,rowAA.projectWeekEnd),
                "divisions": [
                    []
                ],
                "cursus": listOfCursus
            }

            # computing the number of lessons in regards to the size of a segment
            # a project lasts for 3 or 4 hours (rowAA.projectDuration)
            trueNumberOfLessons = int(rowAA.projectHours / rowAA.projectDuration)
            if constants["roundUp"]:
                modelNumberOfLessons = math.ceil(trueNumberOfLessons / constants["segmentSize"])
                delta += modelNumberOfLessons * constants["segmentSize"] - trueNumberOfLessons
            else:
                modelNumberOfLessons = math.floor(trueNumberOfLessons / constants["segmentSize"])
                delta -= trueNumberOfLessons - modelNumberOfLessons * constants["segmentSize"]

            # cp.interval_var_list creates a list of "asize" interval variables
            # the length of a project interval variable is 2
            projectIntervalVariables = cp.interval_var_list(asize=modelNumberOfLessons,
                                                    start=(0,totalSlots-2),
                                                    end=(2,totalSlots),
                                                    size=2,
                                                    length=2,
                                                    name=rowAA.id + "_pr")

            # all the interval variables are added to the first and only division for the AA
            projectsDict[rowAA.id]["divisions"][0].extend(projectIntervalVariables)

            # all the interval variables are added to corresponding groups and teachers dictionaries (no room for projects)
            for group in listOfGroups:
                groupsIntervalVariables[group].extend(projectIntervalVariables)
            for teacher in rowAA.projectTeachers.split(","):
                teachersIntervalVariables[teacher].extend(projectIntervalVariables)

    print("delta", delta)
    return lecturesDict,exercisesDict,tpsDict,projectsDict,\
           groupsIntervalVariables,teachersIntervalVariables,roomsIntervalVariables,\
           cursusGroups,AAset

def generateCharleroiIntervalVariables(model, teachersIntervalVariables, roomsIntervalVariables, constants):
    totalSlots = int(constants["weeks"] * constants["days"] * constants["slots"] / constants["segmentSize"])
    numberOfSegments = int(constants["weeks"] / constants["segmentSize"])
    longVariableFunction = cp.CpoStepFunction(steps=[(i, 1 if i % 4 == 0 else 0) for i in range(
        int(constants["weeks"] * constants["days"] * constants["slots"] / constants["segmentSize"]))])
    shortVariableFunction = cp.CpoStepFunction(steps=[(i, 1 if i % 2 == 0 else 0) for i in range(
        int(constants["weeks"] * constants["days"] * constants["slots"] / constants["segmentSize"]))])

    datasetCharleroiTeachers = TFEdata.loadData(constants["fileDataset"],constants["quadri"], "Charleroi")
    for rowTeacher in datasetCharleroiTeachers.itertuples():
        listOfAA = rowTeacher.AA.split(",")
        variableName = listOfAA[0]
        if len(listOfAA) != 1:
            variableName += ",..."

        numberLongVariablesPerWeek = math.trunc(len(listOfAA) / 2)
        hasShortVariablePerWeek = len(listOfAA)%2
        charleroiVariables = []
        for v in range(numberLongVariablesPerWeek):
            for s in range(numberOfSegments):
                longCharleroiIntervalVariable = cp.interval_var(start=(0,totalSlots-4),
                                                        end=(4,totalSlots),
                                                        size=4,
                                                        length=4,
                                                        name=variableName+"_ch4_"+str((v*4)+s))
                model.add(cp.forbid_start(interval=longCharleroiIntervalVariable, function=longVariableFunction))
                charleroiVariables.append(longCharleroiIntervalVariable)

                teachersIntervalVariables[rowTeacher.teacher].append(longCharleroiIntervalVariable)
                roomsIntervalVariables[rowTeacher.room].append(longCharleroiIntervalVariable)

        if hasShortVariablePerWeek == 1:
            for s in range(numberOfSegments):
                shortCharleroiIntervalVariable = cp.interval_var(start=(0, totalSlots - 2),
                                                    end=(2, totalSlots),
                                                    size=2,
                                                    length=2,
                                                    name=variableName + "_ch2_" + str((numberLongVariablesPerWeek * 4) + s))
                model.add(cp.forbid_start(interval=shortCharleroiIntervalVariable, function=shortVariableFunction))
                charleroiVariables.append(shortCharleroiIntervalVariable)

                teachersIntervalVariables[rowTeacher.teacher].append(shortCharleroiIntervalVariable)
                roomsIntervalVariables[rowTeacher.room].append(shortCharleroiIntervalVariable)

        for v in range(numberLongVariablesPerWeek):
            for s in range(numberOfSegments):
                model.add(cp.start_of(charleroiVariables[(v * numberOfSegments) + s]) >= s * constants["days"] * constants["slots"])
                model.add(cp.end_of(charleroiVariables[v * numberOfSegments + s]) <= (s + 1) * constants["days"] * constants["slots"])
                if v != numberLongVariablesPerWeek - 1:
                    model.add(cp.end_before_start(charleroiVariables[v * numberOfSegments + s], charleroiVariables[(v + 1) * numberOfSegments + s]))

        if hasShortVariablePerWeek != 0:
            for s in range(numberOfSegments):
                model.add(cp.start_of(charleroiVariables[numberLongVariablesPerWeek * numberOfSegments + s]) >= s * constants["days"] * constants["slots"])
                model.add(cp.end_of(charleroiVariables[numberLongVariablesPerWeek * numberOfSegments + s]) <= (s + 1) * constants["days"] * constants["slots"])

def generateCharleroiFixedIntervalVariables(model, teachersIntervalVariables, roomsIntervalVariables, constants):
    totalSlots = int(constants["weeks"] * constants["days"] * constants["slots"] / constants["segmentSize"])
    datasetCharleroiTeachers = TFEdata.loadData(constants["fileDataset"],constants["quadri"], "CharleroiFixed")

    for rowTeacher in datasetCharleroiTeachers.itertuples():
        variableName = rowTeacher.AA
        realWeekBounds = (rowTeacher.weekStart,rowTeacher.weekEnd)
        modelSegmentBounds = (math.floor((realWeekBounds[0] - 1) / constants["segmentSize"]), math.ceil(realWeekBounds[1] / constants["segmentSize"]))

        for w in range(modelSegmentBounds[0],modelSegmentBounds[1]):
            charleroiIntervalVariable = cp.interval_var(start=(0,totalSlots-2),
                                                end=(2,totalSlots),
                                                size=2,
                                                length=2,
                                                name=variableName+"_ch2_"+str(w))

            teachersIntervalVariables[rowTeacher.teacher].append(charleroiIntervalVariable)
            roomsIntervalVariables[rowTeacher.room].append(charleroiIntervalVariable)

            model.add(cp.start_of(charleroiIntervalVariable) == w * constants["days"] * constants["slots"] + constants["slots"] * (rowTeacher.day - 1) + rowTeacher.slot - 1)

def splitVariablesInSequences(intervalVariables, fullSequenceSize):
    numberOfSequences = math.ceil(len(intervalVariables) / fullSequenceSize)
    sequences = [[] for s in range(numberOfSequences)]
    for v in range(len(intervalVariables)):
        sequences[math.trunc(v / fullSequenceSize)].append(intervalVariables[v])
    return sequences