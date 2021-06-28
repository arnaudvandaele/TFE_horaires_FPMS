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
    "bloc": 6,
    "allowed": ["BA1"],
    "quadri": "Q1",
    "data": "listeCoursM1.xlsx",
    "folder": "M1_V2_ba1",
    "gap": 16
}

lecturesDict,exercisesDict,tpsDict,projectsDict,cursusDict,teachersDict,roomsDict,AAset,cursusGroups = TFEvariables.instantiateVariables(options)

TFEconstraints.firstOrThirdSlotConstraint(model,tpsDict,options)
TFEconstraints.firstOrThirdSlotConstraint(model,projectsDict,options)
TFEconstraints.notOverlappingConstraint(model,cursusDict)
TFEconstraints.notOverlappingConstraint(model,teachersDict)
TFEconstraints.notOverlappingConstraint(model,roomsDict)
TFEconstraints.gapBetweenDuplicatesConstraint(model,exercisesDict,options)
TFEconstraints.gapBetweenDuplicatesConstraint(model,tpsDict,options)

TFEconstraints.cursusUnavailabilityConstraint(model,cursusGroups,cursusDict,options)
TFEconstraints.teachersUnavailabilityConstraint(model,teachersDict,options)

TFEconstraints.startAndEndConstraint(model,lecturesDict)
TFEconstraints.startAndEndConstraint(model,exercisesDict)
TFEconstraints.startAndEndConstraint(model,tpsDict)
TFEconstraints.startAndEndConstraint(model,projectsDict)

TFEconstraints.spreadConstraint(model,lecturesDict,options)
TFEconstraints.spreadConstraint(model,exercisesDict,options)
TFEconstraints.spreadConstraint(model,tpsDict,options)
TFEconstraints.spreadConstraint(model,projectsDict,options)
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
    TFEtimetable.generateAndSaveTimetables(solution,cursusDict,teachersDict,roomsDict,options,colors.COLORS)
    TFEtimetable.generateAndSaveTimetables(solution,teachersDict,cursusDict,roomsDict,options,colors.COLORS)
    TFEtimetable.generateAndSaveTimetables(solution, roomsDict, teachersDict, cursusDict, options, colors.COLORS)
    # TFEtimetable.generateAndDisplayTimetable(solution, cursusDict, teachersDict, roomsDict, "BA1_A", options,colors.COLORS)
    # TFEtimetable.generateAndDisplayTimetable(solution, cursusDict, teachersDict, roomsDict, "BA1_B", options,colors.COLORS)
    # TFEtimetable.generateAndDisplayTimetable(solution, roomsDict, teachersDict, cursusDict, "Ho.12", options, colors.COLORS)
    # TFEtimetable.generateAndDisplayTimetable(solution, teachersDict, cursusDict, roomsDict, "Vandaele A", options,colors.COLORS)

    print(time.time() - begin)
else:
    print("No solution. Conflict refiner")
    conflicts = model.refine_conflict()
    conflicts.write()