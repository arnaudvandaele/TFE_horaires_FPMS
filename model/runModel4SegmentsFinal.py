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
print("Beginning : ",current_time)

print("Building model : ...")
begin = time.time()
model = cp.CpoModel()
constants = {
    "weeks":12,
    "days":5,
    "slots":4,
    "segmentSize":3,
    "roundUp": True,
    "cursus": {
        "BA1": True,
        "BA2": True,
        "BA3_CHIM": True,
        "BA3_ELEC": True,
        "BA3_IG": True,
        "BA3_MECA": True,
        "BA3_MIN": True
    },
    "quadri": "Q1",
    "fileDataset": "datasetFinal.xlsx",
    "folderResults": "4SegmentsFinal",
    "groupAuto": False
}

lecturesDict, exercisesDict, tpsDict, projectsDict, \
cursusIntervalVariables, teachersIntervalVariables, roomsIntervalVariables, \
cursusGroups, AAset = TFEvariables.generateIntervalVariables(constants)

TFEconstraints.cursusUnavailabilityConstraint(model, cursusGroups, cursusIntervalVariables, constants)

TFEconstraints.firstOrThirdSlotConstraint(model, tpsDict, constants)
TFEconstraints.firstOrThirdSlotConstraint(model, projectsDict, constants)
TFEconstraints.notOverlappingConstraint(model, cursusIntervalVariables)
TFEconstraints.notOverlappingConstraint(model, teachersIntervalVariables)
TFEconstraints.notOverlappingConstraint(model, roomsIntervalVariables)
TFEconstraints.sameWeekDuplicatesConstraint(model, exercisesDict, constants)
TFEconstraints.sameWeekDuplicatesConstraint(model, tpsDict, constants)

TFEconstraints.spreadConstraint(model, lecturesDict, constants)
TFEconstraints.spreadConstraint(model, exercisesDict, constants)
TFEconstraints.spreadConstraint(model, tpsDict, constants)
TFEconstraints.spreadConstraint(model, projectsDict, constants)

TFEconstraints.lecturesBeforeConstraint(model, lecturesDict, [exercisesDict,tpsDict], AAset, constants)

TFEinitialization.simultaneousGroups(model,exercisesDict["I-PHYS-020"],exercisesDict["I-SDMA-020"])
TFEinitialization.fixedSlots(model, projectsDict["I-POLY-011"], (5,3), constants)
TFEinitialization.fixedSlots(model, projectsDict["I-ILIA-024"], (5,3), constants)

objectiveFunctions = []
coefficients = []
objectiveFunctions.append(TFEobjectives.avoidAfternoonSize1([lecturesDict], [], constants))
coefficients.append(4)
objectiveFunctions.append(TFEobjectives.avoidLastSlotSize1([exercisesDict], ["V-LANG-151","V-LANG-153","V-LANG-155"], constants))
coefficients.append(1)
model.minimize(cp.scal_prod(objectiveFunctions,coefficients))

model.add_solver_callback(TFEcallbacks.PersonalCallback())

print(time.time()-begin)

model.write_information()
solution = model.solve(TimeLimit=60*60*8)

if solution:
    print("Saving/displaying solutions : ...")
    begin = time.time()

    # solution.write()
    pass
    # TFEtimetable.generateAndSaveTimetables(solution, cursusIntervalVariables, teachersIntervalVariables, roomsIntervalVariables, constants, colors.COLORS)
    # TFEtimetable.generateAndSaveTimetables(solution, teachersIntervalVariables, cursusIntervalVariables, roomsIntervalVariables, constants, colors.COLORS)
    # TFEtimetable.generateAndSaveTimetables(solution, roomsIntervalVariables, teachersIntervalVariables, cursusIntervalVariables, constants, colors.COLORS)
    # TFEtimetable.generateAndDisplayTimetable(solution, cursusIntervalVariables, teachersIntervalVariables, roomsIntervalVariables, "BA1_A", constants, colors.COLORS)
    # TFEtimetable.generateAndDisplayTimetable(solution, cursusIntervalVariables, teachersIntervalVariables, roomsIntervalVariables, "BA1_B", constants, colors.COLORS)
    # TFEtimetable.generateAndDisplayTimetable(solution, roomsIntervalVariables, teachersIntervalVariables, cursusIntervalVariables, "Ho.12", constants, colors.COLORS)
    # TFEtimetable.generateAndDisplayTimetable(solution, teachersIntervalVariables, cursusIntervalVariables, roomsIntervalVariables, "Vandaele A", constants, colors.COLORS)

    print(time.time() - begin)
else:
    print("No solution. Conflict refiner")
    conflicts = model.refine_conflict()
    conflicts.write()
