import variables as TFEvariables
import constraints as TFEconstraints
import timetable as TFEtimetable
import data.colors as colors

import time
import docplex.cp.model as cp

t = time.localtime()
current_time = time.strftime("%H:%M:%S", t)
print("Début de l'exécution : ",current_time)

print("Construction du modèle : ...")
begin = time.time()
model = cp.CpoModel()
options = {
    "weeks":12,
    "days":5,
    "periods":4,
    "blocs": 1,
    "up": True,
    "allowed": ["BA1"],
    "quadri": "Q1",
    "delta": 0,
    "data": "datasetBase.xlsx",
    "folder": "12SegmentsReguBA1",
    "gap": 16,
    "regu": 6,
    "groupAuto": True
}

lecturesDict,exercisesDict,tpsDict,projectsDict,cursusDict,teachersDict,roomsDict,cursusGroups,AAset = TFEvariables.instantiateVariables(options)

TFEconstraints.firstOrThirdSlotConstraint(model,tpsDict,options)
TFEconstraints.firstOrThirdSlotConstraint(model,projectsDict,options)
TFEconstraints.notOverlappingConstraint(model,cursusDict)
TFEconstraints.notOverlappingConstraint(model,teachersDict)
TFEconstraints.notOverlappingConstraint(model,roomsDict)
TFEconstraints.gapBetweenDuplicatesConstraint(model,exercisesDict,options)
TFEconstraints.gapBetweenDuplicatesConstraint(model,tpsDict,options)

TFEconstraints.cursusUnavailabilityConstraint(model,cursusGroups,cursusDict,options)
TFEconstraints.teachersUnavailabilityConstraint(model,teachersDict,options)

TFEconstraints.startAndEndConstraint(model,lecturesDict,options)
TFEconstraints.startAndEndConstraint(model,exercisesDict,options)
TFEconstraints.startAndEndConstraint(model,tpsDict,options)
TFEconstraints.startAndEndConstraint(model,projectsDict,options)

TFEconstraints.regularityConstraint(model,lecturesDict,options)
TFEconstraints.regularityConstraint(model,exercisesDict,options)
TFEconstraints.regularityConstraint(model,tpsDict,options)
TFEconstraints.regularityConstraint(model,projectsDict,options)
TFEconstraints.breakSymmetryBetweenSpreads(model,lecturesDict,options)
TFEconstraints.breakSymmetryBetweenSpreads(model,exercisesDict,options)
TFEconstraints.breakSymmetryBetweenSpreads(model,tpsDict,options)
TFEconstraints.breakSymmetryBetweenSpreads(model,projectsDict,options)

print(time.time()-begin)

model.write_information()
solution = model.solve()

if solution:
    print("Sauvegarde/affichage des solutions : ...")
    begin = time.time()

    # solution.write()
    pass
    # TFEtimetable.generateAndSaveTimetables(solution,cursusDict,teachersDict,roomsDict,options,colors.COLORS)
    # TFEtimetable.generateAndSaveTimetables(solution,teachersDict,cursusDict,roomsDict,options,colors.COLORS)
    # TFEtimetable.generateAndSaveTimetables(solution, roomsDict, teachersDict, cursusDict, options, colors.COLORS)
    # TFEtimetable.generateAndDisplayTimetable(solution, cursusDict, teachersDict, roomsDict, "BA1_A", options,colors.COLORS)
    # TFEtimetable.generateAndDisplayTimetable(solution, cursusDict, teachersDict, roomsDict, "BA1_B", options,colors.COLORS)
    # TFEtimetable.generateAndDisplayTimetable(solution, roomsDict, teachersDict, cursusDict, "Ho.12", options, colors.COLORS)
    # TFEtimetable.generateAndDisplayTimetable(solution, teachersDict, cursusDict, roomsDict, "Vandaele A", options,colors.COLORS)

    print(time.time() - begin)
else:
    print("No solution. Conflict refiner")
    conflicts = model.refine_conflict()
    conflicts.write()