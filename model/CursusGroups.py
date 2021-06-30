import data.io as TFEdata
import docplex.cp.model as cp

class CursusGroups:

    def __init__(self, fileDataset):
        self.cursusData = TFEdata.loadCursusData(fileDataset)
        self.knownDivisions = {
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
                "BA3_CHIM": 0,
                "BA3_ELEC_A": 1,
                "BA3_ELEC_B": 1,
                "BA3_IG": 3,
                "BA3_MECA_A": 2,
                "BA3_MECA_B": 0,
                "BA3_MIN": 3
            },
            ("BA3_CHIM", "BA3_ELEC", "BA3_IG", "BA3_MECA_A", "BA3_MECA_B", "BA3_MIN", 4): {
                "BA3_CHIM": 0,
                "BA3_ELEC": 1,
                "BA3_IG": 3,
                "BA3_MECA_A": 2,
                "BA3_MECA_B": 0,
                "BA3_MIN": 3
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

    def getGroups(self, listOfCursus):
        listOfGroups = []
        for cursus in listOfCursus:
            for group in self.cursusData[cursus].keys():
                listOfGroups.append(group)

        return listOfGroups

    def getGroupsWithCapacity(self, listOfCursus):
        listOfGroupsWithCapacity = {}
        for cursus in listOfCursus:
            for group,numberOfStudents in self.cursusData[cursus].items():
                listOfGroupsWithCapacity[group] = numberOfStudents

        return listOfGroupsWithCapacity

    def generateBalancedDivisions(self, listOfCursus, numberDivisions, isGroupAuto):
        listOfGroupsWithCapacity = self.getGroupsWithCapacity(listOfCursus)
        cursusGroupsKey = self.getGroups(listOfCursus)
        cursusGroupsKey.append(numberDivisions)
        if isGroupAuto is False and tuple(cursusGroupsKey) in self.knownDivisions:
            return self.knownDivisions[tuple(cursusGroupsKey)]

        if numberDivisions != 1:
            expectedMean = 0
            divisions = [0 for d in range(numberDivisions)]
            for group,numberOfStudents in listOfGroupsWithCapacity.items():
                expectedMean += numberOfStudents
                groupVariable = cp.integer_var(min=0,max=numberDivisions-1,name=group)
                for d in range(numberDivisions):
                    divisions[d] += (groupVariable == d)*numberOfStudents
            expectedMean /= numberDivisions

            subModel = cp.CpoModel()
            subModel.add(cp.minimize(cp.sum(cp.abs(div-expectedMean) for div in divisions)))
            solution = subModel.solve(LogVerbosity='Quiet')
            return {s.get_name(): s.get_value() for s in solution.get_all_var_solutions()}
        else:
            return {k: 0 for k in listOfGroupsWithCapacity.keys()}
