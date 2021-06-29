import variables as TFEvariables
import constraints as TFEconstraints
import timetable as TFEtimetable
import objectives as TFEobjectives
import callbacks as TFEcallbacks
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
    "weeks":6,
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
    "fileDataset": "datasetP1.xlsx",
    "folderResults": "2SegmentsP1",
    "groupAuto": False
}

lecturesDict,exercisesDict,tpsDict,projectsDict,cursusDict,teachersDict,roomsDict,cursusGroups,AAset = TFEvariables.instantiateVariables(constants)

TFEconstraints.cursusUnavailabilityConstraint(model, cursusGroups, cursusDict, constants)
TFEvariables.charleroiFixedVariables(model, teachersDict, roomsDict, constants)

TFEconstraints.firstOrThirdSlotConstraint(model, tpsDict, constants)
TFEconstraints.firstOrThirdSlotConstraint(model, projectsDict, constants)
TFEconstraints.notOverlappingConstraint(model,cursusDict)
TFEconstraints.notOverlappingConstraint(model,teachersDict)
TFEconstraints.notOverlappingConstraint(model,roomsDict)
TFEconstraints.sameWeekDuplicatesConstraint(model, exercisesDict, constants)
TFEconstraints.sameWeekDuplicatesConstraint(model, tpsDict, constants)

TFEconstraints.spreadConstraint(model, lecturesDict, constants)
TFEconstraints.spreadConstraint(model, exercisesDict, constants)
TFEconstraints.spreadConstraint(model, tpsDict, constants)
TFEconstraints.spreadConstraint(model, projectsDict, constants)

TFEconstraints.lecturesBeforeConstraint(model, lecturesDict, [exercisesDict,tpsDict], AAset, constants)

objectiveFunctions = []
coefficients = []
objectiveFunctions.append(TFEobjectives.avoidAfternoonSize1([lecturesDict], [], constants))
coefficients.append(4)
objectiveFunctions.append(TFEobjectives.avoidLastSlotSize1([exercisesDict], ["V-LANG-151","V-LANG-153","V-LANG-155"], constants))
coefficients.append(1)
model.minimize(cp.scal_prod(objectiveFunctions,coefficients))

model.add_solver_callback(TFEcallbacks.CallbackSolutionPrintingStatus())

print(time.time()-begin)

model.write_information()
solution = model.solve(TimeLimit=60*3)

if solution:
    print("Saving/displaying solutions : ...")
    begin = time.time()

    # solution.write()
    pass
    # TFEtimetable.generateAndSaveTimetables(solution, cursusDict, teachersDict, roomsDict, constants, colors.COLORS)
    # TFEtimetable.generateAndSaveTimetables(solution, teachersDict, cursusDict, roomsDict, constants, colors.COLORS)
    # TFEtimetable.generateAndSaveTimetables(solution, roomsDict, teachersDict, cursusDict, constants, colors.COLORS)
    # TFEtimetable.generateAndDisplayTimetable(solution, cursusDict, teachersDict, roomsDict, "BA1_A", constants, colors.COLORS)
    # TFEtimetable.generateAndDisplayTimetable(solution, cursusDict, teachersDict, roomsDict, "BA1_C", constants, colors.COLORS)
    # TFEtimetable.generateAndDisplayTimetable(solution, cursusDict, teachersDict, roomsDict, "BA1_E", constants, colors.COLORS)
    # TFEtimetable.generateAndDisplayTimetable(solution, roomsDict, teachersDict, cursusDict, "Ch.1", constants, colors.COLORS)
    # TFEtimetable.generateAndDisplayTimetable(solution, teachersDict, cursusDict, roomsDict, "Vandaele A", constants, colors.COLORS)

    print(time.time()-begin)
else:
    print("No solution. Conflict refiner")
    conflicts = model.refine_conflict()
    conflicts.write()
