import variables as TFEvariables
import constraints as TFEconstraints
import timetable as TFEtimetable

import time
import docplex.cp.model as cp

begin = time.time()

quadri = "Q1"
nbrWeeks = 12
nbrDays = 5
nbrPeriods = 4
nbrSlots = nbrWeeks*nbrDays*nbrPeriods
blocSize = 6
cursusAllowed = None

lecturesDict,exercisesDict,tpsDict,projectsDict,cursusDict,teachersDict,roomsDict,AAset,cursusGroups = TFEvariables.instantiateVariables(nbrSlots,quadri,blocSize,cursusAllowed)

print(time.time()-begin)
begin = time.time()

model = cp.CpoModel()
TFEconstraints.blocStructureConstraint(model,lecturesDict)
TFEconstraints.blocStructureConstraint(model,exercisesDict)
TFEconstraints.blocStructureConstraint(model,tpsDict)
TFEconstraints.blocStructureConstraint(model,projectsDict)
TFEconstraints.firstOrThirdSlotConstraint(model,nbrSlots,tpsDict)
TFEconstraints.firstOrThirdSlotConstraint(model,nbrSlots,projectsDict)
TFEconstraints.orderingSlotsConstraint(model,lecturesDict,blocSize)
TFEconstraints.orderingSlotsConstraint(model,exercisesDict,blocSize)
TFEconstraints.orderingSlotsConstraint(model,tpsDict,blocSize)
TFEconstraints.orderingSlotsConstraint(model,projectsDict,blocSize)
TFEconstraints.notOverlappingConstraint(model,cursusDict)
TFEconstraints.notOverlappingConstraint(model,teachersDict)
TFEconstraints.notOverlappingConstraint(model,roomsDict)
# TFEconstraints.duplicateSlotsNotOverlappingConstraint(model,exercisesDict)
# TFEconstraints.duplicateSlotsNotOverlappingConstraint(model,tpsDict)
# TFEconstraints.gapBetweenDuplicatesConstraint(model,exercisesDict,16)
# TFEconstraints.gapBetweenDuplicatesConstraint(model,tpsDict,16)

print(time.time()-begin)
begin = time.time()


# TFEconstraints.cursusUnavailabilityConstraint(model,quadri,nbrSlots,cursusGroups,cursusDict)
# TFEconstraints.teachersUnavailabilityConstraint(model,quadri,nbrSlots,teachersDict)
# TFEconstraints.daysOffUnavailabilityConstraint(model,quadri,nbrSlots,lecturesDict)
# TFEconstraints.daysOffUnavailabilityConstraint(model,quadri,nbrSlots,exercisesDict)
# TFEconstraints.daysOffUnavailabilityConstraint(model,quadri,nbrSlots,tpsDict)
# TFEconstraints.daysOffUnavailabilityConstraint(model,quadri,nbrSlots,projectsDict)


print(time.time()-begin)
begin = time.time()

# TFEconstraints.startAndEndConstraint(model,lecturesDict)
# TFEconstraints.startAndEndConstraint(model,exercisesDict)
# TFEconstraints.startAndEndConstraint(model,tpsDict)
# TFEconstraints.startAndEndConstraint(model,projectsDict)

print(time.time()-begin)
begin = time.time()

model.write_information()
solution = model.solve()
print(time.time()-begin)
begin = time.time()
if solution:
    solution.write()
    # TFEtimetable.generateAndSaveTimetables(solution,nbrPeriods,nbrDays,nbrWeeks,cursusDict,teachersDict,roomsDict)
    # TFEtimetable.generateAndDisplayTimetable(solution,nbrPeriods,nbrDays,nbrWeeks,cursusDict,teachersDict,roomsDict,"BA1_A")
else:
    print("No solution. Conflict refiner")
    conflicts = model.refine_conflict()
    conflicts.write()

print(time.time()-begin)