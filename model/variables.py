import CursusGroups as TFEcursusGroups
import data.io as TFEdata

import docplex.cp.model as cp
import pandas as pd
import math
from collections import defaultdict

def generateVariables(constants):
    lecturesDict = {}
    exercisesDict = {}
    tpsDict = {}
    projectsDict = {}

    cursusVariables = defaultdict(list)
    teachersVariables = defaultdict(list)
    roomsVariables = defaultdict(list)

    cursusGroups = TFEcursusGroups.CursusGroups(constants["fileDataset"])
    AAset = set()

    nbrSlots = int(constants["weeks"] * constants["days"] * constants["slots"] / constants["segmentSize"])
    delta = 0

    dataMons = TFEdata.loadData(constants["fileDataset"],constants["quadri"], "TFE")
    for row in dataMons.itertuples():

        listCursus = row.cursus.split(",")
        if not any(constants["cursus"][cursus] is True for cursus in listCursus):
            continue

        if any(row.id in slots for slots in [lecturesDict,exercisesDict,tpsDict,projectsDict]):
            continue

        AAset.add(row.id)

        if not pd.isna(row.lectureHours):
            listGroups = cursusGroups.getGroups(listCursus)
            lecturesDict[row.id] = {
                "spread": (row.lectureWeekStart,row.lectureWeekEnd),
                "groups": [
                    []
                ],
                "cursus": listCursus
            }
            trueNumberLessons = math.ceil(row.lectureHours / 2)
            if constants["roundUp"]:
                modelnumberLessons = math.ceil(trueNumberLessons / constants["segmentSize"])
                delta += modelnumberLessons * constants["segmentSize"] - trueNumberLessons
            else:
                modelnumberLessons = math.floor(trueNumberLessons / constants["segmentSize"])
                delta -= trueNumberLessons - modelnumberLessons * constants["segmentSize"]

            lectureIntervals = cp.interval_var_list(modelnumberLessons, start=(0, nbrSlots - 1), end=(1, nbrSlots),
                                                    size=1, length=1 ,name=row.id + "_lec")

            lecturesDict[row.id]["groups"][0].extend(lectureIntervals)
            for g in listGroups:
                cursusVariables[g].extend(lectureIntervals)
            for t in row.lectureTeachers.split(","):
                teachersVariables[t].extend(lectureIntervals)
            if not pd.isna(row.lectureRooms):
                for r in row.lectureRooms.split(","):
                    roomsVariables[r].extend(lectureIntervals)

        if not pd.isna(row.exerciseHours):
            listDivisions = cursusGroups.generateBalancedGroups(listCursus, row.exerciseGroups, constants["groupAuto"])
            exercisesDict[row.id] = {
                "spread": (row.exerciseWeekStart,row.exerciseWeekEnd),
                "groups": [
                    [] for g in range(row.exerciseGroups)
                ],
                "cursus": listCursus
            }
            trueNumberLessons = math.ceil(row.exerciseHours / 2)
            listTeachers = row.exerciseTeachers.split(",")
            listRooms = []
            if not pd.isna(row.exerciseRooms):
                listRooms = row.exerciseRooms.split(",")
            if constants["roundUp"]:
                modelnumberLessons = math.ceil(trueNumberLessons / constants["segmentSize"])
                delta += (modelnumberLessons * constants["segmentSize"] - trueNumberLessons) * row.exerciseGroups
            else:
                modelnumberLessons = math.floor(trueNumberLessons / constants["segmentSize"])
                delta -= (trueNumberLessons - modelnumberLessons * constants["segmentSize"]) * row.exerciseGroups
            for g in range(row.exerciseGroups):
                for i in range(modelnumberLessons):
                    exerciseInterval = cp.interval_var(start=(0, nbrSlots - 1), end=(1, nbrSlots), size=1,
                                                       name=row.id + "_ex_" + str(i) + "_g_" + str(g))

                    exercisesDict[row.id]["groups"][g].append(exerciseInterval)
                    for k,v in listDivisions.items():
                        if v == g:
                            cursusVariables[k].append(exerciseInterval)
                    if row.exerciseSplit != 0:
                        numberCycles = math.ceil(len(listTeachers)/row.exerciseSplit)
                        rest = len(listTeachers)%row.exerciseSplit if row.exerciseSplit != 1 else 1
                        currentCycle = g%numberCycles
                        if currentCycle != numberCycles-1:
                            r = row.exerciseSplit
                        else:
                            r = rest
                        for t in range(r):
                            teachersVariables[listTeachers[currentCycle * row.exerciseSplit + t]].append(exerciseInterval)

                        numberCycles = math.ceil(len(listRooms) / row.exerciseSplit)
                        rest = len(listRooms) % row.exerciseSplit if row.exerciseSplit != 1 else 1
                        currentCycle = g % numberCycles
                        if currentCycle != numberCycles - 1:
                            r = row.exerciseSplit
                        else:
                            r = rest
                        for k in range(r):
                            roomsVariables[listRooms[currentCycle * row.exerciseSplit + k]].append(exerciseInterval)

                    else:
                        for t in listTeachers:
                            teachersVariables[t].append(exerciseInterval)
                        for r in listRooms:
                            roomsVariables[r].append(exerciseInterval)

        if not pd.isna(row.tpHours):
            listDivisions = cursusGroups.generateBalancedGroups(listCursus, row.tpGroups, constants["groupAuto"])
            tpsDict[row.id] = {
                "spread": (row.tpWeekStart,row.tpWeekEnd),
                "groups": [
                    [] for g in range(row.tpGroups)
                ],
                "cursus": listCursus
            }
            trueNumberLessons = int(row.tpHours / row.tpDuration)
            if constants["roundUp"]:
                modelnumberLessons = math.ceil(trueNumberLessons / constants["segmentSize"])
                delta += (modelnumberLessons * constants["segmentSize"] - trueNumberLessons) * row.tpGroups
            else:
                modelnumberLessons = math.floor(trueNumberLessons / constants["segmentSize"])
                delta -= (trueNumberLessons - modelnumberLessons * constants["segmentSize"]) * row.tpGroups
            for g in range(row.tpGroups):
                for i in range(modelnumberLessons):
                    tpInterval = cp.interval_var(start=(0, nbrSlots - 2), end=(2, nbrSlots), size=2,
                                                 name=row.id + "_tp_" + str(i) + "_g_" + str(g))

                    tpsDict[row.id]["groups"][g].append(tpInterval)
                    for k, v in listDivisions.items():
                        if v == g:
                            cursusVariables[k].append(tpInterval)
                    for t in row.tpTeachers.split(","):
                        teachersVariables[t].append(tpInterval)
                    for r in row.tpRooms.split(","):
                        roomsVariables[r].append(tpInterval)

        if not pd.isna(row.projectHours):
            listGroups = cursusGroups.getGroups(listCursus)
            projectsDict[row.id] = {
                "spread": (row.projectWeekStart,row.projectWeekEnd),
                "groups": [
                    []
                ],
                "cursus": listCursus
            }
            trueNumberLessons = int(row.projectHours / row.projectDuration)
            if constants["roundUp"]:
                modelnumberLessons = math.ceil(trueNumberLessons / constants["segmentSize"])
                delta += modelnumberLessons * constants["segmentSize"] - trueNumberLessons
            else:
                modelnumberLessons = math.floor(trueNumberLessons / constants["segmentSize"])
                delta -= trueNumberLessons - modelnumberLessons * constants["segmentSize"]

            projectIntervals = cp.interval_var_list(modelnumberLessons,
                                                    start=(0,nbrSlots-2),
                                                    end=(2,nbrSlots),
                                                    size=2,
                                                    length=2,
                                                    name=row.id + "_pr")

            projectsDict[row.id]["groups"][0].extend(projectIntervals)
            for g in listGroups:
                cursusVariables[g].extend(projectIntervals)
            for t in row.projectTeachers.split(","):
                teachersVariables[t].extend(projectIntervals)
    print("delta", delta)
    return lecturesDict,exercisesDict,tpsDict,projectsDict,\
           cursusVariables,teachersVariables,roomsVariables,\
           cursusGroups,AAset

