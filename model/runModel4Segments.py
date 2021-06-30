import variables as TFEvariables
import constraints as TFEconstraints
import timetable as TFEtimetable
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
    "weeks":12,
    "days":5,
    "slots":4,
    "segmentSize":3,
    "roundUp": True,
    "cursus": {
        "BA1": True,
        "BA2": False,
        "BA3_CHIM": False,
        "BA3_ELEC": False,
        "BA3_IG": False,
        "BA3_MECA": False,
        "BA3_MIN": False
    },
    "quadri": "Q1",
    "fileDataset": "datasetAnglais.xlsx", #dataset-Base/Anglais/AnglaisLocaux
    "folderResults": "4SegmentsStrategies",
    "groupAuto": False
}

lecturesDict, exercisesDict, tpsDict, projectsDict, \
cursusIntervalVariables, teachersIntervalVariables, roomsIntervalVariables, \
cursusGroups, AAset = TFEvariables.generateIntervalVariables(constants)

TFEconstraints.cursusUnavailabilityConstraint(model, cursusGroups, cursusIntervalVariables, constants)
TFEconstraints.teachersUnavailabilityConstraint(model, teachersIntervalVariables, constants)

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