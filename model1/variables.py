import CursusGroups as TFEcursusGroups
import data.io as TFEdata

import docplex.cp.model as cp
import pandas as pd
import math
from collections import defaultdict

# liste de variables au lieu de faire variable par variable ?
def instantiateVariables(options):
    lectureSlots = {}
    exerciseSlots = {}
    tpSlots = {}
    projectSlots = {}
    cursusSlots = defaultdict(list)
    teacherSlots = defaultdict(list)
    roomSlots = defaultdict(list)
    AAset = set()
    cursusGroups = TFEcursusGroups.CursusGroups(options)
    nbrSlots = int(options["weeks"]*options["days"]*options["periods"])
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
        9.12: (9,12)
    }

    data = TFEdata.loadData(options,"TFE")
    for row in data.itertuples():

        listCursus = row.Cursus.split(",")
        if options["allowed"] is not None and not any(cursus in listCursus for cursus in options["allowed"]):
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
            for i in range(math.ceil(row.Lectures / 2)):
                lectureInterval = cp.interval_var(start=(0, nbrSlots - 1), end=(1, nbrSlots), size=1,
                                                  name=row.ID_AA + "_lec_" + str(i))

                lectureSlots[row.ID_AA]["groups"][0].append(lectureInterval)
                for g in listGroups:
                    cursusSlots[g].append(lectureInterval)
                for t in row.Lec_teachers.split(","):
                    teacherSlots[t].append(lectureInterval)
                for r in row.Lec_rooms.split(","):
                    roomSlots[r].append(lectureInterval)

        if not pd.isna(row.Exercises):
            listDivisions = cursusGroups.generateBalancedGroups(listCursus, row.Ex_groups)
            exerciseSlots[row.ID_AA] = {
                "spread": spreadDict[row.Ex_spread],
                "groups": [
                    [] for g in range(row.Ex_groups)
                ],
                "cursus": listCursus
            }
            for g in range(row.Ex_groups):
                for i in range(math.ceil(row.Exercises / 2)):
                    exerciseInterval = cp.interval_var(start=(0, nbrSlots - 1), end=(1, nbrSlots), size=1,
                                                       name=row.ID_AA + "_ex_" + str(i) + "_g_" + str(g))

                    exerciseSlots[row.ID_AA]["groups"][g].append(exerciseInterval)
                    for k,v in listDivisions.items():
                        if v == g:
                            cursusSlots[k].append(exerciseInterval)
                    for t in row.Ex_teachers.split(","):
                        teacherSlots[t].append(exerciseInterval)
                    for r in row.Ex_rooms.split(","):
                        roomSlots[r].append(exerciseInterval)

        if not pd.isna(row.TP):
            listDivisions = cursusGroups.generateBalancedGroups(listCursus, row.TP_groups)
            tpSlots[row.ID_AA] = {
                "spread": spreadDict[row.TP_spread],
                "groups": [
                    [] for g in range(row.TP_groups)
                ],
                "cursus": listCursus
            }
            for g in range(row.TP_groups):
                for i in range(int(row.TP / row.TP_duration)):
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
            for i in range(int(row.Project / row.Pr_duration)):
                projectInterval = cp.interval_var(start=(0, nbrSlots - 2), end=(2, nbrSlots), size=2,
                                                  name=row.ID_AA + "_pr_" + str(i))

                projectSlots[row.ID_AA]["groups"][0].append(projectInterval)
                for g in listGroups:
                    cursusSlots[g].append(projectInterval)
                for t in row.Pr_teachers.split(","):
                    teacherSlots[t].append(projectInterval)

    return lectureSlots,exerciseSlots,tpSlots,projectSlots,cursusSlots,teacherSlots,roomSlots,AAset,cursusGroups

def generateSpreads(intervals,blocSize):
    numberSpreads = math.ceil(len(intervals) / blocSize)
    spreads = [[] for i in range(numberSpreads)]
    for i in range(len(intervals)):
        spreads[math.trunc(i/blocSize)].append(intervals[i])
    return spreads