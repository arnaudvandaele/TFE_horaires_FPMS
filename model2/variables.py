import CursusGroups as TFEcursusGroups
import data.io as TFEdata

import docplex.cp.model as cp
import pandas as pd
import math
from collections import defaultdict

def instantiateVariables(nbrSlots,quadri,blocSize,cursusAllowed=None):
    lectureSlots = {}
    exerciseSlots = {}
    tpSlots = {}
    projectSlots = {}
    cursusSlots = defaultdict(list)
    teacherSlots = defaultdict(list)
    roomSlots = defaultdict(list)
    AAset = set()
    cursusGroups = TFEcursusGroups.CursusGroups({"data":"listeCours.xlsx"})
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

    data = TFEdata.loadData({"quadri":quadri,"data":"listeCours.xlsx"},"TFE")
    for row in data.itertuples():

        listCursus = row.Cursus.split(",")
        if cursusAllowed is not None and not any(cursus in listCursus for cursus in cursusAllowed):
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

            numberLessons = math.ceil(row.Lectures / 2)
            numberFullblocs = math.trunc(numberLessons/blocSize)
            sizePartialBloc = numberLessons%blocSize

            for i in range(numberFullblocs):
                lectureInterval = cp.interval_var(start=(0, nbrSlots - 1), end=(1, nbrSlots), size=1,
                                                  name=row.ID_AA + "_lec_" + str(i))

                lectureSlots[row.ID_AA]["groups"][0].append((lectureInterval,blocSize))
                for g in listGroups:
                    cursusSlots[g].append((lectureInterval,blocSize))
                for t in row.Lec_teachers.split(","):
                    teacherSlots[t].append((lectureInterval,blocSize))
                for r in row.Lec_rooms.split(","):
                    roomSlots[r].append((lectureInterval,blocSize))

            if sizePartialBloc != 0:
                lectureInterval = cp.interval_var(start=(0, nbrSlots - 1), end=(1, nbrSlots), size=1,
                                                      name=row.ID_AA + "_lec_" + str(numberFullblocs))

                lectureSlots[row.ID_AA]["groups"][0].append((lectureInterval, sizePartialBloc))
                for g in listGroups:
                    cursusSlots[g].append((lectureInterval, sizePartialBloc))
                for t in row.Lec_teachers.split(","):
                    teacherSlots[t].append((lectureInterval, sizePartialBloc))
                for r in row.Lec_rooms.split(","):
                    roomSlots[r].append((lectureInterval, sizePartialBloc))

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
                numberLessons = math.ceil(row.Exercises / 2)
                numberFullblocs = math.trunc(numberLessons / blocSize)
                sizePartialBloc = numberLessons % blocSize
                for i in range(numberFullblocs):
                    exerciseInterval = cp.interval_var(start=(0, nbrSlots - 1), end=(1, nbrSlots), size=1,
                                                       name=row.ID_AA + "_ex_" + str(i) + "_g_" + str(g))

                    exerciseSlots[row.ID_AA]["groups"][g].append((exerciseInterval,blocSize))
                    for k,v in listDivisions.items():
                        if v == g:
                            cursusSlots[k].append((exerciseInterval,blocSize))
                    for t in row.Ex_teachers.split(","):
                        teacherSlots[t].append((exerciseInterval,blocSize))
                    for r in row.Ex_rooms.split(","):
                        roomSlots[r].append((exerciseInterval,blocSize))

                if sizePartialBloc != 0:
                    exerciseInterval = cp.interval_var(start=(0, nbrSlots - 1), end=(1, nbrSlots), size=1,
                                                       name=row.ID_AA + "_ex_" + str(numberFullblocs) + "_g_" + str(g))

                    exerciseSlots[row.ID_AA]["groups"][g].append((exerciseInterval, sizePartialBloc))
                    for k, v in listDivisions.items():
                        if v == g:
                            cursusSlots[k].append((exerciseInterval, sizePartialBloc))
                    for t in row.Ex_teachers.split(","):
                        teacherSlots[t].append((exerciseInterval, sizePartialBloc))
                    for r in row.Ex_rooms.split(","):
                        roomSlots[r].append((exerciseInterval, sizePartialBloc))

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
                numberLessons = int(row.TP / row.TP_duration)
                numberFullblocs = math.trunc(numberLessons / blocSize)
                sizePartialBloc = numberLessons % blocSize
                for i in range(numberFullblocs):
                    tpInterval = cp.interval_var(start=(0, nbrSlots - 2), end=(2, nbrSlots), size=2,
                                                 name=row.ID_AA + "_tp_" + str(i) + "_g_" + str(g))

                    tpSlots[row.ID_AA]["groups"][g].append((tpInterval,blocSize))
                    for k, v in listDivisions.items():
                        if v == g:
                            cursusSlots[k].append((tpInterval,blocSize))
                    for t in row.TP_teachers.split(","):
                        teacherSlots[t].append((tpInterval,blocSize))
                    for r in row.TP_rooms.split(","):
                        roomSlots[r].append((tpInterval,blocSize))

                if sizePartialBloc != 0:
                    tpInterval = cp.interval_var(start=(0, nbrSlots - 2), end=(2, nbrSlots), size=2,
                                                 name=row.ID_AA + "_tp_" + str(numberFullblocs) + "_g_" + str(g))

                    tpSlots[row.ID_AA]["groups"][g].append((tpInterval, sizePartialBloc))
                    for k, v in listDivisions.items():
                        if v == g:
                            cursusSlots[k].append((tpInterval, sizePartialBloc))
                    for t in row.TP_teachers.split(","):
                        teacherSlots[t].append((tpInterval, sizePartialBloc))
                    for r in row.TP_rooms.split(","):
                        roomSlots[r].append((tpInterval, sizePartialBloc))

        if not pd.isna(row.Project):
            listGroups = cursusGroups.getGroups(listCursus)
            projectSlots[row.ID_AA] = {
                "spread": spreadDict[row.Pr_spread],
                "groups": [
                    []
                ],
                "cursus": listCursus
            }

            numberLessons = int(row.Project / row.Pr_duration)
            numberFullblocs = math.trunc(numberLessons / blocSize)
            sizePartialBloc = numberLessons % blocSize

            for i in range(numberFullblocs):
                projectInterval = cp.interval_var(start=(0, nbrSlots - 2), end=(2, nbrSlots), size=2,
                                                  name=row.ID_AA + "_pr_" + str(i))

                projectSlots[row.ID_AA]["groups"][0].append((projectInterval,blocSize))
                for g in listGroups:
                    cursusSlots[g].append((projectInterval,blocSize))
                for t in row.Pr_teachers.split(","):
                    teacherSlots[t].append((projectInterval,blocSize))

            if sizePartialBloc != 0:
                projectInterval = cp.interval_var(start=(0, nbrSlots - 2), end=(2, nbrSlots), size=2,
                                                  name=row.ID_AA + "_pr_" + str(numberFullblocs))

                projectSlots[row.ID_AA]["groups"][0].append((projectInterval, sizePartialBloc))
                for g in listGroups:
                    cursusSlots[g].append((projectInterval, sizePartialBloc))
                for t in row.Pr_teachers.split(","):
                    teacherSlots[t].append((projectInterval, sizePartialBloc))

    return lectureSlots,exerciseSlots,tpSlots,projectSlots,cursusSlots,teacherSlots,roomSlots,AAset,cursusGroups

# def generateSpreads(intervals,blocSize):
#     numberSpreads = math.ceil(len(intervals) / blocSize)
#     spreads = [[] for i in range(numberSpreads)]
#     for i in range(len(intervals)):
#         spreads[math.trunc(i/blocSize)].append(intervals[i])
#     return spreads