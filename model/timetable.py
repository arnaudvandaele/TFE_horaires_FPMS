import numpy as np
import math
import matplotlib.pyplot as plt
import random

def generateTimetables(solution, majorData, minorData1, minorData2, constants, colorsDict):
    hasGeneratedColors = False
    if colorsDict is None:
        colorsDict = {}

    fullNameOfLessons = {"lec": "Cours","ex": "Exercices","tp": "TP","pr": "Projet"}
    timetables = {}
    for majorID,majorIntervalVariables in majorData.items():
        timetable = np.full((constants["slots"], int(constants["days"] * constants["weeks"] / constants["segmentSize"])), "", dtype=object)
        for majorIntervalVariable in majorIntervalVariables:
            variableName = majorIntervalVariable.get_name()
            valuesOfInterval = solution[variableName]
            caracteristicsOfVariable = variableName.split("_")

            if "ch" in variableName:
                displayName = "Charleroi/" + str(int(caracteristicsOfVariable[2])+1) + "\n" + caracteristicsOfVariable[0] + "\n"
            else:
                displayName = caracteristicsOfVariable[0] + "\n" + fullNameOfLessons[caracteristicsOfVariable[1]] + "/" + str(int(caracteristicsOfVariable[2])+1) + "\n"
            breakFlag = False
            found = False
            for minorID1,minorIntervalVariables1 in minorData1.items():
                if breakFlag:
                    break
                for minorIntervalVariable1 in minorIntervalVariables1:
                    if variableName == minorIntervalVariable1.get_name():
                        if found:
                            displayName += ", ..."
                            breakFlag = True
                            break
                        displayName += minorID1
                        found = True
                        break
            displayName += "\n"
            breakFlag = False
            found = False
            for minorID2,minorIntervalVariables2 in minorData2.items():
                if breakFlag:
                    break
                for minorIntervalVariable2 in minorIntervalVariables2:
                    if variableName == minorIntervalVariable2.get_name():
                        if found:
                            displayName += ", ..."
                            breakFlag = True
                            break
                        displayName += minorID2
                        found = True
                        break
            if "ch2" in variableName:
                displayName += "2"
            elif "ch4" in variableName:
                displayName += "4"

            #TODO reprendre ici
            base = math.trunc(valuesOfInterval[0] / constants["slots"])
            rest = valuesOfInterval[0] % constants["slots"]
            timetable[rest][base] = displayName

            if "Charleroi" not in displayName and caracteristicsOfVariable[0] not in colorsDict:
                hasGeneratedColors = True
                while True:
                    color = (random.randint(1,254)/255,random.randint(1,254)/255,random.randint(1,254)/255,1)
                    if color not in colorsDict.values():
                        colorsDict[caracteristicsOfVariable[0]] = color
                        break


        timetables[majorID] = timetable
    if hasGeneratedColors:
        print(colorsDict)
    return timetables, colorsDict

