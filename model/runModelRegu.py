import variables as TFEvariables
import constraints as TFEconstraints
import timetable as TFEtimetable
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
    "segmentSize": 1,
    "roundUp": True,
    "cursus": {
        "BA1": False,
        "BA2": True,
        "BA3_CHIM": False,
        "BA3_ELEC": False,
        "BA3_IG": False,
        "BA3_MECA": False,
        "BA3_MIN": False
    },
    "quadri": "Q1",
    "fileDataset": "datasetBase.xlsx",
    "folderResults": "12SegmentsReguBA1",
    "gap": 16,
    "regularitySize": 6,
    "groupAuto": True
}

lecturesDict,exercisesDict,tpsDict,projectsDict,cursusDict,teachersDict,roomsDict,cursusGroups,AAset = TFEvariables.instantiateVariables(constants)

TFEconstraints.firstOrThirdSlotConstraint(model, tpsDict, constants)
TFEconstraints.firstOrThirdSlotConstraint(model, projectsDict, constants)
TFEconstraints.notOverlappingConstraint(model,cursusDict)
TFEconstraints.notOverlappingConstraint(model,teachersDict)
TFEconstraints.notOverlappingConstraint(model,roomsDict)
TFEconstraints.gapBetweenDuplicatesConstraint(model, exercisesDict, constants)
TFEconstraints.gapBetweenDuplicatesConstraint(model, tpsDict, constants)

TFEconstraints.cursusUnavailabilityConstraint(model, cursusGroups, cursusDict, constants)
TFEconstraints.teachersUnavailabilityConstraint(model, teachersDict, constants)

TFEconstraints.startAndEndConstraint(model, lecturesDict, constants)
TFEconstraints.startAndEndConstraint(model, exercisesDict, constants)
TFEconstraints.startAndEndConstraint(model, tpsDict, constants)
TFEconstraints.startAndEndConstraint(model, projectsDict, constants)

TFEconstraints.regularityConstraint(model, lecturesDict, constants)
TFEconstraints.regularityConstraint(model, exercisesDict, constants)
TFEconstraints.regularityConstraint(model, tpsDict, constants)
TFEconstraints.regularityConstraint(model, projectsDict, constants)
TFEconstraints.breakSymmetryBetweenSpreads(model, lecturesDict, constants)
TFEconstraints.breakSymmetryBetweenSpreads(model, exercisesDict, constants)
TFEconstraints.breakSymmetryBetweenSpreads(model, tpsDict, constants)
TFEconstraints.breakSymmetryBetweenSpreads(model, projectsDict, constants)

print(time.time()-begin)

model.write_information()
solution = model.solve()

if solution:
    print("Saving/displaying solutions : ...")
    begin = time.time()

    # solution.write()
    pass
    # TFEtimetable.generateAndSaveTimetables(solution, cursusDict, teachersDict, roomsDict, constants, colors.COLORS)
    # TFEtimetable.generateAndSaveTimetables(solution, teachersDict, cursusDict, roomsDict, constants, colors.COLORS)
    # TFEtimetable.generateAndSaveTimetables(solution, roomsDict, teachersDict, cursusDict, constants, colors.COLORS)
    # TFEtimetable.generateAndDisplayTimetable(solution, cursusDict, teachersDict, roomsDict, "BA1_A", constants, colors.COLORS)
    # TFEtimetable.generateAndDisplayTimetable(solution, cursusDict, teachersDict, roomsDict, "BA1_B", constants, colors.COLORS)
    # TFEtimetable.generateAndDisplayTimetable(solution, roomsDict, teachersDict, cursusDict, "Ho.12", constants, colors.COLORS)
    # TFEtimetable.generateAndDisplayTimetable(solution, teachersDict, cursusDict, roomsDict, "Vandaele A", constants, colors.COLORS)

    print(time.time() - begin)
else:
    print("No solution. Conflict refiner")
    conflicts = model.refine_conflict()
    conflicts.write()