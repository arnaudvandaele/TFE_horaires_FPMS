import CursusGroups as TFEcursusGroups
import data.io as TFEdata

import docplex.cp.model as cp
import pandas as pd
import math
from collections import defaultdict

def instantiateVariables(constants):
    lectureSlots = {}
    exerciseSlots = {}
    tpSlots = {}
    projectSlots = {}
    cursusSlots = defaultdict(list)
    teacherSlots = defaultdict(list)
    roomSlots = defaultdict(list)
    cursusGroups = TFEcursusGroups.CursusGroups(constants["fileDataset"])
    AAset = set()
    spreadDict = {
        1.3: (1,3),
        1.6: (1,6),
        1.9: (1,9),
        1.12: (1,12),
        4.6: (4,6),
        4.9: (4,9),
        4.12: (4,12),
        7.9: (7,9),
        7.12: (7,12),
        10.12: (10,12)
    }
    nbrSlots = int(constants["weeks"] * constants["days"] * constants["slots"] / constants["segmentSize"])
    delta = 0

    dataMons = TFEdata.loadData(constants["fileDataset"],constants["quadri"], "TFE")
    for row in dataMons.itertuples():

        listCursus = row.Cursus.split(",")
        if not any(constants["cursus"][cursus] is True for cursus in listCursus):
            continue

        if any(row.ID_AA in slots for slots in [lectureSlots,exerciseSlots,tpSlots,projectSlots]):
            continue

        AAset.add(row.ID_AA)

        if not pd.isna(row.Lectures):
            listGroups = cursusGroups.getGroups(listCursus)
            lectureSlots[row.ID_AA] = {
                "spread": spreadDict[row.Lec_spread],
                "groups": [
                    []
                ],
                "cursus": listCursus
            }
            trueNumberLessons = math.ceil(row.Lectures / 2)
            if constants["roundUp"]:
                modelnumberLessons = math.ceil(trueNumberLessons / constants["segmentSize"])
                delta += modelnumberLessons * constants["segmentSize"] - trueNumberLessons
            else:
                modelnumberLessons = math.floor(trueNumberLessons / constants["segmentSize"])
                delta -= trueNumberLessons - modelnumberLessons * constants["segmentSize"]

            lectureIntervals = cp.interval_var_list(modelnumberLessons, start=(0, nbrSlots - 1), end=(1, nbrSlots),
                                                    size=1, length=1 ,name=row.ID_AA + "_lec")

            lectureSlots[row.ID_AA]["groups"][0].extend(lectureIntervals)
            for g in listGroups:
                cursusSlots[g].extend(lectureIntervals)
            for t in row.Lec_teachers.split(","):
                teacherSlots[t].extend(lectureIntervals)
            if not pd.isna(row.Lec_rooms):
                for r in row.Lec_rooms.split(","):
                    roomSlots[r].extend(lectureIntervals)

        if not pd.isna(row.Exercises):
            listDivisions = cursusGroups.generateBalancedGroups(listCursus, row.Ex_groups, constants["groupAuto"])
            exerciseSlots[row.ID_AA] = {
                "spread": spreadDict[row.Ex_spread],
                "groups": [
                    [] for g in range(row.Ex_groups)
                ],
                "cursus": listCursus
            }
            trueNumberLessons = math.ceil(row.Exercises / 2)
            listTeachers = row.Ex_teachers.split(",")
            listRooms = []
            if not pd.isna(row.Ex_rooms):
                listRooms = row.Ex_rooms.split(",")
            if constants["roundUp"]:
                modelnumberLessons = math.ceil(trueNumberLessons / constants["segmentSize"])
                delta += (modelnumberLessons * constants["segmentSize"] - trueNumberLessons) * row.Ex_groups
            else:
                modelnumberLessons = math.floor(trueNumberLessons / constants["segmentSize"])
                delta -= (trueNumberLessons - modelnumberLessons * constants["segmentSize"]) * row.Ex_groups
            for g in range(row.Ex_groups):
                for i in range(modelnumberLessons):
                    exerciseInterval = cp.interval_var(start=(0, nbrSlots - 1), end=(1, nbrSlots), size=1,
                                                       name=row.ID_AA + "_ex_" + str(i) + "_g_" + str(g))

                    exerciseSlots[row.ID_AA]["groups"][g].append(exerciseInterval)
                    for k,v in listDivisions.items():
                        if v == g:
                            cursusSlots[k].append(exerciseInterval)
                    if row.Ex_split != 0:
                        numberCycles = math.ceil(len(listTeachers)/row.Ex_split)
                        rest = len(listTeachers)%row.Ex_split if row.Ex_split != 1 else 1
                        currentCycle = g%numberCycles
                        if currentCycle != numberCycles-1:
                            r = row.Ex_split
                        else:
                            r = rest
                        for t in range(r):
                            teacherSlots[listTeachers[currentCycle * row.Ex_split + t]].append(exerciseInterval)

                        numberCycles = math.ceil(len(listRooms) / row.Ex_split)
                        rest = len(listRooms) % row.Ex_split if row.Ex_split != 1 else 1
                        currentCycle = g % numberCycles
                        if currentCycle != numberCycles - 1:
                            r = row.Ex_split
                        else:
                            r = rest
                        for k in range(r):
                            roomSlots[listRooms[currentCycle * row.Ex_split + k]].append(exerciseInterval)

                    else:
                        for t in listTeachers:
                            teacherSlots[t].append(exerciseInterval)
                        for r in listRooms:
                            roomSlots[r].append(exerciseInterval)

        if not pd.isna(row.TP):
            listDivisions = cursusGroups.generateBalancedGroups(listCursus, row.TP_groups, constants["groupAuto"])
            tpSlots[row.ID_AA] = {
                "spread": spreadDict[row.TP_spread],
                "groups": [
                    [] for g in range(row.TP_groups)
                ],
                "cursus": listCursus
            }
            trueNumberLessons = int(row.TP / row.TP_duration)
            if constants["roundUp"]:
                modelnumberLessons = math.ceil(trueNumberLessons / constants["segmentSize"])
                delta += (modelnumberLessons * constants["segmentSize"] - trueNumberLessons) * row.TP_groups
            else:
                modelnumberLessons = math.floor(trueNumberLessons / constants["segmentSize"])
                delta -= (trueNumberLessons - modelnumberLessons * constants["segmentSize"]) * row.TP_groups
            for g in range(row.TP_groups):
                for i in range(modelnumberLessons):
                    tpInterval = cp.interval_var(start=(0, nbrSlots - 2), end=(2, nbrSlots), size=2,
                                                 name=row.ID_AA + "_tp_" + str(i) + "_g_" + str(g))

                    tpSlots[row.ID_AA]["groups"][g].append(tpInterval)
                    for k, v in listDivisions.items():
                        if v == g:
                            cursusSlots[k].append(tpInterval)
                    for t in row.TP_teachers.split(","):
                        teacherSlots[t].append(tpInterval)
                    for r in row.TP_rooms.split(","):
                        roomSlots[r].append(tpInterval)

        if not pd.isna(row.Project):
            listGroups = cursusGroups.getGroups(listCursus)
            projectSlots[row.ID_AA] = {
                "spread": spreadDict[row.Pr_spread],
                "groups": [
                    []
                ],
                "cursus": listCursus
            }
            trueNumberLessons = int(row.Project / row.Pr_duration)
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
                                                    name=row.ID_AA + "_pr")

            projectSlots[row.ID_AA]["groups"][0].extend(projectIntervals)
            for g in listGroups:
                cursusSlots[g].extend(projectIntervals)
            for t in row.Pr_teachers.split(","):
                teacherSlots[t].extend(projectIntervals)
    print("delta", delta)
    return lectureSlots,exerciseSlots,tpSlots,projectSlots,cursusSlots,teacherSlots,roomSlots,cursusGroups,AAset

