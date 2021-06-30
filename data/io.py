import pandas as pd
import math

def loadData(fileDataset,quadri,sheet):
    data = pd.read_excel("../data/"+fileDataset, sheet_name=sheet, engine="openpyxl",dtype=object)
    data = data[data["quadri"]==quadri]
    return data

def loadCursusData(fileDataset):
    data = pd.read_excel("../data/"+fileDataset, sheet_name="Groups",engine="openpyxl",dtype=object)
    cursusData = {}
    for row in data.itertuples():
        cursusData[row.cursus] = {}
        base = math.trunc(row.capacity/row.number)
        rest = row.capacity%row.number
        if row.number > 1:
            for i in range(row.number):
                cursusData[row.cursus][row.cursus+"_"+chr(i+65)] = base + (1 if i < rest else 0)
        else:
            cursusData[row.cursus][row.cursus] = base
    return cursusData