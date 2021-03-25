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
                # print("i", i)
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
                    print("VehiclesThroughputArray", VehiclesThroughputArray)

                IterationTTCArray.append(np.sum(VehiclesTTCArray))
                IterationDRACArray.append(np.sum(VehiclesDRACArray))
                IterationPETArray.append(np.sum(VehiclesPETArray))
                IterationThroughputArray.append(np.mean(VehiclesThroughputArray))
                IterationEmmisionsArray.append(np.mean(VehiclesEmmisionsArray))
                print("IterationTTCArray", IterationTTCArray)
                print("IterationThroughputArray", IterationThroughputArray)

            LOSTTCArray.append(np.mean(IterationTTCArray))
            LOSDRACArray.append(np.mean(IterationDRACArray))
            LOSPETArray.append(np.mean(IterationPETArray))
            LOSThroughputArray.append(np.mean(IterationThroughputArray))
            LOSEmmisionsArray.append(np.mean(IterationEmmisionsArray))
            print("LOSTTCArray", LOSTTCArray)
            print("LOSThroughputArray", LOSThroughputArray)

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
    encounterTypes = ["2"]
    safetyIncidents = []
    print("filename", filename)
    document = minidom.parse(filename)
    numberOfTTC = 0
    numberOfDRAC = 0
    numberOfPET = 0
    TTC = document.getElementsByTagName('minTTC')
    for ttc in TTC:
        typeOfConflict = ttc.getAttribute("type")
        desiredConflict = typeOfConflict in encounterTypes
        if ttc.getAttribute("time") != "NA": #and desiredConflict == True:
            numberOfTTC = numberOfTTC + 1

    DRAC = document.getElementsByTagName('maxDRAC')
    for drac in DRAC:
        typeOfConflict = ttc.getAttribute("type")
        desiredConflict = typeOfConflict in encounterTypes
        if drac.getAttribute("time") != "NA":# and desiredConflict == True:
            numberOfDRAC = numberOfDRAC + 1

    PET = document.getElementsByTagName('PET')
    for pet in PET:
        typeOfConflict = ttc.getAttribute("type")
        desiredConflict = typeOfConflict in encounterTypes
        if pet.getAttribute("time") != "NA":# and desiredConflict == True:
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

def intialiseAxisAndTitle(j, TTC, DRAC, PET, THROUGHPUT, EMISSIONS, SCENARIO):
    if(j == 0):
        array = TTC
        yAxis = "Number of TTC"
        title = SCENARIO + ": TTC"
    elif (j==1):
        array = DRAC
        yAxis = "Number of DRAC"
        title = SCENARIO + ": DRAC"
    elif (j==2):
        array = PET
        yAxis = "Number of PET"
        title = SCENARIO + ": PET"
    elif (j==3):
        array = THROUGHPUT
        yAxis = "Throughput of network"
        title = SCENARIO + ": Throughput"
    elif (j==4):
        array = EMISSIONS
        yAxis = "CO2"
        title = SCENARIO + ": Environmental"
        
    return array, yAxis, title

def graphingKPIs(TTC, DRAC, PET, THROUGHPUT, EMISSIONS, SCENARIO):
    xAxis = "Level of Service"
    array = []
    for j in range(0, 5):
        count = 0
        hdvArray = []
        l4CVArray = []
        
        array, yAxis, title = intialiseAxisAndTitle(j, TTC, DRAC, PET, THROUGHPUT, EMISSIONS, SCENARIO)
        
        plotdata = pd.DataFrame(
            {
                "Baseline HDV": array[0],
                "Baseline 100% L4-CV": array[1],
                "Real TMS 100% L4-CV": array[2],
                "Baseline P1": array[3],
                "Real TMS P1": array[4],
                "Baseline P2": array[5],
                "Real TMS P2": array[6],
                "Baseline P3": array[7],
                "Real TMS P3": array[8],
            }, 
            #index=["A", "B", "C"]
            index=["B"]
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

NUMBEROFITERATIONS = 1

SCENARIO = "Roadworks"
# SCENARIO = "Collision"

useCases = ["\BaselinePenetration1"]
useCases = ["\BaselineHDV", "\BaselineCAV", "\RealTMSCAV", "\BaselinePenetration1", "\RealTMSPenetration1", 
            "\BaselinePenetration2", "\RealTMSPenetration2", "\BaselinePenetration3", "\RealTMSPenetration3"]
# useCases = ["\BaselineHDV", "\BaselineCAV", "\RealTMSCAV", "\BaselinePenetration1", "\RealTMSPenetration1", 
#             "\BaselinePenetration2", "\RealTMSPenetration2", "\BaselinePenetration3", "\RealTMSPenetration3"]
# LEVELOFSERVICE = ["A", "B", "C", "D"]
LEVELOFSERVICE = ["B"]
vehicleTypes = ["HDV", "L4-CV"]

# safetyFiles, effiencyFiles = creatingFiles(SCENARIO, useCases, LEVELOFSERVICE, vehicleTypes)
safetyFiles, effiencyFiles, TTC, DRAC, PET, THROUGHPUT, EMISSIONS = newCreatingFiles(SCENARIO, useCases, LEVELOFSERVICE, vehicleTypes)
# safetyFiles, effiencyFiles, TTCArray, DRACArray, PETArray, ThroughputArray, EmmisionsArray
# TTC, THROUGHPUT, EMISSIONS = gatheringTheData(safetyFiles, effiencyFiles)
    
print("TTC", TTC)
print("DRAC", DRAC)
print("PET", PET)
print("Throughput", THROUGHPUT)
print("CO2", EMISSIONS)

# penetrations = ["BaselineHDV", "BaselineCAV", "RealTMSCAV", "RealTMSPenetration1"]
graphingKPIs(TTC, DRAC, PET, THROUGHPUT, EMISSIONS, SCENARIO)

