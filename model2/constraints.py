import data.io as TFEdata
import variables as TFEvariables

import docplex.cp.model as cp
import itertools

def blocStructureConstraint(model,slots):
    for AAdata in slots.values():
        for group in AAdata["groups"]:
            for interval,size in group:
                model.add(cp.start_of(interval) <= (12-size+1) * 20 - 1)

# les séances de TP et projet ne peuvent pas commencer à des périodes impaires (durée 3h ou 4h)
def firstOrThirdSlotConstraint(model,nbrSlots,slots):
    firstSlotOnlyFunction = cp.CpoStepFunction(steps=[(i,1 if i%2 == 0 else 0) for i in range(nbrSlots)])
    for AAdata in slots.values():
        for group in AAdata["groups"]:
            for interval,size in group:
                model.add(cp.forbid_start(interval=interval,function=firstSlotOnlyFunction))

# chaque séance est numérotée et chronologique (briser la symétrie)
def orderingSlotsConstraint(model,slots,blocSize):
    for AAdata in slots.values():
        for group in AAdata["groups"]:
            fullBlocs = [interval for interval,size in group if size == blocSize]
            for i in range(len(fullBlocs)-1):
                model.add(cp.end_before_start(fullBlocs[i],fullBlocs[i+1]))

# toutes les séances d'un cursus/professeur/local sont disjointes
def notOverlappingConstraint(model,slots):
    for listIntervals in slots.values():
        for interval1,interval2 in itertools.combinations(listIntervals,2):
            forbids = [cp.start_of(interval2[0]) + i for i in range(-20*(interval1[1]-1),20*interval2[1],20)]
            model.add(cp.forbidden_assignments(cp.start_of(interval1[0]),forbids))

# les séances dupliquées (ex/tp) sont disjointes
def duplicateSlotsNotOverlappingConstraint(model,slots):
    for AAdata in slots.values():
        if len(AAdata["groups"]) != 1:
            listIntervals = [(interval,size) for group in AAdata["groups"] for interval,size in group]
            cumulFunction = cp.step_at(0,0)
            for interval,size in listIntervals:
                cumulFunction += cp.pulse(interval,1)
                for i in range(size - 1):
                    cumulFunction += cp.step_at(cp.start_of(interval) + 20, 1)
                    cumulFunction -= cp.step_at(cp.start_of(interval) + cp.size_of(interval) + 20, 1)
            model.add(cp.cumul_range(cumulFunction,0,1))

# TODO de ici jusque... ---------------------------------------------
# TODO de ici jusque... ---------------------------------------------
# TODO de ici jusque... ---------------------------------------------
# TODO de ici jusque... ---------------------------------------------
def gapBetweenDuplicatesConstraint(model,slots,gap):
    for AA,AAdata in slots.items():
        numberGroups = len(AAdata["groups"])
        numberLessons = len(AAdata["groups"][0])
        if numberGroups != 1:
            for j in range(numberLessons):
                duplicateSlots = []
                for i in range(numberGroups):
                    duplicateSlots.append(AAdata["groups"][i][j])
                for interval1,interval2 in itertools.combinations(duplicateSlots,2):
                    model.add(gap >= cp.max(cp.start_of(interval1) - cp.end_of(interval2),
                                            cp.start_of(interval2) - cp.end_of(interval1)))

def cursusUnavailabilityConstraint(model,quadri,numberSlots,cursusGroups,cursusSlots):
    data = TFEdata.loadData({"quadri":quadri,"data":"listeCours.xlsx"},"Cursus")
    unavailabilityFunctions = {}

    for row in data.itertuples():
        listCursus = cursusGroups.getGroups([row.Cursus])
        for c in listCursus:
            if c not in unavailabilityFunctions:
                unavailabilityFunctions[c] = cp.CpoStepFunction()
                unavailabilityFunctions[c].set_value(0,numberSlots,1)
            unavailabilityFunctions[c].set_value(row.Start,row.End,0)

    for cursus,unavailabilityFunction in unavailabilityFunctions.items():
        if any(cursus in c for c in cursusSlots.keys()):
            for interval in cursusSlots[cursus]:
                model.add(cp.forbid_extent(interval,unavailabilityFunction))

def teachersUnavailabilityConstraint(model,quadri,numberSlots,teacherSlots):
    data = TFEdata.loadData({"quadri":quadri,"data":"listeCours.xlsx"},"Teachers")
    unavailabilityFunctions = {}

    for row in data.itertuples():
        if row.Teacher not in unavailabilityFunctions:
            unavailabilityFunctions[row.Teacher] = cp.CpoStepFunction()
            unavailabilityFunctions[row.Teacher].set_value(0, numberSlots, 1)
        unavailabilityFunctions[row.Teacher].set_value(row.Start, row.End, 0)

    for teacher, unavailabilityFunction in unavailabilityFunctions.items():
        if teacher in teacherSlots:
            for interval in teacherSlots[teacher]:
                model.add(cp.forbid_extent(interval, unavailabilityFunction))

def daysOffUnavailabilityConstraint(model,quadri,numberSlots,slots):
    data = TFEdata.loadData({"quadri":quadri,"data":"listeCours.xlsx"},"Breaks")
    unavailabilityFunction = cp.CpoStepFunction()
    unavailabilityFunction.set_value(0,numberSlots,1)

    for row in data.itertuples():
        unavailabilityFunction.set_value(row.Start,row.End,0)

    for AAdata in slots.values():
        for group in AAdata["groups"]:
            for interval in group:
                model.add(cp.forbid_extent(interval,unavailabilityFunction))

def startAndEndConstraint(model,slots):
    for AAdata in slots.values():
        for group in AAdata["groups"]:
            if AAdata["spread"][0] != 1:
                for interval in group:
                    model.add(cp.start_of(interval) >= (AAdata["spread"][0] - 1) * 20)
            if AAdata["spread"][1] != 12:
                for interval in group:
                    model.add(cp.end_of(interval) <= AAdata["spread"][1] * 20)
# TODO jusqu'ici -------------------------------------------------------
# TODO jusqu'ici -------------------------------------------------------
# TODO jusqu'ici -------------------------------------------------------
# TODO jusqu'ici -------------------------------------------------------