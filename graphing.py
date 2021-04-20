from xml.dom import minidom
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

def newCreatingFiles(SCENARIO, useCases, LEVELOFSERVICE, vehicleTypes, NUMBEROFITERATIONS):
    safetyFiles = []
    effiencyFiles = []
    TTCArray = []
    DRACArray = []
    PETArray = []
    ThroughputArray = []
    EmmisionsArray = []
    DurationArray = []
    WaitingTimesArray = []

    StdTTCArray = []
    StdDRACArray = []
    StdPETArray = []
    StdThroughputArray = []
    StdEmmisionsArray = []
    StdDurationArray = []
    StdWaitingTimesArray = []

    for case in useCases:
        print("Case", case)
        LOSTTCArray = []
        LOSDRACArray = []
        LOSPETArray = []
        LOSThroughputArray = []
        LOSEmmisionsArray = []
        LOSWaitingTimesArray = []
        LOSDurationArray = []

        LOSTTCArrayStd = []
        LOSDRACArrayStd = []
        LOSPETArrayStd = []
        LOSThroughputArrayStd = []
        LOSEmmisionsArrayStd = []
        LOSWaitingTimesArrayStd = []
        LOSDurationArrayStd = []
        
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
            IterationWaitingTimes = []
            IterationDuration = []      
            for i in range(0, NUMBEROFITERATIONS):
                # print("i", i)
                VehiclesTTCArray = []
                VehiclesPETArray = []
                VehiclesDRACArray = []
                VehiclesThroughputArray = []
                VehiclesEmmisionsArray = []
                VehiclesWaitingTimes = []
                VehiclesDuration = []
                effiencyFilepath = SCENARIO + case + "\Output-Files\LOS-" + los + "\Trips-" + str(i) + ".xml"
                tempThroughput, tempEmmisions, VehiclesWaitingTimes, VehiclesDuration = effiencyKPIs(effiencyFilepath)
                    
                VehiclesThroughputArray.append(tempThroughput)
                # VehiclesEmmisionsArray.append(tempEmmisions)
                for types in vehicleTypes:
                    safetyFilepath = SCENARIO + case + "\Output-Files\LOS-" + los + "\SSM-" + types + "-" + str(i) + ".xml"
                    effiencyFilepath = SCENARIO + case + "\Output-Files\LOS-" + los + "\Trips-" + str(i) + ".xml"
                    
                    tempTTC, tempDRAC, tempPET = safetyKPIs(safetyFilepath)
                    VehiclesTTCArray.append(tempTTC)
                    VehiclesDRACArray.append(tempDRAC)
                    VehiclesPETArray.append(tempPET)

                    
                
                    safetyFiles.append(safetyFilepath)
                    effiencyFiles.append(effiencyFilepath)
                    # print("VehiclesTTCArray", VehiclesTTCArray)
                    # print("VehiclesThroughputArray", VehiclesThroughputArray)
                    # print("VehiclesDuration", len(VehiclesDuration))

                IterationTTCArray.append(np.sum(VehiclesTTCArray))
                IterationDRACArray.append(np.sum(VehiclesDRACArray))
                IterationPETArray.append(np.sum(VehiclesPETArray))
                IterationThroughputArray.append(np.sum(VehiclesThroughputArray))
                # IterationEmmisionsArray.append(np.sum(VehiclesEmmisionsArray))
                IterationEmmisionsArray = np.concatenate((IterationEmmisionsArray, tempEmmisions))
                IterationWaitingTimes = np.concatenate((IterationWaitingTimes, VehiclesWaitingTimes))
                IterationDuration = np.concatenate((IterationDuration, VehiclesDuration))
                # IterationDuration + VehiclesDuration
                # print("IterationTTCArray", IterationTTCArray)
                # print("IterationThroughputArray", IterationThroughputArray)
                # print("IterationWaitingTimes", IterationWaitingTimes)
                # print("len(IterationWaitingTimes)", len(IterationWaitingTimes))

            LOSTTCArray.append(np.array(IterationTTCArray).mean())
            LOSDRACArray.append(np.array(IterationDRACArray).mean())
            LOSPETArray.append(np.array(IterationPETArray).mean())
            LOSThroughputArray.append(np.array(IterationThroughputArray).mean())
            LOSEmmisionsArray.append(np.array(IterationEmmisionsArray).mean())
            LOSWaitingTimesArray.append(np.array(IterationWaitingTimes).mean())
            LOSDurationArray.append(np.array(IterationDuration).mean())

            LOSTTCArrayStd.append(np.array(IterationTTCArray).std())
            LOSDRACArrayStd.append(np.array(IterationDRACArray).std())
            LOSPETArrayStd.append(np.array(IterationPETArray).std())
            LOSThroughputArrayStd.append(np.array(IterationThroughputArray).std())
            LOSEmmisionsArrayStd.append(np.array(IterationEmmisionsArray).std())
            LOSWaitingTimesArrayStd.append(np.array(IterationWaitingTimes).std())
            LOSDurationArrayStd.append(np.array(IterationDuration).std())

            # print("LOSTTCArray", LOSTTCArray)
            # print("LOSTTCArrayStd", LOSTTCArrayStd)
            # print("LOSThroughputArray", LOSThroughputArray)
            # print("LOSThroughputArrayStd", LOSThroughputArrayStd)
            # print("LOSWaitingTimesArray", LOSWaitingTimesArray)
            # print("LOSWaitingTimesArrayStd", LOSWaitingTimesArrayStd)
        
        TTCArray.append(LOSTTCArray)
        DRACArray.append(LOSDRACArray)
        PETArray.append(LOSPETArray)
        ThroughputArray.append(LOSThroughputArray)
        EmmisionsArray.append(LOSEmmisionsArray)
        WaitingTimesArray.append(LOSWaitingTimesArray)
        DurationArray.append(LOSDurationArray)

        StdTTCArray.append(LOSTTCArrayStd)
        StdDRACArray.append(LOSDRACArrayStd)
        StdPETArray.append(LOSPETArrayStd)
        StdThroughputArray.append(LOSThroughputArrayStd)
        StdEmmisionsArray.append(LOSEmmisionsArrayStd)
        StdWaitingTimesArray.append(LOSWaitingTimesArrayStd)
        StdDurationArray.append(LOSDurationArrayStd)
            
    return (safetyFiles, effiencyFiles, TTCArray, DRACArray, PETArray, ThroughputArray, EmmisionsArray, WaitingTimesArray, DurationArray, 
    StdTTCArray, StdDRACArray, StdPETArray, StdThroughputArray, StdEmmisionsArray, StdWaitingTimesArray, StdDurationArray)

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
    encounterTypes = ["2", "3"]
    safetyIncidents = []
    # print("filename", filename)
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
    waitingTimes = []
    tripDuration = []
    for i in range(0, len(trips)):
        if(float(trips[i].getAttribute("arrival") ) < 3600):
            count = count + 1
        emissionsPerRun.append(float(emissions[i].getAttribute("CO2_abs")))
        waitingTimes.append(float(trips[i].getAttribute("waitingTime")))
        tripDuration.append(float(trips[i].getAttribute("duration")))
    
    return count, emissionsPerRun, waitingTimes, tripDuration

