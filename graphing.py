from xml.dom import minidom
import matplotlib
import matplotlib.pyplot as plt
import numpy as np

def creatingFiles(SCENARIO, useCases, LEVELOFSERVICE, vehicleTypes):
    safetyFiles = []
    effiencyFiles = []
    
    for case in useCases:
        for los in LEVELOFSERVICE:
            for types in vehicleTypes:
                for i in range(0, NUMBEROFITERATIONS):
                    safetyFilepath = SCENARIO + case + "\Output-Files\LOS-" + los + "\SSM-" + types + "-" + str(i+1) + ".xml"
                    effiencyFilepath = SCENARIO + case + "\Output-Files\LOS-" + los + "\Trips-" + types + "-" + str(i+1) + ".xml"
                    safetyFiles.append(safetyFilepath)
                    effiencyFiles.append(effiencyFilepath)
    return safetyFiles, effiencyFiles

def safetyKPIs(filename):
    safetyIncidents = []
    filename = "Roadworks\BaselineHDV\Output-Files\LOS-" + str(los) + "\SSM-HDV-" + str(iteration+1) + ".xml"
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
    
    return throughput, np.mean(emissionsPerRun)

# def graphingKPIs(TTC, THROUGHPUT, EMISSIONS, LEVELOFSERVICE):
#     yAxisSafety = "Number of Incidents"
#     yAxisCO2 = "Number of CO2"
#     yAxisThroughPut = "ThroughPut of network"
#     count = 0
#     for los in LEVELOFSERVICE:
#         titleSafety = "LOS-" + los + ": TTC"
#         titleCO2 = "LOS-" + los + ": Total CO2 Output"
#         titleThroughput = "LOS-" + los + ": Throughput"
#         xAxis = "LOS"
#         graphingFunction(xAxis, yAxisSafety, titleSafety, los, TTC[count])
#         graphingFunction(xAxis, yAxisCO2, titleThroughput, los, THROUGHPUT[count])
#         graphingFunction(xAxis, yAxisThroughPut, titleCO2, los, EMISSIONS[count])
#         count = count + 1

def graphingKPIs(TTC, THROUGHPUT, EMISSIONS):
    yAxisSafety = "Number of Incidents"
    yAxisCO2 = "Number of CO2"
    yAxisThroughPut = "ThroughPut of network"
    count = 0
    # for i in range(0, len(TTC)):
        
        
def graphingFunction(xLabel, yLabel, title, xData, yData):
    plt.bar(xData, yData, align='center', alpha=0.5)
    plt.xlabel(xLabel)
    plt.ylabel(yLabel)
    plt.title(title)
    plt.show()

TTC = []
THROUGHPUT = []
EMISSIONS = []
tempTTC = []
tempTHROUGHPUT = []
tempEMISSIONS = []

NUMBEROFITERATIONS = 3

SCENARIO = "Roadworks"
# SCENARIO = "Collision"

useCases = ["\BaselineHDV", "\BaselineCAV"]
LEVELOFSERVICE = ["A", "B", "C", "D"]
vehicleTypes = ["HDV", "L4-CV"]

safetyFiles, effiencyFiles = creatingFiles(SCENARIO, useCases, LEVELOFSERVICE, vehicleTypes)

for i in range(0, len(safetyFiles)):
    tempTTC.append(safetyKPIs(safetyFiles[i]))
    throughputTemp, emissionsTemp = effiencyKPIs(effiencyFiles[i])
    tempTHROUGHPUT.append(throughputTemp)
    tempEMISSIONS.append(emissionsTemp)
    if i % NUMBEROFITERATIONS == 0:
        print("Finished LOS ", los)
        TTC.append(np.mean(tempTTC))
        THROUGHPUT.append(np.mean(tempTHROUGHPUT))
        EMISSIONS.append(np.mean(tempEMISSIONS))
        tempTTC, tempTHROUGHPUT, tempEMISSIONS = []
    
    
graphingKPIs(TTC, THROUGHPUT, EMISSIONS, LEVELOFSERVICE)
print("TTC", TTC)
print("Throughput", THROUGHPUT)
print("CO2", EMISSIONS)