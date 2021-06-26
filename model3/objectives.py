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