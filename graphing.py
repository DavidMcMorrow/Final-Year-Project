from xml.dom import minidom
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

def newCreatingFiles(SCENARIO, useCases, LEVELOFSERVICE, vehicleTypes):
    safetyFiles = []
    effiencyFiles = []
    TTCArray = []
    DRACArray = []
    PETArray = []
    ThroughputArray = []
    EmmisionsArray = []

    for case in useCases:
        LOSTTCArray = []
        LOSDRACArray = []
        LOSPETArray = []
        LOSThroughputArray = []
        LOSEmmisionsArray = []
        if case == "\BaselineHDV":
            vehicleTypes = ["L0-HDV"]
        elif case == "\BaselineCAV" or case == "\RealTMSCAV":
            vehicleTypes = ["L4-CV"]
        else:
            vehicleTypes = ["L0-HDV", "L2-AV", "L2-CV", "L4-AV","L4-CV"]
        
        for los in LEVELOFSERVICE:
            IterationTTCArray = []
            IterationDRACArray = []
            IterationPETArray = []
            IterationThroughputArray = []
            IterationEmmisionsArray = []        
            for i in range(0, NUMBEROFITERATIONS):
                VehiclesTTCArray = []
                VehiclesPETArray = []
                VehiclesDRACArray = []
                VehiclesThroughputArray = []
                VehiclesEmmisionsArray = [] 
                for types in vehicleTypes:
                    safetyFilepath = SCENARIO + case + "\Output-Files\LOS-" + los + "\SSM-" + types + "-" + str(i) + ".xml"
                    effiencyFilepath = SCENARIO + case + "\Output-Files\LOS-" + los + "\Trips-" + str(i) + ".xml"
                    
                    tempTTC, tempDRAC, tempPET = safetyKPIs(safetyFilepath)
                    VehiclesTTCArray.append(tempTTC)
                    VehiclesDRACArray.append(tempDRAC)
                    VehiclesPETArray.append(tempPET)

                    tempThroughput, tempEmmisions = effiencyKPIs(effiencyFilepath)
                    VehiclesThroughputArray.append(tempThroughput)
                    VehiclesEmmisionsArray.append(tempEmmisions)

                    safetyFiles.append(safetyFilepath)
                    effiencyFiles.append(effiencyFilepath)
                    print("VehiclesTTCArray", VehiclesTTCArray)
                IterationTTCArray.append(np.mean(VehiclesTTCArray))
                IterationDRACArray.append(np.mean(VehiclesDRACArray))
                IterationPETArray.append(np.mean(VehiclesPETArray))
                IterationThroughputArray.append(np.mean(VehiclesThroughputArray))
                IterationEmmisionsArray.append(np.mean(VehiclesThroughputArray))
                print("IterationTTCArray", IterationTTCArray)

            LOSTTCArray.append(np.mean(IterationTTCArray))
            LOSDRACArray.append(np.mean(IterationDRACArray))
            LOSPETArray.append(np.mean(IterationPETArray))
            LOSThroughputArray.append(np.mean(IterationThroughputArray))
            LOSEmmisionsArray.append(np.mean(IterationEmmisionsArray))
            print("LOSTTCArray", LOSTTCArray)

        TTCArray.append(LOSTTCArray)
        DRACArray.append(LOSDRACArray)
        PETArray.append(LOSPETArray)
        ThroughputArray.append(LOSThroughputArray)
        EmmisionsArray.append(LOSEmmisionsArray)
            
    return safetyFiles, effiencyFiles, TTCArray, DRACArray, PETArray, ThroughputArray, EmmisionsArray

