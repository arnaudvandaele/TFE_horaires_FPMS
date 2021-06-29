import math

import data.io as TFEdata
import variables as TFEvariables

import docplex.cp.model as cp
import itertools

# les séances de TP et projet ne peuvent pas commencer à des périodes impaires (durée 3h ou 4h)
def firstOrThirdSlotConstraint(model, slots, constants):
    firstOrThirdSlotOnlyFunction = cp.CpoStepFunction(steps=[(i,1 if i%2 == 0 else 0) for i in range(int(constants["weeks"] * constants["days"] * constants["slots"] / constants["segmentSize"]))])
    for AAdata in slots.values():
        for group in AAdata["groups"]:
            for interval in group:
                model.add(cp.forbid_start(interval=interval,function=firstOrThirdSlotOnlyFunction))

def morningSlotConstraint(model, slots, constants, allowed=None):
    morningOnlyFunction = cp.CpoStepFunction(steps=[(i,1 if i%4 < 2 else 0) for i in range(int(constants["weeks"] * constants["days"] * constants["slots"] / constants["segmentSize"]))])
    for AAdata in slots.values():
        if allowed is not None and not any(cursus in AAdata["cursus"] for cursus in allowed):
            continue
        for group in AAdata["groups"]:
            for interval in group:
                model.add(cp.forbid_start(interval=interval,function=morningOnlyFunction))

# toutes les séances d'un cursus/professeur/local sont disjointes
def notOverlappingConstraint(model,slots):
    for intervals in slots.values():
        model.add(cp.no_overlap(intervals))

def sameWeekDuplicatesConstraint(model, slots, constants):
    for AA,AAdata in slots.items():
        numberGroups = len(AAdata["groups"])
        numberLessons = len(AAdata["groups"][0])
        if numberGroups != 1:
            for j in range(numberLessons):
                duplicateSlots = [AAdata["groups"][i][j] for i in range(numberGroups)]
                for interval1,interval2 in itertools.combinations(duplicateSlots,2):
                    model.add(cp.trunc(cp.start_of(interval1) / (constants["days"] * constants["slots"])) ==
                              cp.trunc(cp.start_of(interval2) / (constants["days"] * constants["slots"])))

def gapBetweenDuplicatesConstraint(model, slots, constants):
    for AA,AAdata in slots.items():
        numberGroups = len(AAdata["groups"])
        numberLessons = len(AAdata["groups"][0])
        if numberGroups != 1:
            for j in range(numberLessons):
                duplicateSlots = [AAdata["groups"][i][j] for i in range(numberGroups)]
                for interval1,interval2 in itertools.combinations(duplicateSlots,2):
                    model.add(constants["gap"] >= cp.max(cp.start_of(interval1) - cp.end_of(interval2),
                                                         cp.start_of(interval2) - cp.end_of(interval1)))

def cursusUnavailabilityConstraint(model, cursusGroups, cursusSlots, constants):
    data = TFEdata.loadData(constants["fileDataset"],constants["quadri"], "Cursus")
    unavailabilityFunctions = {}

    for row in data.itertuples():
        listCursus = cursusGroups.getGroups([row.Cursus])
        startValue = math.trunc((row.Week_start - 1) / constants["segmentSize"]) * 20 + (row.Day_start - 1) * constants[
            "slots"] + (row.Slot_start - 1)
        endValue = math.trunc((row.Week_end - 1) / constants["segmentSize"]) * 20 + (row.Day_end - 1) * constants[
            "slots"] + row.Slot_end
        for c in listCursus:
            if c not in unavailabilityFunctions:
                unavailabilityFunctions[c] = cp.CpoStepFunction()
                unavailabilityFunctions[c].set_value(0, int(constants["weeks"] * constants["days"] * constants["slots"] / constants["segmentSize"]), 100)
            unavailabilityFunctions[c].set_value(startValue,endValue,0)

    for cursus,unavailabilityFunction in unavailabilityFunctions.items():
        if any(cursus in c for c in cursusSlots.keys()):
            for interval in cursusSlots[cursus]:
                model.add(cp.forbid_extent(interval,unavailabilityFunction))