def charleroiVariables(model, teacherSlots, roomSlots, constants):
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
                teacherSlots[row.Teacher].append(charleroiInterval)
                roomSlots[row.Room].append(charleroiInterval)

                blocSize4Function = cp.CpoStepFunction(steps=[(i,1 if i%4 == 0 else 0) for i in range(int(constants["weeks"] * constants["days"] * constants["slots"] / constants["segmentSize"]))])
                model.add(cp.forbid_start(interval=charleroiInterval, function=blocSize4Function))

        for i in range(partialIntervalPerWeek):
            for j in range(numberSegments):
                charleroiInterval = cp.interval_var(start=(0, nbrSlots - 2), end=(2, nbrSlots), size=2,
                                                    name=variableName + "_ch2_" + str(((i+numberFullIntervalsPerWeek) * 4) + j))

                charleroiIntervals.append(charleroiInterval)
                teacherSlots[row.Teacher].append(charleroiInterval)
                roomSlots[row.Room].append(charleroiInterval)

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

def charleroiFixedVariables(model, teacherSlots, roomSlots, constants):
    nbrSlots = int(constants["weeks"] * constants["days"] * constants["slots"] / constants["segmentSize"])
    dataCharleroi = TFEdata.loadData(constants["fileDataset"],constants["quadri"], "CharleroiFixed")
    spreadDict = {
        1.3: (1, 3),
        1.6: (1, 6),
        1.9: (1, 9),
        1.12: (1, 12),
        4.6: (4, 6),
        4.9: (4, 9),
        4.12: (4, 12),
        7.9: (7, 9),
        7.12: (7, 12),
        10.12: (10, 12)
    }
    for row in dataCharleroi.itertuples():
        variableName = row.AA
        spread = spreadDict[row.Week]
        modelStartEnd = (math.floor((spread[0] - 1) / constants["segmentSize"]), math.ceil(spread[1] / constants["segmentSize"]))
        for i in range(modelStartEnd[0],modelStartEnd[1]):
            charleroiInterval = cp.interval_var(start=(0,nbrSlots-2),end=(2,nbrSlots),size=2,name=variableName+"_ch2_"+str(i))

            teacherSlots[row.Teacher].append(charleroiInterval)
            roomSlots[row.Room].append(charleroiInterval)

            model.add(cp.start_of(charleroiInterval) == i * constants["days"] * constants["slots"] + constants["slots"] * (row.Day - 1) + row.Slot - 1)

def generateSpreads(intervals,blocSize):
    numberSpreads = math.ceil(len(intervals) / blocSize)
    spreads = [[] for i in range(numberSpreads)]
    for i in range(len(intervals)):
        spreads[math.trunc(i/blocSize)].append(intervals[i])
    return spreads