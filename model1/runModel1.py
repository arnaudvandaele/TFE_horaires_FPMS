import variables as TFEvariables
import constraints as TFEconstraints
import timetable as TFEtimetable
import solver as TFEsolver
import data.colors as colors

import time
import docplex.cp.model as cp

t = time.localtime()
current_time = time.strftime("%H:%M:%S", t)
print(current_time)

begin = time.time()
model = cp.CpoModel()
options = {
    "weeks":12,
    "days":5,
    "periods":4,
    "bloc": 6,
    "allowed": None,
    "quadri": "Q1",
    "data": "listeCoursM1.xlsx",
    "folder": "M1_1",
    "gap": 16
}

lecturesDict,exercisesDict,tpsDict,projectsDict,cursusDict,teachersDict,roomsDict,AAset,cursusGroups = TFEvariables.instantiateVariables(options)

print(time.time()-begin)
begin = time.time()


TFEconstraints.firstOrThirdSlotConstraint(model,tpsDict,options)
TFEconstraints.firstOrThirdSlotConstraint(model,projectsDict,options)
TFEconstraints.notOverlappingConstraint(model,cursusDict)
TFEconstraints.notOverlappingConstraint(model,teachersDict)
TFEconstraints.notOverlappingConstraint(model,roomsDict)
# TFEconstraints.duplicateSlotsNotOverlappingConstraint(model,exercisesDict)
# TFEconstraints.duplicateSlotsNotOverlappingConstraint(model,tpsDict)
TFEconstraints.gapBetweenDuplicatesConstraint(model,exercisesDict,options)
TFEconstraints.gapBetweenDuplicatesConstraint(model,tpsDict,options)

print(time.time()-begin)
begin = time.time()

TFEconstraints.cursusUnavailabilityConstraint(model,cursusGroups,cursusDict,options)
TFEconstraints.teachersUnavailabilityConstraint(model,teachersDict,options)
# TFEconstraints.daysOffUnavailabilityConstraint(model,lecturesDict,options)
# TFEconstraints.daysOffUnavailabilityConstraint(model,exercisesDict,options)
# TFEconstraints.daysOffUnavailabilityConstraint(model,tpsDict,options)
# TFEconstraints.daysOffUnavailabilityConstraint(model,projectsDict,options)

print(time.time()-begin)
begin = time.time()

TFEconstraints.startAndEndConstraint(model,lecturesDict)
TFEconstraints.startAndEndConstraint(model,exercisesDict)
TFEconstraints.startAndEndConstraint(model,tpsDict)
TFEconstraints.startAndEndConstraint(model,projectsDict)

TFEconstraints.orderingSlotsConstraint(model,lecturesDict)
TFEconstraints.orderingSlotsConstraint(model,exercisesDict)
TFEconstraints.orderingSlotsConstraint(model,tpsDict)
TFEconstraints.orderingSlotsConstraint(model,projectsDict)

# BA2 blocsize 6 : 50 s
# BA1 blocsize 6 : 35 min sans mercredi après midi, 0.19 s avec
# BA3_CHIM blocsize 6 : 0.09 s
# BA3_ELEC blocsize 6 : 0.12 s
# BA3_IG blocsize 6 : 0.13 s
# BA3_MECA blocsize 6 : 2.92 s
# BA3_MIN blocsize 6 : 0.08 s
# ["BA2","BA3_CHIM","BA3_ELEC","BA3_MECA","BA3_IG","BA3_MIN"] blocsize 6 : 43 min
# TFEconstraints.spreadConstraint(model,lecturesDict,options)
# TFEconstraints.spreadConstraint(model,exercisesDict,options)
# TFEconstraints.spreadConstraint(model,tpsDict,options)
# TFEconstraints.spreadConstraint(model,projectsDict,options)
# TFEconstraints.breakSymmetryBetweenSpreads(model,lecturesDict,options)
# TFEconstraints.breakSymmetryBetweenSpreads(model,exercisesDict,options)
# TFEconstraints.breakSymmetryBetweenSpreads(model,tpsDict,options)
# TFEconstraints.breakSymmetryBetweenSpreads(model,projectsDict,options)


print(time.time()-begin)
begin = time.time()

# TFEsolver.addSearchPhaseWithFirstVariables(model,lecturesDict,blocSize)
# TFEsolver.addSearchPhaseWithFirstVariables(model,exercisesDict,blocSize)
# TFEsolver.addSearchPhaseWithFirstVariables(model,tpsDict,blocSize)
# TFEsolver.addSearchPhaseWithFirstVariables(model,projectsDict,blocSize)

model.write_information()
solution = model.solve()
print(time.time()-begin)
begin = time.time()
if solution:
    # solution.write()
    pass
    TFEtimetable.generateAndSaveTimetables(solution,cursusDict,teachersDict,roomsDict,options,colors.COLORS)
    TFEtimetable.generateAndSaveTimetables(solution,teachersDict,cursusDict,roomsDict,options,colors.COLORS)
    TFEtimetable.generateAndSaveTimetables(solution, roomsDict, teachersDict, cursusDict, options, colors.COLORS)
    # TFEtimetable.generateAndDisplayTimetable(solution, cursusDict, teachersDict, roomsDict, "BA1_A", options,colors.COLORS)
    # TFEtimetable.generateAndDisplayTimetable(solution, cursusDict, teachersDict, roomsDict, "BA1_B", options,colors.COLORS)
    # TFEtimetable.generateAndDisplayTimetable(solution, roomsDict, teachersDict, cursusDict, "Ho.12", options, colors.COLORS)
    # TFEtimetable.generateAndDisplayTimetable(solution, teachersDict, cursusDict, roomsDict, "Vandaele A", options,colors.COLORS)
else:
    print("No solution. Conflict refiner")
    conflicts = model.refine_conflict()
    conflicts.write()

print(time.time()-begin)