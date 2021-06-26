import numpy as np
import math
import matplotlib.pyplot as plt


def generateTimetables(solution,numberPeriods,numberDays,numberWeeks,cursusSlots,teacherSlots,roomSlots):
    typeLessons = {"lec": "Cours","ex": "Exercices","tp": "TP","pr": "Projet"}
    cursusTimetables = {}
    for cursus,cursusIntervals in cursusSlots.items():
        timetable = np.full((numberPeriods,numberDays*numberWeeks),"",dtype=object)
        for intervalC in cursusIntervals:
            variableName = intervalC.get_name()
            value = solution[variableName]
            caracteristics = variableName.split("_")

            displayName = caracteristics[0] + "\n" + typeLessons[caracteristics[1]] + "/" + caracteristics[2] + "\n"
            breakFlag = False
            foundT = False
            for teacher,teacherIntervals in teacherSlots.items():
                if breakFlag:
                    break
                for intervalT in teacherIntervals:
                    if variableName == intervalT.get_name():
                        if foundT:
                            displayName += ", ..."
                            breakFlag = True
                            break
                        displayName += teacher
                        foundT = True
                        break

            displayName += "\n"
            foundR = False
            breakFlag = False
            for room, roomIntervals in roomSlots.items():
                if breakFlag:
                    break
                for intervalR in roomIntervals:
                    if variableName == intervalR.get_name():
                        if foundR:
                            displayName += ", ..."
                            breakFlag = True
                            break
                        displayName += room
                        foundR = True
                        break

            base = math.trunc(value[0]/numberPeriods)
            rest = value[0]%numberPeriods
            timetable[rest][base] = displayName
            if value[2] == 2:
                timetable[rest+1][base] = displayName

        cursusTimetables[cursus] = timetable
    return cursusTimetables

def saveTimetables(cursusTimetables):
    for cursus,timetable in cursusTimetables.items():
        m,n = timetable.shape
        for j in range(n):
            day = j%5
            if day == 0:
                fig, ax = plt.subplots()
                nameFile = cursus + "_Week_" + str(math.trunc(j / 5) + 1)
                ax.set_title(nameFile)
                ax.set_xlim(0, 5)
                ax.set_ylim(0, 4)
                ax.set_xticks(np.linspace(0, 5, 6))
                ax.set_yticks(np.linspace(0, 4, 5))
                ax.set_xticks(np.linspace(0.5, 4.5, 5), minor="True")
                ax.set_yticks(np.linspace(0.5, 3.5, 4), minor="True")
                ax.set_xticklabels([])
                ax.set_yticklabels([])
                ax.set_xticklabels(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"], minor=True)
                ax.set_yticklabels(["15h45\n17h45", "13h30\n15h30", "10h30\n12h30", "8h15\n10h15"], minor=True,fontsize=6)
                ax.grid()
            for i in range(m):
                if timetable[i][j] != "":
                    ax.fill_between([day,day+1],3-i,4-i,color='green')
                    ax.text(day+0.5,3.5-i,timetable[i][j],fontsize=6,horizontalalignment='center',verticalalignment='center')
            if day == 4:
                fig.savefig("results/"+nameFile+".jpg")
                plt.close(fig)

def displayTimetable(cursusTimetables,cursus):
    if cursus in cursusTimetables:
        m,n = cursusTimetables[cursus].shape
        for j in range(n):
            day = j%5
            if day == 0:
                fig, ax = plt.subplots()
                nameFile = cursus+"_Week_"+str(math.trunc(j/5)+1)
                ax.set_title(nameFile)
                ax.set_xlim(0,5)
                ax.set_ylim(0,4)
                ax.set_xticks(np.linspace(0,5,6))
                ax.set_yticks(np.linspace(0,4,5))
                ax.set_xticks(np.linspace(0.5, 4.5, 5),minor="True")
                ax.set_yticks(np.linspace(0.5, 3.5, 4),minor="True")
                ax.set_xticklabels([])
                ax.set_yticklabels([])
                ax.set_xticklabels(["Monday","Tuesday","Wednesday","Thursday","Friday"],minor=True)
                ax.set_yticklabels(["15h45\n17h45","13h30\n15h30","10h30\n12h30","8h15\n10h15"],minor=True,fontsize=6)
                ax.grid()
            for i in range(m):
                if cursusTimetables[cursus][i][j] != "":
                    ax.fill_between([day,day+1],3-i,4-i,color='green')
                    ax.text(day+0.5,3.5-i,cursusTimetables[cursus][i][j],fontsize=6,horizontalalignment='center',verticalalignment='center')
            if day == 4:
                plt.show()

def generateAndSaveTimetables(solution,numberPeriods,numberDays,numberWeeks,cursusSlots,teacherSlots,roomSlots):
    cursusTimetables = generateTimetables(solution,numberPeriods,numberDays,numberWeeks,cursusSlots,teacherSlots,roomSlots)
    saveTimetables(cursusTimetables)

def generateAndDisplayTimetable(solution,numberPeriods,numberDays,numberWeeks,cursusSlots,teacherSlots,roomSlots,cursus):
    cursusTimetables = generateTimetables(solution,numberPeriods,numberDays,numberWeeks,cursusSlots,teacherSlots,roomSlots)
    displayTimetable(cursusTimetables,cursus)