def charleroiVariables(model, teachersVariables, roomsVariables, constants):
    nbrSlots = int(constants["weeks"] * constants["days"] * constants["slots"] / constants["segmentSize"])
    numberSegments = int(constants["weeks"] / constants["segmentSize"])
    dataCharleroi = TFEdata.loadData(constants["fileDataset"],constants["quadri"], "Charleroi")
    for row in dataCharleroi.itertuples():
        listAA = row.AA.split(",")
        if len(listAA) == 1:
            variableName = listAA[0]
        else:
            variableName = listAA[0]+",..."
        numberFullIntervalsPerWeek = math.trunc(len(listAA) / 2)
        partialIntervalPerWeek = len(listAA)%2
        charleroiIntervals = []
        for i in range(numberFullIntervalsPerWeek):
            for j in range(numberSegments):
                charleroiInterval = cp.interval_var(start=(0,nbrSlots-4),end=(4,nbrSlots),size=4,name=variableName+"_ch4_"+str((i*4)+j))

                charleroiIntervals.append(charleroiInterval)
                teachersVariables[row.teacher].append(charleroiInterval)
                roomsVariables[row.room].append(charleroiInterval)

                blocSize4Function = cp.CpoStepFunction(steps=[(i,1 if i%4 == 0 else 0) for i in range(int(constants["weeks"] * constants["days"] * constants["slots"] / constants["segmentSize"]))])
                model.add(cp.forbid_start(interval=charleroiInterval, function=blocSize4Function))

        for i in range(partialIntervalPerWeek):
            for j in range(numberSegments):
                charleroiInterval = cp.interval_var(start=(0, nbrSlots - 2), end=(2, nbrSlots), size=2,
                                                    name=variableName + "_ch2_" + str(((i+numberFullIntervalsPerWeek) * 4) + j))

                charleroiIntervals.append(charleroiInterval)
                teachersVariables[row.teacher].append(charleroiInterval)
                roomsVariables[row.room].append(charleroiInterval)

                blocSize4Function = cp.CpoStepFunction(steps=[(i, 1 if i % 2 == 0 else 0) for i in range(
                    int(constants["weeks"] * constants["days"] * constants["slots"] / constants["segmentSize"]))])
                model.add(cp.forbid_start(interval=charleroiInterval, function=blocSize4Function))

        for i in range(numberFullIntervalsPerWeek):
            for j in range(numberSegments):
                model.add(cp.start_of(charleroiIntervals[(i * numberSegments) + j]) >= j * 20)
                model.add(cp.end_of(charleroiIntervals[i * numberSegments + j]) <= (j + 1) * 20)
                if i != numberFullIntervalsPerWeek - 1:
                    model.add(cp.end_before_start(charleroiIntervals[i * numberSegments + j], charleroiIntervals[(i + 1) * numberSegments + j]))

        if partialIntervalPerWeek != 0:
            for i in range(numberSegments):
                model.add(cp.start_of(charleroiIntervals[numberFullIntervalsPerWeek * numberSegments + i]) >= i*20)
                model.add(cp.end_of(charleroiIntervals[numberFullIntervalsPerWeek * numberSegments + i]) <= (i+1)*20)

