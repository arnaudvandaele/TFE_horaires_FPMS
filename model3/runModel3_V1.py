import variables as TFEvariables
import constraints as TFEconstraints
import timetable as TFEtimetable
import callbacks as TFEcallbacks
import data.colors as colors

import time
import docplex.cp.model as cp

t = time.localtime()
current_time = time.strftime("%H:%M:%S", t)
print("Début de l'exécution : ...")
print(current_time)

print("Construction du modèle : ...")
begin = time.time()
model = cp.CpoModel()
options = {
    "weeks":12,
    "days":5,
    "periods":4,
    "blocs":3,
    "up": True,
    "allowed": ["BA3_CHIM","BA3_ELEC","BA3_IG","BA3_MECA","BA3_MIN"],
    "quadri": "Q1",
    "delta": 0,
    "data": "listeCoursM1.xlsx",
    "folder": "M3_V1_ba1_ba3_M",
    "groupAuto": False
}

lecturesDict,exercisesDict,tpsDict,projectsDict,cursusDict,teachersDict,roomsDict,cursusGroups,AAset = TFEvariables.instantiateVariables(options)

TFEconstraints.cursusUnavailabilityConstraint(model,cursusGroups,cursusDict,options)
TFEconstraints.teachersUnavailabilityConstraint(model,teachersDict,options)

TFEconstraints.firstOrThirdSlotConstraint(model,tpsDict,options)
TFEconstraints.firstOrThirdSlotConstraint(model,projectsDict,options)
TFEconstraints.notOverlappingConstraint(model,cursusDict)
TFEconstraints.notOverlappingConstraint(model,teachersDict)
TFEconstraints.notOverlappingConstraint(model,roomsDict)
TFEconstraints.sameWeekDuplicatesConstraint(model,exercisesDict,options)
TFEconstraints.sameWeekDuplicatesConstraint(model,tpsDict,options)

TFEconstraints.spreadConstraint(model,lecturesDict,options)
TFEconstraints.spreadConstraint(model,exercisesDict,options)
TFEconstraints.spreadConstraint(model,tpsDict,options)
TFEconstraints.spreadConstraint(model,projectsDict,options)

model.add_solver_callback(TFEcallbacks.CallbackSolutionPrintingStatus())

print(time.time()-begin)

model.write_information()
solution = model.solve(TimeLimit=60*60*8)

if solution:
    print("Sauvegarde/affichage des solutions : ...")
    begin = time.time()

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

    print(time.time() - begin)
else:
    print("No solution. Conflict refiner")
    conflicts = model.refine_conflict()
    conflicts.write()