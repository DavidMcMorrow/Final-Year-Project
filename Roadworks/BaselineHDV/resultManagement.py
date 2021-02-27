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
    for iteration in range(0,3):
        filename = "Roadworks\BaselineHDV\Output-Files\LOS-" + str(los) + "\Trips-HDV-" + str(iteration+1) + ".xml"
        document = minidom.parse(filename)
        trips = document.getElementsByTagName('tripinfo')
        count = 0
        
        for i in range(0, len(trips)):
            if(float(trips[i].getAttribute("arrival") ) < 3600):
                count = count + 1
        throughput.append(count)
    return np.mean(throughput)



LEVELOFSERVICE = ["A", "B", "C", "D"]
TTC = []
THROUGHPUT = []

for los in LEVELOFSERVICE:
    TTC.append(safetyKPIs(los))
    THROUGHPUT.append(effiencyKPIs(los))

print("TTC", TTC)
print("Throughput", THROUGHPUT)
print("CO2")