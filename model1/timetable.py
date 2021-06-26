import numpy as np
import math
import matplotlib.pyplot as plt
import random

def generateTimetables(solution, majorSlots, minorSlots1, minorSlots2, options, colors):
    generateColors = False
    if colors is None:
        colors = {}
    typeLessons = {"lec": "Cours","ex": "Exercices","tp": "TP","pr": "Projet"}
    timetables = {}
    for majorItem,majorIntevals in majorSlots.items():
        timetable = np.full((options["periods"],int(options["days"]*options["weeks"])),"",dtype=object)
        for majorInteval in majorIntevals:
            variableName = majorInteval.get_name()
            value = solution[variableName]
            caracteristics = variableName.split("_")

            if "ch" in variableName:
                displayName = "Charleroi/" + str(int(caracteristics[2])+1) + "\n" + caracteristics[0]
            else:
                displayName = caracteristics[0] + "\n" + typeLessons[caracteristics[1]] + "/" + str(int(caracteristics[2])+1) + "\n"
            breakFlag = False
            found1 = False
            for minorItem1,minorIntervals1 in minorSlots1.items():
                if breakFlag:
                    break
                for minorInterval1 in minorIntervals1:
                    if variableName == minorInterval1.get_name():
                        if found1:
                            displayName += ", ..."
                            breakFlag = True
                            break
                        displayName += minorItem1
                        found1 = True
                        break

            displayName += "\n"
            breakFlag = False
            found2 = False
            for minorItem2,minorIntervals2 in minorSlots2.items():
                if breakFlag:
                    break
                for minorInterval2 in minorIntervals2:
                    if variableName == minorInterval2.get_name():
                        if found2:
                            displayName += ", ..."
                            breakFlag = True
                            break
                        displayName += minorItem2
                        found2 = True
                        break

            if "ch2" in variableName:
                displayName += "2"
            elif "ch4" in variableName:
                displayName += "4"
            base = math.trunc(value[0]/options["periods"])
            rest = value[0]%options["periods"]
            timetable[rest][base] = displayName

            if "Charleroi" not in displayName and caracteristics[0] not in colors:
                generateColors = True
                while True:
                    color = (random.randint(1,254)/255,random.randint(1,254)/255,random.randint(1,254)/255,1)
                    if color not in colors.values():
                        colors[caracteristics[0]] = color
                        break


        timetables[majorItem] = timetable
    if generateColors:
        print(colors)
    return timetables,colors

def saveTimetables(timetables,colors,options):
    for item,timetable in timetables.items():
        m,n = timetable.shape
        k = 1
        for j in range(n):
            day = j%options["days"]
            if day == 0:
                fig, ax = plt.subplots()
                nameFile = item + "_Segment_" + str(k)
                title = item + " : Segment " + str(k)
                ax.set_title(title)
                ax.set_xticks(np.linspace(0, 5, 6))
                ax.set_yticks([0, 1, 1.125, 2.125, 2.625, 3.625, 3.750, 4.750])
                ax.set_xticks(np.linspace(0.5, 4.5, 5), minor="True")
                ax.set_xticklabels([])
                ax.set_yticklabels(["17h45", "15h45", "15h30", "13h30", "12h30", "10h30", "10h15", "8h15"], fontsize=6)
                ax.set_xticklabels(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"], minor=True)
                ax.set_xlim(0, options["days"])
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
                        color = colors[timetables[item][i][j].split("\n")[0]]
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
                fig.savefig("results/"+options["folder"]+"/"+nameFile+".jpg")
                plt.close(fig)

def displayTimetable(timetables,colors,item,options):
    if item in timetables:
        m,n = timetables[item].shape
        k = 1
        for j in range(n):
            day = j%options["days"]
            if day == 0:
                fig, ax = plt.subplots()
                title = item + " : Segment " + str(k)
                ax.set_title(title)
                ax.set_xticks(np.linspace(0,5,6))
                ax.set_yticks([0,1,1.125,2.125,2.625,3.625,3.750,4.750])
                ax.set_xticks(np.linspace(0.5, 4.5, 5),minor="True")
                ax.set_xticklabels([])
                ax.set_yticklabels(["17h45","15h45","15h30","13h30","12h30","10h30","10h15","8h15"],fontsize=6)
                ax.set_xticklabels(["Monday","Tuesday","Wednesday","Thursday","Friday"],minor=True)
                ax.set_xlim(0, options["days"])
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
                        color = colors[timetables[item][i][j].split("\n")[0]]
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
                plt.show()

def generateAndSaveTimetables(solution,majorSlots,minorSlots1,minorSlots2,options,colors):
    timetables,colors = generateTimetables(solution,majorSlots,minorSlots1,minorSlots2,options,colors)
    saveTimetables(timetables,colors,options)

def generateAndDisplayTimetable(solution,majorSlots,minorSlots1,minorSlots2,item,options,colors):
    timetables,colors = generateTimetables(solution,majorSlots,minorSlots1,minorSlots2,options,colors)
    displayTimetable(timetables,colors,item,options)