def charleroiFixedVariables(model, teachersVariables, roomsVariables, constants):
    nbrSlots = int(constants["weeks"] * constants["days"] * constants["slots"] / constants["segmentSize"])
    dataCharleroi = TFEdata.loadData(constants["fileDataset"],constants["quadri"], "CharleroiFixed")

    for row in dataCharleroi.itertuples():
        variableName = row.AA
        spread = (row.weekStart,row.weekEnd)
        modelStartEnd = (math.floor((spread[0] - 1) / constants["segmentSize"]), math.ceil(spread[1] / constants["segmentSize"]))
        for i in range(modelStartEnd[0],modelStartEnd[1]):
            charleroiInterval = cp.interval_var(start=(0,nbrSlots-2),end=(2,nbrSlots),size=2,name=variableName+"_ch2_"+str(i))

            teachersVariables[row.teacher].append(charleroiInterval)
            roomsVariables[row.room].append(charleroiInterval)

            model.add(cp.start_of(charleroiInterval) == i * constants["days"] * constants["slots"] + constants["slots"] * (row.day - 1) + row.slot - 1)

def generateSpreads(intervals,blocSize):
    numberSpreads = math.ceil(len(intervals) / blocSize)
    spreads = [[] for i in range(numberSpreads)]
    for i in range(len(intervals)):
        spreads[math.trunc(i/blocSize)].append(intervals[i])
    return spreads