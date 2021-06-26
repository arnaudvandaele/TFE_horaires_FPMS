import data.io as TFEdata
import docplex.cp.model as cp

class CursusGroups:

    def __init__(self,options):
        self.cursusData = TFEdata.loadCursusData(options)
        self.knownGroups = {
            ("BA1_A", "BA1_B", "BA1_C", "BA1_D", "BA1_E", "BA1_F", "BA1_G", "BA1_H", 8): {
                "BA1_A": 0,
                "BA1_B": 1,
                "BA1_C": 2,
                "BA1_D": 3,
                "BA1_E": 4,
                "BA1_F": 5,
                "BA1_G": 6,
                "BA1_H": 7,
            },
            ("BA1_A","BA1_B","BA1_C","BA1_D","BA1_E","BA1_F","BA1_G","BA1_H",4): {
                "BA1_A": 0,
                "BA1_B": 0,
                "BA1_C": 1,
                "BA1_D": 1,
                "BA1_E": 2,
                "BA1_F": 2,
                "BA1_G": 3,
                "BA1_H": 3,
            },
            ("BA1_A", "BA1_B", "BA1_C", "BA1_D", "BA1_E", "BA1_F", "BA1_G", "BA1_H",2): {
                "BA1_A": 0,
                "BA1_B": 0,
                "BA1_C": 0,
                "BA1_D": 0,
                "BA1_E": 1,
                "BA1_F": 1,
                "BA1_G": 1,
                "BA1_H": 1,
            },
            ("BA2_A", "BA2_B", "BA2_C", "BA2_D", 4): {
                "BA2_A": 0,
                "BA2_B": 1,
                "BA2_C": 2,
                "BA2_D": 3
            },
            ("BA2_A", "BA2_B", "BA2_C", "BA2_D", 2): {
                "BA2_A": 0,
                "BA2_B": 0,
                "BA2_C": 1,
                "BA2_D": 1
            },
            ("BA3_ELEC_A","BA3_ELEC_B",2): {
                "BA3_ELEC_A": 0,
                "BA3_ELEC_B": 1
            },
            ("BA3_MECA_A", "BA3_MECA_B", 2): {
                "BA3_MECA_A": 0,
                "BA3_MECA_B": 1
            },
            ("BA3_CHIM", "BA3_ELEC_A", "BA3_ELEC_B", "BA3_IG", "BA3_MECA_A","BA3_MECA_B","BA3_MIN", 4): {
                "BA3_CHIM": 3,
                "BA3_ELEC_A": 1,
                "BA3_ELEC_B": 1,
                "BA3_IG": 3,
                "BA3_MECA_A": 2,
                "BA3_MECA_B": 0,
                "BA3_MIN": 0
            },
            ("BA3_CHIM", "BA3_ELEC", "BA3_IG", "BA3_MECA_A", "BA3_MECA_B", "BA3_MIN", 4): {
                "BA3_CHIM": 3,
                "BA3_ELEC": 1,
                "BA3_IG": 3,
                "BA3_MECA_A": 2,
                "BA3_MECA_B": 0,
                "BA3_MIN": 0
            },
            ("BA3_CHIM", "BA3_MIN", 2): {
                "BA3_CHIM": 0,
                "BA3_MIN": 1
            },
            ("BA3_ELEC_A","BA3_ELEC_B","BA3_MECA_A", "BA3_MECA_B", 2): {
                "BA3_ELEC_A": 0,
                "BA3_ELEC_B": 0,
                "BA3_MECA_A": 1,
                "BA3_MECA_B": 1
            },
            ("BA3_ELEC","BA3_MECA_A", "BA3_MECA_B", 2): {
                "BA3_ELEC": 0,
                "BA3_MECA_A": 1,
                "BA3_MECA_B": 1
            }
        }

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

    def generateBalancedGroups(self,cursusList,numberDivisions,options):
        cursusGroups = self.getGroupsWithCapacity(cursusList)
        cursusGroupsCheck = self.getGroups(cursusList)
        cursusGroupsCheck.append(numberDivisions)
        if tuple(cursusGroupsCheck) in self.knownGroups and options["groupAuto"] is False:
            return self.knownGroups[tuple(cursusGroupsCheck)]

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
            solution = model.solve(LogVerbosity='Quiet')
            balancedGroups = {s.get_name(): s.get_value() for s in solution.get_all_var_solutions()}
            print("!!!!!! Warning !!!!!!")
            print("Unknown groups have been encountered. Please register them and/or review the response")
            print(balancedGroups)
            return balancedGroups
        else:
            return {k: 0 for k in cursusGroups.keys()}