def intialiseAxisAndTitle(j, TTC, DRAC, PET, THROUGHPUT, EMISSIONS, WaitingTimesArray, DurationArray, SCENARIO, StdTTCArray, StdDRACArray, StdPETArray, StdThroughputArray, StdEmmisionsArray, StdWaitingTimesArray, StdDurationArray):
    if SCENARIO == "Collision":
        SCENARIO = SCENARIO + "(With Vehicle Rerouting)"
    if(j == 0):
        array = TTC
        yAxis = "Number of TTC Incidents"
        title = SCENARIO + ": TTC Incidents"
        std = StdTTCArray
    elif (j==1):
        array = DRAC
        yAxis = "Number of DRAC Incidents"
        title = SCENARIO + ": DRAC Incidents"
        std = StdDRACArray
    elif (j==2):
        array = PET
        yAxis = "Number of PET Incidents"
        title = SCENARIO + ": PET Incidents"
        std = StdPETArray
    elif (j==3):
        array = THROUGHPUT
        yAxis = "Throughput of network (veh/hr)"
        title = SCENARIO + ": Throughput"
        std = StdThroughputArray
    elif (j==4):
        array = EMISSIONS
        yAxis = "CO2 (mg)"
        title = SCENARIO + ": Environmental"
        std = StdEmmisionsArray
    elif (j==5):
        array = WaitingTimesArray
        yAxis = "Time (s)"
        title = SCENARIO + ": Mean Waiting Times"
        std = StdWaitingTimesArray
    elif (j==6):
        array = DurationArray
        yAxis = "Time (s)"
        title = SCENARIO + ": Mean Trip Duration"
        std = StdDurationArray
        
    return array, yAxis, title, std

