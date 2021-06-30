import CursusGroups as TFEcursusGroups
import data.io as TFEdata

import docplex.cp.model as cp
import pandas as pd
import math
from collections import defaultdict

def generateIntervalVariables(constants):
    lecturesDict = {}
    exercisesDict = {}
    tpsDict = {}
    projectsDict = {}

    cursusIntervalVariables = defaultdict(list)
    teachersIntervalVariables = defaultdict(list)
    roomsIntervalVariables = defaultdict(list)

    cursusGroups = TFEcursusGroups.CursusGroups(constants["fileDataset"])
    AAset = set()

    totalSlots = int(constants["weeks"] * constants["days"] * constants["slots"] / constants["segmentSize"])
    delta = 0

    datasetAA = TFEdata.loadData(constants["fileDataset"],constants["quadri"], "TFE")
    for rowAA in datasetAA.itertuples():

        listOfCursus = rowAA.cursus.split(",")
        if not any(constants["cursus"][cursus] is True for cursus in listOfCursus):
            continue

        if rowAA.id in AAset:
            continue
        AAset.add(rowAA.id)

        if not pd.isna(rowAA.lectureHours):
            listOfGroups = cursusGroups.getGroups(listOfCursus)
            lecturesDict[rowAA.id] = {
                "weekBounds": (rowAA.lectureWeekStart,rowAA.lectureWeekEnd),
                "divisions": [
                    []
                ],
                "cursus": listOfCursus
            }

            trueNumberOfLessons = math.ceil(rowAA.lectureHours / 2)
            if constants["roundUp"]:
                modelNumberOfLessons = math.ceil(trueNumberOfLessons / constants["segmentSize"])
                delta += modelNumberOfLessons * constants["segmentSize"] - trueNumberOfLessons
            else:
                modelNumberOfLessons = math.floor(trueNumberOfLessons / constants["segmentSize"])
                delta -= trueNumberOfLessons - modelNumberOfLessons * constants["segmentSize"]

            lectureIntervalVariables = cp.interval_var_list(asize=modelNumberOfLessons,
                                                    start=(0, totalSlots - 1),
                                                    end=(1, totalSlots),
                                                    size=1,
                                                    length=1,
                                                    name=rowAA.id + "_lec")
            lecturesDict[rowAA.id]["divisions"][0].extend(lectureIntervalVariables)

            for group in listOfGroups:
                cursusIntervalVariables[group].extend(lectureIntervalVariables)
            for teacher in rowAA.lectureTeachers.split(","):
                teachersIntervalVariables[teacher].extend(lectureIntervalVariables)
            for room in rowAA.lectureRooms.split(","):
                roomsIntervalVariables[room].extend(lectureIntervalVariables)

        if not pd.isna(rowAA.exerciseHours):
            listOfDivisions = cursusGroups.generateBalancedDivisions(listOfCursus, rowAA.exerciseDivisions, constants["groupAuto"])
            exercisesDict[rowAA.id] = {
                "weekBounds": (rowAA.exerciseWeekStart,rowAA.exerciseWeekEnd),
                "divisions": [
                    [] for d in range(rowAA.exerciseDivisions)
                ],
                "cursus": listOfCursus
            }

            trueNumberOfLessons = math.ceil(rowAA.exerciseHours / 2)
            if constants["roundUp"]:
                modelNumberOfLessons = math.ceil(trueNumberOfLessons / constants["segmentSize"])
                delta += (modelNumberOfLessons * constants["segmentSize"] - trueNumberOfLessons) * rowAA.exerciseDivisions
            else:
                modelNumberOfLessons = math.floor(trueNumberOfLessons / constants["segmentSize"])
                delta -= (trueNumberOfLessons - modelNumberOfLessons * constants["segmentSize"]) * rowAA.exerciseDivisions

            listOfTeachers = rowAA.exerciseTeachers.split(",")
            listOfRooms = rowAA.exerciseRooms.split(",")
            for currentDivisionIndex in range(rowAA.exerciseDivisions):
                for l in range(modelNumberOfLessons):
                    exerciseIntervalVariable = cp.interval_var(start=(0, totalSlots - 1),
                                                       end=(1, totalSlots),
                                                       size=1,
                                                       length=1,
                                                       name=rowAA.id + "_ex_" + str(l) + "_d_" + str(currentDivisionIndex))
                    exercisesDict[rowAA.id]["divisions"][currentDivisionIndex].append(exerciseIntervalVariable)

                    for group,divisionIndex in listOfDivisions.items():
                        if divisionIndex == currentDivisionIndex:
                            cursusIntervalVariables[group].append(exerciseIntervalVariable)
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

                    else:
                        for teacher in listOfTeachers:
                            teachersIntervalVariables[teacher].append(exerciseIntervalVariable)
                        for room in listOfRooms:
                            roomsIntervalVariables[room].append(exerciseIntervalVariable)

        if not pd.isna(rowAA.tpHours):
            listOfDivisions = cursusGroups.generateBalancedDivisions(listOfCursus, rowAA.tpDivisions, constants["groupAuto"])
            tpsDict[rowAA.id] = {
                "weekBounds": (rowAA.tpWeekStart,rowAA.tpWeekEnd),
                "divisions": [
                    [] for d in range(rowAA.tpDivisions)
                ],
                "cursus": listOfCursus
            }

            trueNumberOfLessons = int(rowAA.tpHours / rowAA.tpDuration)
            if constants["roundUp"]:
                modelNumberOfLessons = math.ceil(trueNumberOfLessons / constants["segmentSize"])
                delta += (modelNumberOfLessons * constants["segmentSize"] - trueNumberOfLessons) * rowAA.tpDivisions
            else:
                modelNumberOfLessons = math.floor(trueNumberOfLessons / constants["segmentSize"])
                delta -= (trueNumberOfLessons - modelNumberOfLessons * constants["segmentSize"]) * rowAA.tpDivisions

            for currentDivisionIndex in range(rowAA.tpDivisions):
                for l in range(modelNumberOfLessons):
                    tpIntervalVariable = cp.interval_var(start=(0, totalSlots - 2),
                                                 end=(2, totalSlots),
                                                 size=2,
                                                 length=2,
                                                 name=rowAA.id + "_tp_" + str(l) + "_d_" + str(currentDivisionIndex))
                    tpsDict[rowAA.id]["divisions"][currentDivisionIndex].append(tpIntervalVariable)

                    for group, divisionIndex in listOfDivisions.items():
                        if divisionIndex == currentDivisionIndex:
                            cursusIntervalVariables[group].append(tpIntervalVariable)
                    for teacher in rowAA.tpTeachers.split(","):
                        teachersIntervalVariables[teacher].append(tpIntervalVariable)
                    for room in rowAA.tpRooms.split(","):
                        roomsIntervalVariables[room].append(tpIntervalVariable)

        if not pd.isna(rowAA.projectHours):
            listOfGroups = cursusGroups.getGroups(listOfCursus)
            projectsDict[rowAA.id] = {
                "weekBounds": (rowAA.projectWeekStart,rowAA.projectWeekEnd),
                "divisions": [
                    []
                ],
                "cursus": listOfCursus
            }

            trueNumberOfLessons = int(rowAA.projectHours / rowAA.projectDuration)
            if constants["roundUp"]:
                modelNumberOfLessons = math.ceil(trueNumberOfLessons / constants["segmentSize"])
                delta += modelNumberOfLessons * constants["segmentSize"] - trueNumberOfLessons
            else:
                modelNumberOfLessons = math.floor(trueNumberOfLessons / constants["segmentSize"])
                delta -= trueNumberOfLessons - modelNumberOfLessons * constants["segmentSize"]

            projectIntervalVariables = cp.interval_var_list(asize=modelNumberOfLessons,
                                                    start=(0,totalSlots-2),
                                                    end=(2,totalSlots),
                                                    size=2,
                                                    length=2,
                                                    name=rowAA.id + "_pr")
            projectsDict[rowAA.id]["divisions"][0].extend(projectIntervalVariables)

            for group in listOfGroups:
                cursusIntervalVariables[group].extend(projectIntervalVariables)
            for teacher in rowAA.projectTeachers.split(","):
                teachersIntervalVariables[teacher].extend(projectIntervalVariables)

    print("delta", delta)
    return lecturesDict,exercisesDict,tpsDict,projectsDict,\
           cursusIntervalVariables,teachersIntervalVariables,roomsIntervalVariables,\
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
        modelWeekBounds = (math.floor((realWeekBounds[0] - 1) / constants["segmentSize"]), math.ceil(realWeekBounds[1] / constants["segmentSize"]))

        for w in range(modelWeekBounds[0],modelWeekBounds[1]):
            charleroiIntervalVariable = cp.interval_var(start=(0,totalSlots-2),
                                                end=(2,totalSlots),
                                                size=2,
                                                length=2,
                                                name=variableName+"_ch2_"+str(w))

            teachersIntervalVariables[rowTeacher.teacher].append(charleroiIntervalVariable)
            roomsIntervalVariables[rowTeacher.room].append(charleroiIntervalVariable)

            model.add(cp.start_of(charleroiIntervalVariable) == w * constants["days"] * constants["slots"] + constants["slots"] * (rowTeacher.day - 1) + rowTeacher.slot - 1)

def splitVariablesInBlocs(intervalVariables, blocSize):
    numberOfBlocs = math.ceil(len(intervalVariables) / blocSize)
    blocs = [[] for b in range(numberOfBlocs)]
    for v in range(len(intervalVariables)):
        blocs[math.trunc(v/blocSize)].append(intervalVariables[v])
    return blocs