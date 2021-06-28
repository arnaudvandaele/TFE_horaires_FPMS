import docplex.cp.model as cp

def avoidAfternoonSize1(arraySlots,blacklist,options):
    afternoonPenalty = cp.CpoSegmentedFunction()
    for i in range(int(options["weeks"] * options["days"] * options["periods"] / options["blocs"])):
        slotNumber = i%4
        if slotNumber == 0:
            afternoonPenalty.set_value(i,i+1,0)
        elif slotNumber == 1:
            afternoonPenalty.set_value(i,i+1,0)
        elif slotNumber == 2:
            afternoonPenalty.set_value(i,i+1,0.5)
        elif slotNumber == 3:
            afternoonPenalty.set_value(i,i+1,1)
    objectiveValue = cp.sum(
        [cp.start_eval(interval, afternoonPenalty) for slots in arraySlots for AA,AAdata in slots.items() for group in
         AAdata["groups"] for interval in group if AA not in blacklist])
    return objectiveValue

def avoidAfternoonSize2(arraySlots,blacklist,options):
    afternoonPenalty = cp.CpoSegmentedFunction()
    for i in range(int((options["weeks"] * options["days"] * options["periods"] / options["blocs"]) / 2 + 1)):
        slotNumber = i % 2
        if slotNumber == 0:
            afternoonPenalty.set_value(2 * i, 2 * (i + 1), 1)
        elif slotNumber == 1:
            afternoonPenalty.set_value(2 * i, 2 * (i + 1), 0)

    objectiveValue = cp.sum(
        [cp.end_eval(interval, afternoonPenalty) for slots in arraySlots for AA,AAdata in slots.items() for group in
         AAdata["groups"] for interval in group if AA not in blacklist])
    return objectiveValue

def avoidLastSlotSize1(arraySlots,blacklist,options):
    lastSlotPenalty = cp.CpoSegmentedFunction()
    for i in range(int(options["weeks"] * options["days"] * options["periods"] / options["blocs"])):
        slotNumber = i % 4
        if slotNumber == 3:
            lastSlotPenalty.set_value(i, i + 1, 1)


    objectiveValue = cp.sum(
        [cp.start_eval(interval, lastSlotPenalty) for slots in arraySlots for AA,AAdata in slots.items() for group in
         AAdata["groups"] for interval in group if AA not in blacklist])
    return objectiveValue

def spreadSlots(lecturesDict,exercisesDict,tpsDict,projectsDict,AAset):
    spreadExpression = 0
    for AA in AAset:
        hasLec = AA in lecturesDict
        hasEx = AA in exercisesDict
        hasTP = AA in tpsDict
        hasPr = AA in projectsDict

        spreadMode = hasLec*1 + hasEx*2 + hasTP*4 + hasPr*8
        if spreadMode == 1:
            spreadExpression += cp.square(cp.standard_deviation(
                [cp.start_of(lecturesDict[AA][i+1]) - cp.start_of(lecturesDict[AA][i]) for i in
                 range(len(lecturesDict[AA])-1)]))
        elif spreadMode == 2:
            for exerciceIntervals in exercisesDict[AA]:
                spreadExpression += cp.square(cp.standard_deviation(
                    [cp.start_of(exerciceIntervals[i+1]) - cp.start_of(exerciceIntervals[i]) for i in
                    range(len(exerciceIntervals)-1)]))
        elif spreadMode == 4:
            for tpIntervals in tpsDict[AA]:
                spreadExpression += cp.square(cp.standard_deviation(
                    [cp.start_of(tpIntervals[i+1]) - cp.start_of(tpIntervals[i]) for i in
                     range(len(tpIntervals)-1)]))
        elif spreadMode == 8:
            spreadExpression += cp.square(cp.standard_deviation(
                [cp.start_of(projectsDict[AA][i+1]) - cp.start_of(projectsDict[AA][i]) for i in
                 range(len(projectsDict[AA])-1)]))
        else:
            pass
    return spreadExpression