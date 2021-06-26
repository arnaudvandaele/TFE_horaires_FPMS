import math

import data.io as TFEdata
import variables as TFEvariables

import docplex.cp.model as cp
import itertools

def simultaneousGroups(model,slots1,slots2):
    numberGroups1 = len(slots1["groups"])
    numberGroups2 = len(slots2["groups"])
    if slots1["spread"] == slots2["spread"] and numberGroups1 == numberGroups2 and set(
            slots1["cursus"]) == set(slots2["cursus"]) and numberGroups1%2 == 0:
        for i in range(numberGroups1):
            for j in range(len(slots1["groups"][0])):
                model.add(cp.start_at_start(slots1["groups"][i][j],slots2["groups"][numberGroups2-1-i][j]))
    else:
        print("ko")

def fixedSlots(model,slots,timing,options):
    numberSlots = len(slots["groups"][0])
    startWeek = math.floor((slots["spread"][0]-1)/options["blocs"])
    endWeek = math.ceil(slots["spread"][1]/options["blocs"])
    if endWeek - startWeek == numberSlots and 1 <= timing[0] <= options["days"] and 1 <= timing[1] <= options["periods"]:
        for i,slot in enumerate(slots["groups"][0]):
            model.add(cp.start_of(slot) == i*options["days"]*options["periods"] + (timing[0]-1)*options["periods"]+timing[1]-1)
