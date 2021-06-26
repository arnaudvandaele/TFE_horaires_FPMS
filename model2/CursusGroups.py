from data.io import *
import docplex.cp.model as cp

class CursusGroups:

    def __init__(self,options):
        self.cursusData = loadCursusData(options)

    def getGroups(self,cursusList):
        cursusGroups = []
        for c in cursusList:
            for k in self.cursusData[c].keys():
                cursusGroups.append(k)

        return cursusGroups

    def getGroupsWithCapacity(self,cursusList):
        cursusGroups = {}
        for c in cursusList:
            for k,v in self.cursusData[c].items():
                cursusGroups[k] = v

        return cursusGroups

    def generateBalancedGroups(self,cursusList,numberDivisions):
        cursusGroups = self.getGroupsWithCapacity(cursusList)

        if numberDivisions != 1:
            threshold = 0
            for v in cursusGroups.values():
                threshold += v
            threshold /= numberDivisions

            model = cp.CpoModel()
            divisions = [0 for i in range(numberDivisions)]
            for k,v in cursusGroups.items():
                group = cp.integer_var(min=0,max=numberDivisions-1,name=k)
                for i in range(numberDivisions):
                    divisions[i] += (group == i)*v

            model.add(cp.minimize(cp.sum(cp.abs(div-threshold) for div in divisions)))

            return {s.get_name(): s.get_value() for s in model.solve(LogVerbosity='Quiet').get_all_var_solutions()}
        else:
            return {k: 0 for k in cursusGroups.keys()}
