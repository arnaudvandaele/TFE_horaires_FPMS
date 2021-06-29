import pandas as pd
import math

def loadData(fileDataset,quadri,sheet):
    data = pd.read_excel("../data/"+fileDataset, sheet_name=sheet, engine="openpyxl",dtype=object)
    data = data[data["Quadri"]==quadri]
    return data

def loadCursusData(fileDataset):
    data = pd.read_excel("../data/"+fileDataset, sheet_name="Groups",engine="openpyxl",dtype=object)
    cursusData = {}
    for row in data.itertuples():
        cursusData[row.Cursus] = {}
        base = math.trunc(row.Capacity/row.Number)
        rest = row.Capacity%row.Number
        if row.Number > 1:
            for i in range(row.Number):
                cursusData[row.Cursus][row.Cursus+"_"+chr(i+65)] = base + (1 if i < rest else 0)
        else:
            cursusData[row.Cursus][row.Cursus] = base
    return cursusData