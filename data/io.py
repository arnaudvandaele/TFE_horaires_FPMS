import pandas as pd
import math

def loadData(fileDataset,quadri,sheet):
    dataset = pd.read_excel("../data/"+fileDataset, sheet_name=sheet, engine="openpyxl",dtype=object)
    dataset = dataset[dataset["quadri"]==quadri]
    return dataset

def loadCursusData(fileDataset):
    datasetCursus = pd.read_excel("../data/"+fileDataset, sheet_name="Groups",engine="openpyxl",dtype=object)
    cursusData = {}
    for rowCursus in datasetCursus.itertuples():
        cursusData[rowCursus.cursus] = {}
        baseNumberOfStudents = math.trunc(rowCursus.totalStudents/rowCursus.numberGroups)
        restNumberOfStudents = rowCursus.totalStudents%rowCursus.numberGroups
        if rowCursus.numberGroups > 1:
            for i in range(rowCursus.numberGroups):
                cursusData[rowCursus.cursus][rowCursus.cursus+"_"+chr(i+65)] = baseNumberOfStudents + (1 if i < restNumberOfStudents else 0)
        else:
            cursusData[rowCursus.cursus][rowCursus.cursus] = baseNumberOfStudents
    return cursusData