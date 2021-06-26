import docplex.cp.model as cp

def spreadSlots(lecturesDict,exercisesDict,tpsDict,projectsDict,AAset):
    spreadExpression = 0
    for AA in AAset:
        hasLec = AA in lecturesDict
        hasEx = AA in exercisesDict
        hasTP = AA in tpsDict
        hasPr = AA in projectsDict

        spreadMode = hasLec*1 + hasEx*2 + hasTP*4 + hasPr*8
        if spreadMode == 1:
            spreadExpression += cp.square(cp.standard_deviation(
                [cp.start_of(lecturesDict[AA][i+1]) - cp.start_of(lecturesDict[AA][i]) for i in
                 range(len(lecturesDict[AA])-1)]))
        elif spreadMode == 2:
            for exerciceIntervals in exercisesDict[AA]:
                spreadExpression += cp.square(cp.standard_deviation(
                    [cp.start_of(exerciceIntervals[i+1]) - cp.start_of(exerciceIntervals[i]) for i in
                    range(len(exerciceIntervals)-1)]))
        elif spreadMode == 4:
            for tpIntervals in tpsDict[AA]:
                spreadExpression += cp.square(cp.standard_deviation(
                    [cp.start_of(tpIntervals[i+1]) - cp.start_of(tpIntervals[i]) for i in
                     range(len(tpIntervals)-1)]))
        elif spreadMode == 8:
            spreadExpression += cp.square(cp.standard_deviation(
                [cp.start_of(projectsDict[AA][i+1]) - cp.start_of(projectsDict[AA][i]) for i in
                 range(len(projectsDict[AA])-1)]))
        else:
            pass
    return spreadExpression