def graphingKPIs(TTC, DRAC, PET, THROUGHPUT, EMISSIONS, WaitingTimesArray, DurationArray, SCENARIO, StdTTCArray, StdDRACArray, StdPETArray, StdThroughputArray, StdEmmisionsArray, StdWaitingTimesArray, StdDurationArray):
    xAxis = "Level of Service"
    array = []
    for j in range(0, 7):
        count = 0
        hdvArray = []
        l4CVArray = []
        
        array, yAxis, title, std = intialiseAxisAndTitle(j, TTC, DRAC, PET, THROUGHPUT, EMISSIONS, WaitingTimesArray, DurationArray, SCENARIO, StdTTCArray, StdDRACArray, StdPETArray, StdThroughputArray, StdEmmisionsArray, StdWaitingTimesArray, StdDurationArray)
        print("title", title)
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
                # "Baseline 100%": array[0],
                # "Real TMS 100%": array[1],
            }, 
            # index=["A", "B", "C", "D"]
            index=["A", "B", "C"]
            # index=["B"]
        )
        print("array", array[0])
        print("std", std[0])
        plotdata.plot(kind='bar', yerr=std)
        plt.rc('font', size=14)
       
        plt.xlabel(xAxis, size=20)
        # plt.yscale("log")
        ax = plt.subplot(111)
        chartBox = ax.get_position()
        ax.set_position([chartBox.x0, chartBox.y0, chartBox.width*0.7, chartBox.height])
        ax.legend(loc='upper center', bbox_to_anchor=(1.25, 0.8), shadow=True, ncol=1)
        plt.ylabel(yAxis, size=20)
        plt.xticks(size = 18)
        plt.yticks(size = 18)
        plt.title(title, size=18)
    plt.show()


def graphingFunction(xLabel, yLabel, title, xData, yData):
    plt.bar(xData, yData, align='center', alpha=0.5)
    plt.xlabel(xLabel)
    plt.ylabel(yLabel)
    plt.title(title)
    plt.show()

def graphingTTCs(ttcScenario, ttcUseCase, ttcLOS, i):
    if ttcUseCase == "\BaselineHDV":
        vehicleTypes = ["L0-HDV"]
    elif ttcUseCase == "\BaselineCAV" or ttcUseCase == "\RealTMSCAV":
        vehicleTypes = ["L4-CV"]
    else:
        vehicleTypes = ["L0-HDV", "L2-AV", "L2-CV", "L4-AV","L4-CV"]
    followTTCXCoor = []
    followTTCYCoor = []
    otherTTCXCoor = []
    otherTTCYCoor = []

    for types in vehicleTypes:
        safetyFilepath = ttcScenario + ttcUseCase + "\Output-Files\LOS-" + ttcLOS + "\SSM-" + types + "-" + str(i) + ".xml"
        followTTCXCoor, followTTCYCoor, otherTTCXCoor, otherTTCYCoor = gettingTTCPositions(safetyFilepath, followTTCXCoor, followTTCYCoor, otherTTCXCoor, otherTTCYCoor)
    # print("ttcXCoor", ttcXCoor)
    # print("ttcYCoor", ttcYCoor)
    plt.plot(followTTCXCoor, followTTCYCoor, 'o', color='black')
    plt.plot(otherTTCXCoor, otherTTCYCoor, 'o', color='red')
    plt.xlabel("meters")
    plt.ylabel("meters")
    plt.show()

