from xml.dom import minidom
import matplotlib
import matplotlib.pyplot as plt
import numpy as np


def safetyKPIs(los):
    safetyIncidents = []
    for iteration in range(0,3):
        filename = "Roadworks\BaselineHDV\Output-Files\LOS-" + str(los) + "\SSM-HDV-" + str(iteration+1) + ".xml"
        document = minidom.parse(filename)
        safetyIncidents.append(len(document.getElementsByTagName('conflict')))
    return np.mean(safetyIncidents)

def effiencyKPIs(los):
    throughput = []
    CO2 = []
    allEmissionsForLOS = []
    for iteration in range(0,3):
        filename = "Roadworks\BaselineHDV\Output-Files\LOS-" + str(los) + "\Trips-HDV-" + str(iteration+1) + ".xml"
        document = minidom.parse(filename)
        trips = document.getElementsByTagName('tripinfo')
        emissions = document.getElementsByTagName('emissions')
        count = 0
        emissionsPerRun = []
        for i in range(0, len(trips)):
            if(float(trips[i].getAttribute("arrival") ) < 3600):
                count = count + 1
                emissionsPerRun.append(float(emissions[i].getAttribute("CO2_abs")))
        allEmissionsForLOS.append(np.mean(emissionsPerRun))

        throughput.append(count)
    return np.mean(throughput), np.mean(allEmissionsForLOS)

def graphingKPIs(TTC, THROUGHPUT, EMISSIONS, LEVELOFSERVICE):
    yAxisSafety = "Number of Incidents"
    yAxisCO2 = "Number of CO2"
    yAxisThroughPut = "ThroughPut of network"
    count = 0
    for los in LEVELOFSERVICE:
        titleSafety = "LOS-" + los + ": TTC"
        titleCO2 = "LOS-" + los + ": Total CO2 Output"
        titleThroughput = "LOS-" + los + ": Throughput"
        xAxis = "LOS"
        graphingFunction(xAxis, yAxisSafety, titleSafety, los, TTC[count])
        graphingFunction(xAxis, yAxisCO2, titleThroughput, los, THROUGHPUT[count])
        graphingFunction(xAxis, yAxisThroughPut, titleCO2, los, EMISSIONS[count])
        count = count + 1
        
def graphingFunction(xLabel, yLabel, title, xData, yData):
    plt.bar(xData, yData, align='center', alpha=0.5)
    plt.xlabel(xLabel)
    plt.ylabel(yLabel)
    plt.title(title)
    plt.show()

LEVELOFSERVICE = ["A", "B", "C", "D"]

TTC = []
THROUGHPUT = []
EMISSIONS = []

for los in LEVELOFSERVICE:
    TTC.append(safetyKPIs(los))
    throughputTemp, emissionsTemp = effiencyKPIs(los)
    THROUGHPUT.append(throughputTemp)
    EMISSIONS.append(emissionsTemp)
    print("Finished LOS ", los)
    
graphingKPIs(TTC, THROUGHPUT, EMISSIONS, LEVELOFSERVICE)
print("TTC", TTC)
print("Throughput", THROUGHPUT)
print("CO2", EMISSIONS)