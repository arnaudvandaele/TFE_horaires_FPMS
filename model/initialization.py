import math

import data.io as TFEdata
import variables as TFEvariables

import docplex.cp.model as cp
import itertools

def simultaneousGroups(model,slots1,slots2):
    numberGroups1 = len(slots1["divisions"])
    numberGroups2 = len(slots2["divisions"])
    if slots1["weekBounds"] == slots2["weekBounds"] and numberGroups1 == numberGroups2 and set(
            slots1["cursus"]) == set(slots2["cursus"]) and numberGroups1%2 == 0:
        for i in range(numberGroups1):
            for j in range(len(slots1["divisions"][0])):
                model.add(cp.start_at_start(slots1["divisions"][i][j],slots2["divisions"][numberGroups2-1-i][j]))
    else:
        print("ko")

def fixedSlots(model, slots, timing, constants):
    numberSlots = len(slots["divisions"][0])
    startWeek = math.floor((slots["weekBounds"][0]-1) / constants["segmentSize"])
    endWeek = math.ceil(slots["weekBounds"][1] / constants["segmentSize"])
    if endWeek - startWeek == numberSlots and 1 <= timing[0] <= constants["days"] and 1 <= timing[1] <= constants["slots"]:
        for i,slot in enumerate(slots["divisions"][0]):
            model.add(cp.start_of(slot) == i * constants["days"] * constants["slots"] + (timing[0] - 1) * constants["slots"] + timing[1] - 1)