def saveTimetables(timetables, colorsDict, constants):
    for item,timetable in timetables.items():
        m,n = timetable.shape
        k = 1
        for j in range(n):
            day = j % constants["days"]
            if day == 0:
                fig, ax = plt.subplots()
                title = item + " : Segment " + str(k)
                nameFile = item + "_Segment_" + str(k)
                ax.set_title(title)
                ax.set_xticks(np.linspace(0, 5, 6))
                ax.set_yticks([0, 1, 1.125, 2.125, 2.625, 3.625, 3.750, 4.750])
                ax.set_xticks(np.linspace(0.5, 4.5, 5), minor="True")
                ax.set_xticklabels([])
                ax.set_yticklabels(["17h45", "15h45", "15h30", "13h30", "12h30", "10h30", "10h15", "8h15"], fontsize=6)
                ax.set_xticklabels(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"], minor=True)
                ax.set_xlim(0, constants["days"])
                ax.set_ylim(0, 4.750)
                ax.grid()
                ax.set_axisbelow(True)
                k += 1
            for i in range(m):
                if timetables[item][i][j] != "":
                    if "Charleroi" in timetables[item][i][j]:
                        color = (0,0,0,1)
                        colorText = 'white'
                        if timetables[item][i][j][-1] == "2":
                            if i == 0:
                                center = 3.625
                                ax.fill_between([day, day + 1], 2.625, 4.625, color=color)
                            elif i == 2:
                                center = 1.125
                                ax.fill_between([day, day + 1], 0.125, 2.125, color=color)
                            else:
                                continue
                        elif timetables[item][i][j][-1] == "4":
                            ax.fill_between([day, day + 1], 0, 4.75, color=color)
                            center = 2.375
                        else:
                            continue
                        ax.text(day + 0.5, center, timetables[item][i][j][:-1], fontsize=6, horizontalalignment='center',
                                verticalalignment='center', color=colorText)
                    else:
                        color = colorsDict[timetables[item][i][j].split("\n")[0]]
                        colorText = 'black' if (color[0] * 255 * 0.299 + color[1] * 255 * 0.587 + color[
                            2] * 255 * 0.114) > 150 else 'white'
                        center = 0
                        if "TP/" in timetables[item][i][j] or "Projet/" in timetables[item][i][j]:
                            if i == 0:
                                ax.fill_between([day, day + 1], 2.625, 4.625, color=color)
                                center = 3.625
                            elif i == 2:
                                ax.fill_between([day, day + 1], 0.125, 2.125, color=color)
                                center = 1.125
                            else:
                                continue
                            ax.text(day + 0.5, center, timetables[item][i][j], fontsize=6, horizontalalignment='center',
                                    verticalalignment='center',color=colorText)
                        else:
                            if i == 0:
                                ax.fill_between([day, day + 1], 3.750, 4.750, color=color)
                                center = 4.25
                            elif i == 1:
                                ax.fill_between([day, day + 1], 2.625, 3.625, color=color)
                                center = 3.125
                            elif i == 2:
                                ax.fill_between([day, day + 1], 1.125, 2.125, color=color)
                                center = 1.625
                            elif i == 3:
                                ax.fill_between([day, day + 1], 0, 1, color=color)
                                center = 0.5
                            ax.text(day + 0.5, center, timetables[item][i][j], fontsize=6, horizontalalignment='center',
                                    verticalalignment='center',color=colorText)
            if day == 4:
                fig.savefig("results/" + constants["folderResults"] + "/" + nameFile + ".jpg")
                plt.close(fig)

def displayTimetable(timetables, colorsDict, ID, constants):
    if ID in timetables:
        m,n = timetables[ID].shape
        k = 1
        for j in range(n):
            day = j % constants["days"]
            if day == 0:
                fig, ax = plt.subplots()
                title = ID + " : Segment " + str(k)
                ax.set_title(title)
                ax.set_xticks(np.linspace(0,5,6))
                ax.set_yticks([0,1,1.125,2.125,2.625,3.625,3.750,4.750])
                ax.set_xticks(np.linspace(0.5, 4.5, 5),minor="True")
                ax.set_xticklabels([])
                ax.set_yticklabels(["17h45","15h45","15h30","13h30","12h30","10h30","10h15","8h15"],fontsize=6)
                ax.set_xticklabels(["Monday","Tuesday","Wednesday","Thursday","Friday"],minor=True)
                ax.set_xlim(0, constants["days"])
                ax.set_ylim(0, 4.750)
                ax.grid()
                ax.set_axisbelow(True)
                k += 1
            for i in range(m):
                if timetables[ID][i][j] != "":
                    if "Charleroi" in timetables[ID][i][j]:
                        color = (0,0,0,1)
                        colorText = 'white'
                        if timetables[ID][i][j][-1] == "2":
                            if i == 0:
                                center = 3.625
                                ax.fill_between([day, day + 1], 2.625, 4.625, color=color)
                            elif i == 2:
                                center = 1.125
                                ax.fill_between([day, day + 1], 0.125, 2.125, color=color)
                            else:
                                continue
                        elif timetables[ID][i][j][-1] == "4":
                            ax.fill_between([day, day + 1], 0, 4.75, color=color)
                            center = 2.375
                        else:
                            continue
                        ax.text(day + 0.5, center, timetables[ID][i][j][:-1], fontsize=6, horizontalalignment='center',
                                verticalalignment='center', color=colorText)
                    else:
                        color = colorsDict[timetables[ID][i][j].split("\n")[0]]
                        colorText = 'black' if (color[0] * 255 * 0.299 + color[1] * 255 * 0.587 + color[
                            2] * 255 * 0.114) > 150 else 'white'
                        center = 0
                        if "TP/" in timetables[ID][i][j] or "Projet/" in timetables[ID][i][j]:
                            if i == 0:
                                ax.fill_between([day, day + 1], 2.625, 4.625, color=color)
                                center = 3.625
                            elif i == 2:
                                ax.fill_between([day, day + 1], 0.125, 2.125, color=color)
                                center = 1.125
                            else:
                                continue
                            ax.text(day + 0.5, center, timetables[ID][i][j], fontsize=6, horizontalalignment='center',
                                    verticalalignment='center', color=colorText)
                        else:
                            if i == 0:
                                ax.fill_between([day, day + 1], 3.750, 4.750, color=color)
                                center = 4.25
                            elif i == 1:
                                ax.fill_between([day, day + 1], 2.625, 3.625, color=color)
                                center = 3.125
                            elif i == 2:
                                ax.fill_between([day, day + 1], 1.125, 2.125, color=color)
                                center = 1.625
                            elif i == 3:
                                ax.fill_between([day, day + 1], 0, 1, color=color)
                                center = 0.5
                            ax.text(day + 0.5, center, timetables[ID][i][j], fontsize=6, horizontalalignment='center',
                                    verticalalignment='center', color=colorText)
            if day == 4:
                plt.show()

def generateAndSaveTimetables(solution, majorData, minorData1, minorData2, constants, colorsDict):
    timetables, colorsDict = generateTimetables(solution, majorData, minorData1, minorData2, constants, colorsDict)
    saveTimetables(timetables, colorsDict, constants)

def generateAndDisplayTimetable(solution, majorData, minorData1, minorData2, ID, constants, colorsDict):
    timetables, colorsDict = generateTimetables(solution, majorData, minorData1, minorData2, constants, colorsDict)
    displayTimetable(timetables, colorsDict, ID, constants)