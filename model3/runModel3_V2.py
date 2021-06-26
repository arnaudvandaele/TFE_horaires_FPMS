import variables as TFEvariables
import constraints as TFEconstraints
import timetable as TFEtimetable
import objectives as TFEobjectives
import callbacks as TFEcallbacks
import initialization as TFEinitialization
import data.colors as colors

import time
import docplex.cp.model as cp

t = time.localtime()
current_time = time.strftime("%H:%M:%S", t)
print(current_time)

# ----------------------------------------- DATA -----------------------------------
begin = time.time()
model = cp.CpoModel()
options = {
    "weeks":12,
    "days":5,
    "periods":4,
    "blocs":3, #(12,6,)3,2,1=runModel1
    "up": True,
    "allowed": ["BA1","BA2"],
    "quadri": "Q1",
    "delta": 0,
    "data": "listeCoursM3_V2.xlsx",
    "folder": "M3_V3"
}
lecturesDict,exercisesDict,tpsDict,projectsDict,cursusDict,teachersDict,roomsDict,cursusGroups,AAset = TFEvariables.instantiateVariables(options)
print(time.time()-begin)

TFEconstraints.cursusUnavailabilityConstraint(model,cursusGroups,cursusDict,options)

# TFEvariables.charleroiVariables(model,teachersDict,roomsDict,options)
# TFEvariables.charleroiFixedVariables(model,teachersDict,roomsDict,options)
TFEconstraints.teachersUnavailabilityConstraint(model,teachersDict,options)
# ----------------------------------------- DATA -----------------------------------


# ----------------------------------------- MANDATORY CONSTRAINTS -----------------------------------
begin = time.time()
TFEconstraints.firstOrThirdSlotConstraint(model,tpsDict,options)
TFEconstraints.firstOrThirdSlotConstraint(model,projectsDict,options)
TFEconstraints.notOverlappingConstraint(model,cursusDict)
TFEconstraints.notOverlappingConstraint(model,teachersDict)
TFEconstraints.notOverlappingConstraint(model,roomsDict)
TFEconstraints.sameWeekDuplicatesConstraint(model,exercisesDict,options)
TFEconstraints.sameWeekDuplicatesConstraint(model,tpsDict,options)
# ----------------------------------------- MANDATORY CONSTRAINTS -----------------------------------


# ----------------------------------------- BLOC CONSTRAINTS -----------------------------------
# TFEconstraints.orderingSlotsConstraint(model,lecturesDict)
# TFEconstraints.orderingSlotsConstraint(model,exercisesDict)
# TFEconstraints.orderingSlotsConstraint(model,tpsDict)
# TFEconstraints.orderingSlotsConstraint(model,projectsDict)
#
# TFEconstraints.startAndEndConstraint(model,lecturesDict,options)
# TFEconstraints.startAndEndConstraint(model,exercisesDict,options)
# TFEconstraints.startAndEndConstraint(model,tpsDict,options)
# TFEconstraints.startAndEndConstraint(model,projectsDict,options)

TFEconstraints.spreadConstraint(model,lecturesDict,options)
TFEconstraints.spreadConstraint(model,exercisesDict,options)
TFEconstraints.spreadConstraint(model,tpsDict,options)
TFEconstraints.spreadConstraint(model,projectsDict,options)

# TFEconstraints.lecturesBeforeConstraint(model,lecturesDict,[exercisesDict,tpsDict],AAset,options)
# ----------------------------------------- BLOC CONSTRAINTS -----------------------------------

# TFEconstraints.morningSlotConstraint(model,lecturesDict,options,allowed=["BA1"])

# ----------------------------------------- INITIALIZATION -----------------------------------
# TFEinitialization.simultaneousGroups(model,exercisesDict["I-PHYS-020"],exercisesDict["I-SDMA-020"])
# TFEinitialization.simultaneousGroups(model,tpsDict["I-GMEC-021"],tpsDict["I-SDMA-020"])
# TFEinitialization.fixedSlots(model,projectsDict["I-POLY-011"],(5,3),options)
#
# TFEinitialization.simultaneousGroups(model,tpsDict["I-MRDV-023"],tpsDict["I-SDMA-022"])
#
# TFEinitialization.fixedSlots(model,projectsDict["I-ILIA-024"],(5,3),options)
# ----------------------------------------- INITIALIZATION -----------------------------------


# ----------------------------------------- OBJECTIVES -----------------------------------
objectiveFunctions = []
coefficients = []

objectiveFunctions.append(TFEobjectives.avoidAfternoonSize1([lecturesDict],[],options))
coefficients.append(4)
objectiveFunctions.append(TFEobjectives.avoidLastSlotSize1([exercisesDict],["V-LANG-151","V-LANG-153","V-LANG-155"],options))
coefficients.append(1)

# model.minimize(cp.scal_prod(objectiveFunctions,coefficients))
# ----------------------------------------- OBJECTIVES -----------------------------------


# ----------------------------------------- CALLBACK -----------------------------------
model.add_solver_callback(TFEcallbacks.CallbackSolutionPrintingStatus())
# ----------------------------------------- CALLBACK -----------------------------------


# ----------------------------------------- SOLVE -----------------------------------
model.write_information()
solution = model.solve(TimeLimit=60*60*8)
print(time.time()-begin)
begin = time.time()
if solution:
    # solution.write()
    pass
    # TFEtimetable.generateAndSaveTimetables(solution,cursusDict,teachersDict,roomsDict,options,colors.COLORS)
    # TFEtimetable.generateAndSaveTimetables(solution,teachersDict,cursusDict,roomsDict,options,colors.COLORS)
    # TFEtimetable.generateAndSaveTimetables(solution, roomsDict, teachersDict, cursusDict, options, colors.COLORS)
    # TFEtimetable.generateAndDisplayTimetable(solution, cursusDict, teachersDict, roomsDict, "BA1_A", options,colors.COLORS)
    # TFEtimetable.generateAndDisplayTimetable(solution, cursusDict, teachersDict, roomsDict, "BA1_C", options,colors.COLORS)
    # TFEtimetable.generateAndDisplayTimetable(solution, cursusDict, teachersDict, roomsDict, "BA1_E", options,colors.COLORS)
    # TFEtimetable.generateAndDisplayTimetable(solution, roomsDict, teachersDict, cursusDict, "Ho.12", options, colors.COLORS)
    # TFEtimetable.generateAndDisplayTimetable(solution, teachersDict, cursusDict, roomsDict, "Vandaele A", options,colors.COLORS)
else:
    print("No solution. Conflict refiner")
    conflicts = model.refine_conflict()
    conflicts.write()
print(time.time()-begin)
# ----------------------------------------- SOLVE -----------------------------------