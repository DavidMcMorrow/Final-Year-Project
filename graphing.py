from xml.dom import minidom
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

def creatingFiles(SCENARIO, useCases, LEVELOFSERVICE, vehicleTypes):
    safetyFiles = []
    effiencyFiles = []
    
    for case in useCases:
        if case == "\BaselineHDV":
            vehicleTypes = ["HDV"]
        elif case == "\BaselineCAV":
            vehicleTypes = ["L4-CV"]
        for los in LEVELOFSERVICE:
            for types in vehicleTypes:
                for i in range(0, NUMBEROFITERATIONS):
                    safetyFilepath = SCENARIO + case + "\Output-Files\LOS-" + los + "\SSM-" + types + "-" + str(i+1) + ".xml"
                    effiencyFilepath = SCENARIO + case + "\Output-Files\LOS-" + los + "\Trips-" + str(i+1) + ".xml"
                    safetyFiles.append(safetyFilepath)
                    effiencyFiles.append(effiencyFilepath)
    return safetyFiles, effiencyFiles

def gatheringTheData(safetyFiles, effiencyFiles):
    tempTTC = []
    tempTHROUGHPUT = []
    tempEMISSIONS = []
    TTC = []
    THROUGHPUT = []
    EMISSIONS = []
    for i in range(0, len(safetyFiles)):
        tempTTC.append(safetyKPIs(safetyFiles[i]))
        throughputTemp, emissionsTemp = effiencyKPIs(effiencyFiles[i])
        tempTHROUGHPUT.append(throughputTemp)
        tempEMISSIONS.append(emissionsTemp)
        if i % NUMBEROFITERATIONS == 2:
            print("Finished LOS ")
            TTC.append(np.mean(tempTTC))
            THROUGHPUT.append(np.mean(tempTHROUGHPUT))
            EMISSIONS.append(np.mean(tempEMISSIONS))
            tempTTC = [] 
            tempTHROUGHPUT = [] 
            tempEMISSIONS = []
    return TTC, THROUGHPUT, EMISSIONS

def safetyKPIs(filename):
    safetyIncidents = []
    document = minidom.parse(filename)
    return len(document.getElementsByTagName('conflict'))

def effiencyKPIs(filename):
    throughput = []
    CO2 = []
    allEmissionsForLOS = []
    document = minidom.parse(filename)
    trips = document.getElementsByTagName('tripinfo')
    emissions = document.getElementsByTagName('emissions')
    count = 0
    emissionsPerRun = []
    for i in range(0, len(trips)):
        if(float(trips[i].getAttribute("arrival") ) < 3600):
            count = count + 1
            emissionsPerRun.append(float(emissions[i].getAttribute("CO2_abs")))
    
    return count, np.mean(emissionsPerRun)

def intialiseAxisAndTitle(j):
    if(j == 0):
        array = TTC
        yAxis = "Number of Safety Incidents"
        title = "Safety"
    elif (j==1):
        array = THROUGHPUT
        yAxis = "Throughput of network"
        title = "Throughput"
    elif (j==2):
        array = EMISSIONS
        yAxis = "CO2"
        title = "Environmental"
    return array, yAxis, title

def graphingKPIs(TTC, THROUGHPUT, EMISSIONS, vehicleTypes):
    xAxis = "Level of Service"
    array = []
    for j in range(0, 3):
        count = 0
        hdvArray = []
        l4CVArray = []
        
        array, yAxis, title = intialiseAxisAndTitle(j)

        for i in range(0, len(array)):
            if(i == len(vehicleTypes)):
                count = count + 1
            
            if vehicleTypes[count] == "HDV":
                hdvArray.append(array[i])
                
            elif vehicleTypes[count] == "L4-CV":
                l4CVArray.append(array[i])
        
        plotdata = pd.DataFrame(
            {
                "HDV": hdvArray,
                "L4-CV": l4CVArray,       
            }, 
            index=["A", "B"]
        )
        plotdata.plot(kind='bar')
        plt.xlabel(xAxis)
        plt.ylabel(yAxis)
        plt.title(title)
        plt.show()


def graphingFunction(xLabel, yLabel, title, xData, yData):
    plt.bar(xData, yData, align='center', alpha=0.5)
    plt.xlabel(xLabel)
    plt.ylabel(yLabel)
    plt.title(title)
    plt.show()

TTC = []
THROUGHPUT = []
EMISSIONS = []

NUMBEROFITERATIONS = 3

SCENARIO = "Roadworks"
# SCENARIO = "Collision"

useCases = ["\BaselineHDV", "\BaselineCAV"]
# LEVELOFSERVICE = ["A", "B", "C", "D"]
LEVELOFSERVICE = ["A", "B"]
vehicleTypes = ["HDV", "L4-CV"]

safetyFiles, effiencyFiles = creatingFiles(SCENARIO, useCases, LEVELOFSERVICE, vehicleTypes)


TTC, THROUGHPUT, EMISSIONS = gatheringTheData(safetyFiles, effiencyFiles)
    
print("TTC", TTC)
print("Throughput", THROUGHPUT)
print("CO2", EMISSIONS)

graphingKPIs(TTC, THROUGHPUT, EMISSIONS, vehicleTypes)