def teachersUnavailabilityConstraint(model, teacherSlots, constants):
    data = TFEdata.loadData(constants["fileDataset"],constants["quadri"], "Teachers")
    unavailabilityFunctions = {}

    for row in data.itertuples():
        startValue = math.trunc((row.Week_start - 1) / constants["segmentSize"]) * 20 + (row.Day_start - 1) * constants[
            "slots"] + (row.Slot_start - 1)
        endValue = math.trunc((row.Week_end - 1) / constants["segmentSize"]) * 20 + (row.Day_end - 1) * constants[
            "slots"] + row.Slot_end
        if row.Teacher not in unavailabilityFunctions:
            unavailabilityFunctions[row.Teacher] = cp.CpoStepFunction()
            unavailabilityFunctions[row.Teacher].set_value(0, int(constants["weeks"] * constants["days"] * constants["slots"] / constants["segmentSize"]), 100)
        unavailabilityFunctions[row.Teacher].set_value(startValue, endValue, 0)

    for teacher, unavailabilityFunction in unavailabilityFunctions.items():
        if teacher in teacherSlots:
            for interval in teacherSlots[teacher]:
                model.add(cp.forbid_extent(interval, unavailabilityFunction))

def daysOffUnavailabilityConstraint(model, slots, constants):
    data = TFEdata.loadData(constants["fileDataset"],constants["quadri"], "Breaks")
    unavailabilityFunction = cp.CpoStepFunction()
    unavailabilityFunction.set_value(0, int(constants["weeks"] * constants["days"] * constants["slots"] / constants["segmentSize"]), 100)

    for row in data.itertuples():
        startValue = math.trunc((row.Week_start - 1) / constants["segmentSize"]) * 20 + (row.Day_start - 1) * constants[
            "slots"] + (row.Slot_start - 1)
        endValue = math.trunc((row.Week_end - 1) / constants["segmentSize"]) * 20 + (row.Day_end - 1) * constants[
            "slots"] + row.Slot_end
        unavailabilityFunction.set_value(startValue, endValue, 0)

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

def startAndEndConstraint(model, slots, constants):
    for AAdata in slots.values():
        for group in AAdata["groups"]:
            modelStartEnd = (math.floor((AAdata["spread"][0]-1) / constants["segmentSize"]), math.ceil(AAdata["spread"][1] / constants["segmentSize"]))
            if modelStartEnd[0] != 0:
                for interval in group:
                    model.add(cp.start_of(interval) >= modelStartEnd[0] * 20)
            if modelStartEnd[1] != constants["weeks"]/constants["segmentSize"]:
                for interval in group:
                    model.add(cp.end_of(interval) <= modelStartEnd[1] * 20)


def spreadConstraint(model, slots, constants):
    numberWeeksModel = int(constants["weeks"] / constants["segmentSize"])
    for AAdata in slots.values():
        for group in AAdata["groups"]:
            modelStartEnd = (math.floor((AAdata["spread"][0] - 1) / constants["segmentSize"]), math.ceil(AAdata["spread"][1] / constants["segmentSize"]))
            spreadTime = modelStartEnd[1]-modelStartEnd[0]
            numberFullBlocs = math.trunc(len(group)/spreadTime)
            trailingBloc = int(len(group)%spreadTime)
            for i in range(numberFullBlocs):
                for j in range(spreadTime):
                    model.add(cp.start_of(group[i * spreadTime + j]) >= (modelStartEnd[0] + j) * 20)
                    model.add(cp.end_of(group[i * spreadTime + j]) <= (modelStartEnd[0] + j + 1) * 20)
                    if i != numberFullBlocs - 1:
                        model.add(cp.end_before_start(group[i * spreadTime + j], group[(i + 1) * spreadTime + j]))
                # if trailingBloc != 0:
                #     model.add(cp.end_before_start(group[len(group)-1],group[spreadTime-1]))
                #     model.add(cp.end_before_start(group[(numberFullBlocs - 1) * spreadTime],group[numberFullBlocs * spreadTime]))

            for i in range(trailingBloc):
                if i != trailingBloc-1:
                    model.add(cp.trunc(cp.start_of(group[numberFullBlocs*spreadTime+i]) / (constants["days"] * constants["slots"])) == cp.trunc(cp.start_of(group[numberFullBlocs * spreadTime + i + 1]) / (constants["days"] * constants["slots"])) - 1)
                #     model.add(cp.end_before_start(group[numberFullBlocs * spreadTime + i], group[numberFullBlocs * spreadTime + i + 1]))
                if modelStartEnd[0] != 0:
                    model.add(cp.start_of(group[numberFullBlocs*spreadTime+i]) >= modelStartEnd[0] * 20)
                if modelStartEnd[1] != numberWeeksModel:
                    model.add(cp.end_of(group[numberFullBlocs*spreadTime+i]) <= modelStartEnd[1] * 20)
            if trailingBloc != 0 and numberFullBlocs != 0:
                trailingBlocPossibilities = spreadTime - trailingBloc + 1
                logicalOrs = []
                for i in range(trailingBlocPossibilities):
                    logicalAnds = []
                    for j in range(trailingBloc):
                        logicalAnds.append((cp.end_of(group[(numberFullBlocs-1)*spreadTime+i+j]) <= cp.start_of(group[numberFullBlocs*spreadTime+j])))
                        logicalAnds.append((cp.start_of(group[numberFullBlocs*spreadTime+j]) >= (modelStartEnd[0]+i+j) * constants["days"] * constants["slots"]))
                        logicalAnds.append((cp.end_of(group[numberFullBlocs*spreadTime+j]) <= (modelStartEnd[0]+i+j+1) * constants["days"] * constants["slots"]))
                    logicalOrs.append(cp.logical_and(logicalAnds))
                model.add(cp.logical_or(logicalOrs))

