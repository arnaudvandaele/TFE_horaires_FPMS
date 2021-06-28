import data.io as TFEdata
import variables as TFEvariables

import docplex.cp.model as cp
import itertools

# les séances de TP et projet ne peuvent pas commencer à des périodes impaires (durée 3h ou 4h)
def firstOrThirdSlotConstraint(model,slots,options):
    firstSlotOnlyFunction = cp.CpoStepFunction(steps=[(i,1 if i%2 == 0 else 0) for i in range(int(options["weeks"]*options["days"]*options["periods"]))])
    for AAdata in slots.values():
        for group in AAdata["groups"]:
            for interval in group:
                model.add(cp.forbid_start(interval=interval,function=firstSlotOnlyFunction))

# toutes les séances d'un cursus/professeur/local sont disjointes
def notOverlappingConstraint(model,slots):
    for intervals in slots.values():
        model.add(cp.no_overlap(intervals))

# les séances dupliquées (ex/tp) sont disjointes
# def duplicateSlotsNotOverlappingConstraint(model,slots):
#     for AAdata in slots.values():
#         if len(AAdata["groups"]) != 1:
#             model.add(cp.no_overlap([interval for group in AAdata["groups"] for interval in group]))

def gapBetweenDuplicatesConstraint(model,slots,options):
    for AA,AAdata in slots.items():
        numberGroups = len(AAdata["groups"])
        numberLessons = len(AAdata["groups"][0])
        if numberGroups != 1:
            for j in range(numberLessons):
                duplicateSlots = [AAdata["groups"][i][j] for i in range(numberGroups)]
                for interval1,interval2 in itertools.combinations(duplicateSlots,2):
                    model.add(options["gap"] >= cp.max(cp.start_of(interval1) - cp.end_of(interval2),
                                            cp.start_of(interval2) - cp.end_of(interval1)))

def cursusUnavailabilityConstraint(model,cursusGroups,cursusSlots,options):
    data = TFEdata.loadData(options,"Cursus")
    unavailabilityFunctions = {}

    for row in data.itertuples():
        listCursus = cursusGroups.getGroups([row.Cursus])
        for c in listCursus:
            if c not in unavailabilityFunctions:
                unavailabilityFunctions[c] = cp.CpoStepFunction()
                unavailabilityFunctions[c].set_value(0,int(options["weeks"]*options["days"]*options["periods"]),1)
            unavailabilityFunctions[c].set_value(row.Start,row.End,0)

    for cursus,unavailabilityFunction in unavailabilityFunctions.items():
        if any(cursus in c for c in cursusSlots.keys()):
            for interval in cursusSlots[cursus]:
                model.add(cp.forbid_extent(interval,unavailabilityFunction))

def teachersUnavailabilityConstraint(model,teacherSlots,options):
    data = TFEdata.loadData(options,"Teachers")
    unavailabilityFunctions = {}

    for row in data.itertuples():
        if row.Teacher not in unavailabilityFunctions:
            unavailabilityFunctions[row.Teacher] = cp.CpoStepFunction()
            unavailabilityFunctions[row.Teacher].set_value(0, int(options["weeks"]*options["days"]*options["periods"]), 1)
        unavailabilityFunctions[row.Teacher].set_value(row.Start, row.End, 0)

    for teacher, unavailabilityFunction in unavailabilityFunctions.items():
        if teacher in teacherSlots:
            for interval in teacherSlots[teacher]:
                model.add(cp.forbid_extent(interval, unavailabilityFunction))

def daysOffUnavailabilityConstraint(model,slots,options):
    data = TFEdata.loadData(options,"Breaks")
    unavailabilityFunction = cp.CpoStepFunction()
    unavailabilityFunction.set_value(0,int(options["weeks"]*options["days"]*options["periods"]),1)

    for row in data.itertuples():
        unavailabilityFunction.set_value(row.Start,row.End,0)

    for AAdata in slots.values():
        for group in AAdata["groups"]:
            for interval in group:
                model.add(cp.forbid_extent(interval,unavailabilityFunction))

# chaque séance est numérotée et chronologique (briser la symétrie)
def orderingSlotsConstraint(model,slots):
    for AAdata in slots.values():
        for group in AAdata["groups"]:
            for i in range(len(group)-1):
                model.add(cp.end_before_start(group[i],group[i+1]))

def spreadConstraint(model,slots,options):
    for AAdata in slots.values():
        for group in AAdata["groups"]:
            spreads = TFEvariables.generateSpreads(group,options["bloc"])
            for spread in spreads:
                for i in range(len(spread)-1):
                    model.add(cp.start_at_start(spread[i], spread[i + 1], delay=20))

def breakSymmetryBetweenSpreads(model,slots,options):
    for AAdata in slots.values():
        for group in AAdata["groups"]:
            spreads = TFEvariables.generateSpreads(group,options["bloc"])
            fullSpreads = [spread for spread in spreads if len(spread)==options["bloc"]]
            for i in range(len(fullSpreads)-1):
                for j in range(len(fullSpreads[0])):
                    model.add(cp.end_before_start(fullSpreads[i][j],fullSpreads[i+1][j]))

def startAndEndConstraint(model,slots):
    for AAdata in slots.values():
        for group in AAdata["groups"]:
            if AAdata["spread"][0] != 1:
                for interval in group:
                    model.add(cp.start_of(interval) >= (AAdata["spread"][0] - 1) * 20)
            if AAdata["spread"][1] != 12:
                for interval in group:
                    model.add(cp.end_of(interval) <= AAdata["spread"][1] * 20)