def gettingTTCPositions(safetyFilepath, followTTCXCoor, followTTCYCoor, otherTTCXCoor, otherTTCYCoor):
    document = minidom.parse(safetyFilepath)
    TTC = document.getElementsByTagName('minTTC')
    leadFollowTypes = ["2", "3"]
    otherTypes = ["11", "12"]
    for ttc in TTC:
        typeOfConflict = ttc.getAttribute("type")
        
        if ttc.getAttribute("time") != "NA":
            leadFollowIssue = ttc.getAttribute("type") in leadFollowTypes
            otherIssue = ttc.getAttribute("type") in otherTypes
            if leadFollowIssue == True:
                tempCoor = ttc.getAttribute("position").split(",")
                followTTCXCoor.append(float(tempCoor[0]))
                followTTCYCoor.append(float(tempCoor[1]))
            if otherIssue == True:
                tempCoor = ttc.getAttribute("position").split(",")
                otherTTCXCoor.append(float(tempCoor[0]))
                otherTTCYCoor.append(float(tempCoor[1]))
    
    return followTTCXCoor, followTTCYCoor, otherTTCXCoor, otherTTCYCoor

def plottingLocationsOfTTCs():
    ttcScenario = "Collision"
    ttcUseCase = "\RealTMSPenetration1"
    ttcLOS = "A"
    i = 0
    graphingTTCs(ttcScenario, ttcUseCase, ttcLOS, i)

def graphingPerformance():
    TTC = []
    DRAC = []
    PET = []
    THROUGHPUT = []
    EMISSIONS = []

    NUMBEROFITERATIONS = 3
    # NUMBEROFITERATIONS = 2

    # SCENARIO = "Roadworks"
    SCENARIO = "Collision"

    # useCases = ["\BaselinePenetration3", "\RealTMSPenetration3"]
    useCases = ["\BaselineHDV", "\BaselineCAV", "\RealTMSCAV", "\BaselinePenetration1", "\RealTMSPenetration1", 
                "\BaselinePenetration2", "\RealTMSPenetration2", "\BaselinePenetration3", "\RealTMSPenetration3"]

    # LEVELOFSERVICE = ["A", "B", "C", "D"]
    LEVELOFSERVICE = ["A", "B", "C"]
    # LEVELOFSERVICE = ["A"]
    vehicleTypes = ["HDV", "L4-CV"]

    safetyFiles, effiencyFiles, TTC, DRAC, PET, THROUGHPUT, EMISSIONS, WaitingTimesArray, DurationArray, StdTTCArray, StdDRACArray, StdPETArray, StdThroughputArray, StdEmmisionsArray, StdWaitingTimesArray, StdDurationArray = newCreatingFiles(SCENARIO, useCases, LEVELOFSERVICE, vehicleTypes, NUMBEROFITERATIONS)

    print("TTC", TTC)
    print("DRAC", DRAC)
    print("PET", PET)
    print("Throughput", THROUGHPUT)
    print("CO2", EMISSIONS)
    print("WaitingTimesArray", WaitingTimesArray)
    print("DurationArray", DurationArray)
    print("-----------------")
    print("StdTTCArray", StdTTCArray)
    print("StdDRACArray", StdDRACArray)
    print("StdPETArray", StdPETArray)
    print("StdThroughputArray", StdThroughputArray)
    print("StdEmmisionsArray", StdEmmisionsArray)
    print("StdWaitingTimesArray", StdWaitingTimesArray)
    print("StdDurationArray", StdDurationArray)

    graphingKPIs(TTC, DRAC, PET, THROUGHPUT, EMISSIONS, WaitingTimesArray, DurationArray, SCENARIO, StdTTCArray, StdDRACArray, StdPETArray, StdThroughputArray, StdEmmisionsArray, StdWaitingTimesArray, StdDurationArray)