def newGatheringTheData(safetyFiles, effiencyFiles):
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
        if i % NUMBEROFITERATIONS == 3:
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
    print("filename", filename)
    document = minidom.parse(filename)
    numberOfTTC = 0
    numberOfDRAC = 0
    numberOfPET = 0
    TTC = document.getElementsByTagName('minTTC')
    for ttc in TTC:
        if ttc.getAttribute("time") != "NA":
            numberOfTTC = numberOfTTC + 1

    DRAC = document.getElementsByTagName('maxDRAC')
    for drac in DRAC:
        if drac.getAttribute("time") != "NA":
            numberOfDRAC = numberOfDRAC + 1

    PET = document.getElementsByTagName('PET')
    for pet in PET:
        if pet.getAttribute("time") != "NA":
            numberOfPET = numberOfPET + 1

    return numberOfTTC, numberOfDRAC, numberOfPET

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

def intialiseAxisAndTitle(j, SCENARIO):
    if(j == 0):
        array = TTC
        yAxis = "Number of TTC"
        title = SCENARIO + ": TTC"
    elif (j==1):
        array = THROUGHPUT
        yAxis = "Number of DRAC"
        title = SCENARIO + ": DRAC"
    elif (j==2):
        array = EMISSIONS
        yAxis = "Number of PET"
        title = SCENARIO + ": PET"
    elif (j==3):
        array = EMISSIONS
        yAxis = "CO2"
        title = SCENARIO + ": Environmental"
    elif (j==4):
        array = THROUGHPUT
        yAxis = "Throughput of network"
        title = SCENARIO + ": Throughput"
    return array, yAxis, title

def graphingKPIs(TTC, DRAC, PET, THROUGHPUT, EMISSIONS, SCENARIO):
    xAxis = "Level of Service"
    array = []
    for j in range(0, 5):
        count = 0
        hdvArray = []
        l4CVArray = []
        
        array, yAxis, title = intialiseAxisAndTitle(j, SCENARIO)

        if j == 0:
            array = TTC
        elif j == 1:
            array = DRAC
        elif j == 2:
            array = PET
        elif j == 3:
            array = THROUGHPUT
        elif j == 4:
            array = EMISSIONS
        
        
        plotdata = pd.DataFrame(
            {
                "Baseline HDV": array[0],
                "Baseline L4-CV": array[1],
                "Real TMS L4-CV": array[2],
                "Real TMS P1": array[3],
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
DRAC = []
PET = []
THROUGHPUT = []
EMISSIONS = []

NUMBEROFITERATIONS = 4

SCENARIO = "Roadworks"
# SCENARIO = "Collision"

# useCases = ["\BaselineHDV", "\BaselineCAV"]
useCases = ["\BaselineHDV", "\BaselineCAV", "\RealTMSCAV", "\RealTMSPenetration1"]
# useCases = ["\BaselineHDV", "\BaselineCAV", "\RealTMSCAV", "\RealTMSPenetration1", "\RealTMSPenetration2", "\RealTMSPenetration3"]
# LEVELOFSERVICE = ["A", "B", "C", "D"]
LEVELOFSERVICE = ["A", "B"]
vehicleTypes = ["HDV", "L4-CV"]

# safetyFiles, effiencyFiles = creatingFiles(SCENARIO, useCases, LEVELOFSERVICE, vehicleTypes)
safetyFiles, effiencyFiles, TTC, DRAC, PET, THROUGHPUT, EMISSIONS = newCreatingFiles(SCENARIO, useCases, LEVELOFSERVICE, vehicleTypes)

print("---------------------------")
print("Safety Files", safetyFiles[0])
print("Effiency Files", effiencyFiles[0])
print("Safety Files", safetyFiles[1])
print("Effiency Files", effiencyFiles[1])
print("Safety Files", safetyFiles[25])
print("Effiency Files", effiencyFiles[25])
print("---------------------------")

# TTC, THROUGHPUT, EMISSIONS = gatheringTheData(safetyFiles, effiencyFiles)
    
print("TTC", TTC)
print("DRAC", DRAC)
print("PET", PET)
print("Throughput", THROUGHPUT)
print("CO2", EMISSIONS)

# penetrations = ["BaselineHDV", "BaselineCAV", "RealTMSCAV", "RealTMSPenetration1"]
graphingKPIs(TTC, DRAC, PET, THROUGHPUT, EMISSIONS, SCENARIO)