def regularityConstraint(model, slots, constants):
    for AAdata in slots.values():
        for group in AAdata["groups"]:
            spreads = TFEvariables.generateSpreads(group, constants["regularitySize"])
            for spread in spreads:
                for i in range(len(spread)-1):
                    model.add(cp.start_at_start(spread[i], spread[i + 1], delay=20))

def breakSymmetryBetweenSpreads(model, slots, constants):
    for AAdata in slots.values():
        for group in AAdata["groups"]:
            spreads = TFEvariables.generateSpreads(group, constants["regularitySize"])
            fullSpreads = [spread for spread in spreads if len(spread) == constants["regularitySize"]]
            for i in range(len(fullSpreads)-1):
                for j in range(len(fullSpreads[0])):
                    model.add(cp.end_before_start(fullSpreads[i][j],fullSpreads[i+1][j]))

def lecturesBeforeConstraint(model, lectureSlots, afterSlots, AAset, constants):
    for AA in AAset:
        if AA in lectureSlots:
            modelStartEndLecture = (
                math.floor((lectureSlots[AA]["spread"][0] - 1) / constants["segmentSize"]),
                math.ceil(lectureSlots[AA]["spread"][1] / constants["segmentSize"])
            )
            spreadTimeLecture = modelStartEndLecture[1] - modelStartEndLecture[0]
            for groupLecture in lectureSlots[AA]["groups"]:
                numberFullBlocsLecture = math.trunc(len(groupLecture) / spreadTimeLecture)
                trailingBlocLecture = int(len(groupLecture) % spreadTimeLecture)
                for slots in afterSlots:
                    if AA in slots:
                        modelStartEndSlots = (
                            math.floor((slots[AA]["spread"][0] - 1) / constants["segmentSize"]),
                            math.ceil(slots[AA]["spread"][1] / constants["segmentSize"])
                        )
                        spreadTimeSlots = modelStartEndSlots[1] - modelStartEndSlots[0]
                        if (modelStartEndLecture[0] >= modelStartEndSlots[1] or modelStartEndSlots[0] >= modelStartEndLecture[1]):
                            continue
                        else:
                            intersectionTime = (
                                max(modelStartEndLecture[0],modelStartEndSlots[0]),
                                min(modelStartEndLecture[1],modelStartEndSlots[1])
                            )
                            for groupSlots in slots[AA]["groups"]:
                                numberFullBlocsSlots = math.trunc(len(groupSlots) / spreadTimeSlots)
                                trailingBlocSlots = int(len(groupSlots) % spreadTimeSlots)

                                if trailingBlocLecture == 0:
                                    if trailingBlocSlots == 0 or numberFullBlocsSlots != 0:
                                        for i in range(intersectionTime[0],intersectionTime[1]):
                                            model.add(cp.end_before_start(
                                                groupLecture[(numberFullBlocsLecture-1)*spreadTimeLecture+i-modelStartEndLecture[0]],
                                                groupSlots[i-modelStartEndSlots[0]]
                                            ))
                                    else:
                                        trailingBlocPossibilities = spreadTimeSlots - trailingBlocSlots + 1
                                        overlapPossibilities = []
                                        for i in range(trailingBlocPossibilities):
                                            overlapPossibilities.append([(l,s) for l in range(spreadTimeLecture) for s in range(trailingBlocSlots) if l + modelStartEndLecture[0] == s + modelStartEndSlots[0] + i])
                                        logicalOrs = []
                                        for overlap in overlapPossibilities:
                                            logicalAnds = []
                                            if len(overlap) != 0:
                                                for l,s in overlap:
                                                    logicalAnds.append((cp.end_of(groupLecture[(numberFullBlocsLecture-1)*spreadTimeLecture+l]) <= cp.start_of(groupSlots[s])))
                                                    logicalAnds.append((cp.end_of(groupSlots[s]) <= (l + 1 + modelStartEndLecture[0]) * constants["days"] * constants["slots"]))
                                                    logicalAnds.append((cp.start_of(groupSlots[s]) >= (l + modelStartEndLecture[0]) * constants["days"] * constants["slots"]))
                                                logicalOrs.append(cp.logical_and(logicalAnds))
                                        model.add(cp.logical_or(logicalOrs))

                                else:
                                    if trailingBlocSlots == 0 or numberFullBlocsSlots != 0:
                                        trailingBlocPossibilities = spreadTimeLecture - trailingBlocLecture + 1
                                        overlapPossibilities = []
                                        for i in range(trailingBlocPossibilities):
                                            overlapPossibilities.append(
                                                [(l, s) for l in range(trailingBlocLecture) for s in
                                                 range(spreadTimeSlots) if
                                                 l + modelStartEndLecture[0] + i == s + modelStartEndSlots[0]])
                                        logicalOrs = []
                                        for overlap in overlapPossibilities:
                                            logicalAnds = []
                                            if len(overlap) != 0:
                                                for l, s in overlap:
                                                    logicalAnds.append((cp.end_of(groupLecture[numberFullBlocsLecture * spreadTimeLecture + l]) <= cp.start_of(groupSlots[s])))
                                                    logicalAnds.append((cp.end_of(groupLecture[numberFullBlocsLecture * spreadTimeLecture + l]) <= (s+1+modelStartEndSlots[0]) * constants["days"] * constants["slots"]))
                                                    logicalAnds.append((cp.start_of(groupLecture[numberFullBlocsLecture * spreadTimeLecture + l]) >= (s+modelStartEndSlots[0]) * constants["days"] * constants["slots"]))
                                                logicalOrs.append(cp.logical_and(logicalAnds))
                                        model.add(cp.logical_or(logicalOrs))
                                        if numberFullBlocsLecture != 0:
                                            for i in range(intersectionTime[0], intersectionTime[1]):
                                                model.add(cp.end_before_start(
                                                    groupLecture[(numberFullBlocsLecture - 1) * spreadTimeLecture + i - modelStartEndLecture[0]],
                                                    groupSlots[i - modelStartEndSlots[0]]
                                                ))
                                    else:
                                        trailingBlocPossibilitiesLectures = spreadTimeLecture - trailingBlocLecture + 1
                                        trailingBlocPossibilitiesSlots = spreadTimeSlots - trailingBlocSlots + 1
                                        overlapPossibilities = {}
                                        for i in range(trailingBlocPossibilitiesLectures):
                                            for j in range(trailingBlocPossibilitiesSlots):
                                                possibilities = [(l,s) for l in range(trailingBlocLecture) for s in
                                                     range(trailingBlocSlots) if
                                                     l + modelStartEndLecture[0] + i == s + modelStartEndSlots[0] + j]
                                                overlapPossibilities[(i+modelStartEndLecture[0],j+modelStartEndSlots[0])] = possibilities
                                        logicalOrs = []
                                        for weekKeys,overlap in overlapPossibilities.items():
                                            logicalAnds = []
                                            for l,s in overlap:
                                                logicalAnds.append((cp.end_of(groupLecture[numberFullBlocsLecture * spreadTimeLecture + l]) <= cp.start_of(groupSlots[s])))
                                            for i in range(trailingBlocLecture):
                                                logicalAnds.append((cp.end_of(groupLecture[numberFullBlocsLecture * spreadTimeLecture + i]) <= (weekKeys[0] + i + 1) * constants["days"] * constants["slots"]))
                                                logicalAnds.append((cp.start_of(groupLecture[numberFullBlocsLecture * spreadTimeLecture + i]) >= (weekKeys[0] + i) * constants["days"] * constants["slots"]))
                                            for i in range(trailingBlocSlots):
                                                logicalAnds.append((cp.end_of(groupSlots[i]) <= (weekKeys[1] + i + 1) * constants["days"] * constants["slots"]))
                                                logicalAnds.append((cp.start_of(groupSlots[i]) >= (weekKeys[1] + i) * constants["days"] * constants["slots"]))
                                                if numberFullBlocsLecture != 0 and i + weekKeys[1] in range(intersectionTime[0],intersectionTime[1]):
                                                    logicalAnds.append((cp.end_of(groupLecture[(numberFullBlocsLecture - 1) * spreadTimeLecture + i + weekKeys[1] - modelStartEndLecture[0]]) <= cp.start_of(groupSlots[i])))
                                            logicalOrs.append(cp.logical_and(logicalAnds))
                                        model.add(cp.logical_or(logicalOrs))