# graphingPerformance()
# plottingLocationsOfTTCs()


def metricGathering(trips, emissions, start, end, count, TYPE, metric):
    # metric = 0
    hit = 0
    
    if (trips.getAttribute("departLane").split("-")[0] == start):
        if (trips.getAttribute("arrivalLane").split("-")[0] == end):
            if TYPE == "waitingTime":
                metric.append(float(trips.getAttribute("waitingTime")))
                hit = 1
            elif TYPE == "duration":
                metric.append(float(trips.getAttribute("duration")))
                hit = 1
            elif TYPE == "CO2_abs":
                metric.append(float(emissions[count].getAttribute("CO2_abs")))
                hit = 1
            elif TYPE == "Throughput":
                if (float(trips.getAttribute("arrival")) < 3600):
                    metric.append(1)
                    hit = 1
    return metric
        
        

def depthEfficiency():
    SCENARIO = "Collision"
    # SCENARIO = "Roadworks"
    # useCases = ["\BaselineCAV"]
    # useCases = ["\RealTMSCAV"]

    # useCases = ["\BaselinePenetration3"]
    useCases = ["\RealTMSPenetration3"] 
    # LEVELOFSERVICE = ["A", "B", "C", "D"]
    LEVELOFSERVICE = ["C"]
    # LEVELOFSERVICE = ["B", "C"]
    vehicleTypes = ["HDV", "L4-CV"]

    metric = [[], [], [], [], [], [], [], [], [], [], [], []]
    number = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    realOrFake = "TMS"
    # realOrFake = "Baseline"
    
    # TYPE = "waitingTime"
    TYPE = "duration"
    # TYPE = "CO2_abs"
    # TYPE = "Throughput"

    # TITLE = realOrFake + ": Throughput by route"
    # TITLE = realOrFake + ": Amount of CO2 emitted by route"
    # TITLE = realOrFake + ": Mean Waiting Times per route"
    TITLE = realOrFake + ": Mean Trip Duration per route"

    # YAXIS = "Throughput of network (veh/hr)"
    # YAXIS = "CO2 (mg)"
    # YAXIS = "Time (s)"
    YAXIS = "Time (s)"
    iteration = 0
    for i in range(3):
        print("i", i)
        effiencyFilepath = SCENARIO + useCases[0] + "\Output-Files\LOS-" + LEVELOFSERVICE[0] + "\Trips-" + str(i) + ".xml"

        document = minidom.parse(effiencyFilepath)
        trips = document.getElementsByTagName('tripinfo')
        emissions = document.getElementsByTagName('emissions')
        count = 0
    
        for trip in trips:
            metric[0] = metricGathering(trip, emissions, "left", "top", count, TYPE, metric[0])
            # metric[0] = metric[0] + temp1
            # number[0] = number[0] + temp2
            metric[1] = metricGathering(trip, emissions, "left", "right", count, TYPE, metric[1])
            # metric[1] = metric[1] + temp1
            # number[1] = number[1] + temp2
            metric[2] = metricGathering(trip, emissions, "left", "bottom", count, TYPE, metric[2])
            # metric[2] = metric[2] + temp1
            # number[2] = number[2] + temp2

            metric[3] = metricGathering(trip, emissions, "top", "right", count, TYPE, metric[3])
            # metric[3] = metric[3] + temp1
            # number[3] = number[3] + temp2
            metric[4] = metricGathering(trip, emissions, "top", "bottom", count, TYPE, metric[4])
            # metric[4] = metric[4] + temp1
            # number[4] = number[4] + temp2
            metric[5] = metricGathering(trip, emissions, "top", "left", count, TYPE, metric[5])
            # metric[5] = metric[5] + temp1
            # number[5] = number[5] + temp2

            metric[6] =  metricGathering(trip, emissions, "right", "bottom", count, TYPE, metric[6])
            # metric[6] = metric[6] + temp1
            # number[6] = number[6] + temp2
            metric[7] = metricGathering(trip, emissions, "right", "left", count, TYPE, metric[7])
            # metric[7] = metric[7] + temp1
            # number[7] = number[7] + temp2
            metric[8] = metricGathering(trip, emissions, "right", "top", count, TYPE, metric[8])
            # metric[8] = metric[8] + temp1
            # number[8] = number[8] + temp2

            metric[9] = metricGathering(trip, emissions, "bottom", "left", count, TYPE, metric[9])
            # metric[9] = metric[9] + temp1
            # number[9] = number[9] + temp2
            metric[10] = metricGathering(trip, emissions, "bottom", "top", count, TYPE, metric[10])
            # metric[10] = metric[10] + temp1
            # number[10] = number[10] + temp2
            metric[11] = metricGathering(trip, emissions, "bottom", "right", count, TYPE, metric[11])
            # metric[11] = metric[11] + temp1
            # number[11] = number[11] + temp2
            
            count = count + 1
        
        print("metric", metric[0])
        # print("number", number)
        # print("metric", sum(metric))
    mean = [[], [], [], [], [], [], [], [], [], [], [], []]
    std = [[], [], [], [], [], [], [], [], [], [], [], []]
    if TYPE == "duration" or TYPE == "waitingTime" or TYPE == "CO2_abs":
        for i in range(len(metric)):
            mean[i].append(np.array(metric[i]).mean())
            std[i].append(np.array(metric[i]).std())
    else:
        for i in range(len(metric)):
            mean[i].append(sum(metric[i]))
            std[i].append(0)
    # print("metric", metric)
    
    print("Left -> Top", mean[0])
    print("Left -> Right", mean[1])
    print("Left -> Bottom", mean[2])
    print("Top -> Right", mean[3])
    print("Top -> Bottom", mean[4])
    print("Top -> Left", mean[5])
    print("Right -> Bottom", mean[6])
    print("Right -> Left", mean[7])
    print("Right -> Top", mean[8])
    print("Bottom -> Left", mean[9])
    print("Bottom -> Top", mean[10])
    print("Bottom -> Right", mean[11])

   

    xAxis = "Level of Service"
    plotdata = pd.DataFrame(
            {
                "Left -> Top": mean[0],
                "Left -> Right": mean[1],
                "Left -> Bottom": mean[2],
                "Top -> Right": mean[3],
                "Top -> Bottom": mean[4],
                "Top -> Left": mean[5],
                "Right -> Bottom": mean[6],
                "Right -> Left": mean[7],
                "Right -> Top": mean[8],
                "Bottom -> Left": mean[9],
                "Bottom -> Top": mean[10],
                "Bottom -> Right": mean[11],
            }, 
            # index=["A", "B", "C", "D"]
            # index=["A", "B", "C"]
            index=[LEVELOFSERVICE[0]]
        )
    print("std", std)
    print("mean", mean)
    print("std", len(std))
    print("mean", len(mean))
    plotdata.plot(kind='bar', yerr=std)
    
    plt.rc('font', size=14)
       
    plt.xlabel(xAxis, size=20)
    plt.ylabel(YAXIS, size=20)
    # plt.yscale("log")
    # ax = plt.subplot(111)
    # chartBox = ax.get_position()
    # ax.set_position([chartBox.x0, chartBox.y0, chartBox.width*0.7, chartBox.height])
    # ax.legend(loc='upper center', bbox_to_anchor=(1.25, 0.8), shadow=True, ncol=1)
    # plt.ylabel(yAxis, size=20)
    plt.xticks(size = 18)
    plt.yticks(size = 18)
    plt.title(TITLE, size=20)
    plt.show()

graphingPerformance()

# depthEfficiency()



#
#
#
#
