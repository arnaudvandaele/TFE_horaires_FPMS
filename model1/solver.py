import variables as TFEvariables

import docplex.cp.model as cp

def addSearchPhaseWithFirstVariables(model,slots,blocSize):
    fullBlocs = []
    for AAdata in slots.values():
        for group in AAdata["groups"]:
            spreads = TFEvariables.generateSpreads(group,blocSize)
            fullBlocs.extend([interval for spread in spreads for interval in spread if len(spread)==blocSize])
    if len(fullBlocs) != 0:
        model.add(cp.search_phase(vars=fullBlocs))
