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
                for types in vehicleTypes:
                    safetyFilepath = SCENARIO + case + "\Output-Files\LOS-" + los + "\SSM-" + types + "-" + str(i) + ".xml"
                    effiencyFilepath = SCENARIO + case + "\Output-Files\LOS-" + los + "\Trips-" + str(i) + ".xml"
                    
                    tempTTC, tempDRAC, tempPET = safetyKPIs(safetyFilepath)
                    VehiclesTTCArray.append(tempTTC)
                    VehiclesDRACArray.append(tempDRAC)
                    VehiclesPETArray.append(tempPET)

                    tempThroughput, tempEmmisions, VehiclesWaitingTimes, VehiclesDuration = effiencyKPIs(effiencyFilepath)
                    
                    VehiclesThroughputArray.append(tempThroughput)
                    VehiclesEmmisionsArray.append(tempEmmisions)
                    

                    safetyFiles.append(safetyFilepath)
                    effiencyFiles.append(effiencyFilepath)
                    # print("VehiclesTTCArray", VehiclesTTCArray)
                    # print("VehiclesThroughputArray", VehiclesThroughputArray)
                    # print("VehiclesDuration", len(VehiclesDuration))

                IterationTTCArray.append(np.sum(VehiclesTTCArray))
                IterationDRACArray.append(np.sum(VehiclesDRACArray))
                IterationPETArray.append(np.sum(VehiclesPETArray))
                IterationThroughputArray.append(np.sum(VehiclesThroughputArray))
                IterationEmmisionsArray.append(np.sum(VehiclesEmmisionsArray))
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
            LOSThroughputArray.append(np.array(VehiclesThroughputArray).mean())
            LOSEmmisionsArray.append(np.array(VehiclesEmmisionsArray).mean())
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
        if ttc.getAttribute("time") != "NA":# and desiredConflict == True:
            numberOfTTC = numberOfTTC + 1

    DRAC = document.getElementsByTagName('maxDRAC')
    for drac in DRAC:
        typeOfConflict = ttc.getAttribute("type")
        desiredConflict = typeOfConflict in encounterTypes
        if drac.getAttribute("time") != "NA": #and desiredConflict == True:
            numberOfDRAC = numberOfDRAC + 1

    PET = document.getElementsByTagName('PET')
    for pet in PET:
        typeOfConflict = ttc.getAttribute("type")
        desiredConflict = typeOfConflict in encounterTypes
        if pet.getAttribute("time") != "NA" and float(pet.getAttribute("value")) < 1.5:# and desiredConflict == True:
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
    
    return count, np.mean(emissionsPerRun), waitingTimes, tripDuration

def intialiseAxisAndTitle(j, TTC, DRAC, PET, THROUGHPUT, EMISSIONS, WaitingTimesArray, DurationArray, SCENARIO, StdTTCArray, StdDRACArray, StdPETArray, StdThroughputArray, StdEmmisionsArray, StdWaitingTimesArray, StdDurationArray):
    if(j == 0):
        array = TTC
        yAxis = "Number of TTC Incidents"
        title = SCENARIO + ": TTC Incidents"
        std = StdTTCArray
    elif (j==1):
        array = DRAC
        yAxis = "Number of DRAC Incidents"
        title = SCENARIO + ": DRAC"
        std = StdDRACArray
    elif (j==2):
        array = PET
        yAxis = "Number of PET Incidents"
        title = SCENARIO + ": PET"
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
                # "Baseline P1": array[3],
                # "Real TMS P1": array[4],
                # "Baseline P2": array[5],
                # "Real TMS P2": array[6],
                # "Baseline P3": array[7],
                # "Real TMS P3": array[8],
                # "Baseline 100% L4-CV": array[0],
                # "TMS 100% L4-CV": array[1],
            }, 
            # index=["A", "B", "C", "D"]
            index=["A", "B", "C"]
            # index=["B", "C"]
        )
        plotdata.plot(kind='bar', yerr=std)
        plt.rc('font', size=14)
       
        plt.xlabel(xAxis, size=20)
        # plt.yscale("log")
        # ax = plt.subplot(111)
        # chartBox = ax.get_position()
        # ax.set_position([chartBox.x0, chartBox.y0, chartBox.width*0.7, chartBox.height])
        # ax.legend(loc='upper center', bbox_to_anchor=(1.25, 0.8), shadow=True, ncol=1)
        plt.ylabel(yAxis, size=20)
        plt.xticks(size = 18)
        plt.yticks(size = 18)
        plt.title(title, size=20)
    plt.show()

def graphingFunction(xLabel, yLabel, title, xData, yData):
    plt.bar(xData, yData, align='center', alpha=0.5)
    plt.xlabel(xLabel)
    plt.ylabel(yLabel)
    plt.title(title)
    plt.show()

def graphingIncidents(ttcScenario, ttcUseCase, ttcLOS, i):
    NumberOfTTCPerVehicle = []
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
        NumberOfTTCPerVehicle.append(len(followTTCXCoor))
    # print("ttcXCoor", ttcXCoor)
    # print("ttcYCoor", ttcYCoor)
    from matplotlib.offsetbox import TextArea, DrawingArea, OffsetImage, AnnotationBbox
    # print("NumberOfTTCPerVehicle", NumberOfTTCPerVehicle)
    # print("sum", sum(NumberOfTTCPerVehicle))
    import matplotlib.pyplot as plt
    import matplotlib.image as mpimg
   
    # fig, ax = plt.subplots()

    # ax.set_xlim(0, 1)
    # ax.set_ylim(0, 1)

    import matplotlib.pyplot as plt
    im = plt.imread("Incident background.PNG")
    implot = plt.imshow(im)


    # imagebox = OffsetImage(arr_lena, zoom=0.2)

    # ab = AnnotationBbox(imagebox, (500, 500))

    # plt.scatter(x=[(505 * 0.7), (498 * 0.7)], y=[(500 * 0.7), (505 * 0.7)], c='r', s=1)
    # plt.plot(followTTCXCoor, followTTCYCoor, 'o', color='black')
    # print("followTTCXCoor", followTTCXCoor)
    fittedX = [element  for element in followTTCXCoor]
    # print("fittedX", fittedX)
    # print("followTTCYCoor", followTTCYCoor)
    fittedY = [element  for element in followTTCYCoor]
    # print("fittedX", fittedY)
    
    plt.plot(fittedX, fittedY, 'o', color='red')
    plt.show()

    
    # plt.draw()
    
    ax.add_artist(ab)
    # plt.grid()
    
    plt.xlabel("meters")
    plt.ylabel("meters")
    # plt.savefig('add_picture_matplotlib_figure.png',bbox_inches='tight')
    plt.show()
    return NumberOfTTCPerVehicle

def gettingTTCPositions(safetyFilepath, followTTCXCoor, followTTCYCoor, otherTTCXCoor, otherTTCYCoor):
    document = minidom.parse(safetyFilepath)
    TTC = document.getElementsByTagName('PET')
    leadFollowTypes = ["2", "3"]
    otherTypes = ["11", "12"]
    for ttc in TTC:
        typeOfConflict = ttc.getAttribute("type")
        
        if ttc.getAttribute("time") != "NA":
            leadFollowIssue = ttc.getAttribute("type") in leadFollowTypes
            otherIssue = ttc.getAttribute("type") in otherTypes
            # if leadFollowIssue == True:
            tempCoor = ttc.getAttribute("position").split(",")
            followTTCXCoor.append(float(tempCoor[0]))
            followTTCYCoor.append(float(tempCoor[1]))
            # if otherIssue == True:
            # tempCoor = ttc.getAttribute("position").split(",")
            # otherTTCXCoor.append(float(tempCoor[0]))
            # otherTTCYCoor.append(float(tempCoor[1]))
    from statistics import mode
    # print("mode X", mode(followTTCXCoor))
    # print("mode Y", mode(followTTCYCoor))
    # print("X", set(followTTCXCoor))
    # print("mode Y", set(followTTCYCoor))
    # findingWhereIncidentsOccur(followTTCXCoor, followTTCYCoor)
    return followTTCXCoor, followTTCYCoor, otherTTCXCoor, otherTTCYCoor

def plottingLocationsOfIncidents():
    ttcScenario = "Roadworks"
    ttcUseCase = ["\BaselinePenetration1", "\RealTMSPenetration1"]
    # ttcUseCase = "\RealTMSPenetration3"
    # print("ttcUseCase", ttcUseCase)
    ttcLOS = "D"
    i = 0
    import numpy as np
    for uc in ttcUseCase:
        Total = [0, 0, 0, 0, 0]
        for i in range(0, 3):
            print("ttcUseCase", ttcUseCase)
            print("i", i)
            value = graphingIncidents(ttcScenario, uc, ttcLOS, i)
            Total = np.add(Total, value)
        print("total", Total)

def graphingPerformance():
    TTC = []
    DRAC = []
    PET = []
    THROUGHPUT = []
    EMISSIONS = []

    NUMBEROFITERATIONS = 3
    # NUMBEROFITERATIONS = 1

    # SCENARIO = "Roadworks"
    SCENARIO = "Collision"

    useCases = ["\BaselineHDV", "\BaselineCAV", "\RealTMSCAV"]
    # useCases = ["\BaselineHDV", "\BaselineCAV", "\RealTMSCAV", "\BaselinePenetration1", "\RealTMSPenetration1", 
    #             "\BaselinePenetration2", "\RealTMSPenetration2", "\BaselinePenetration3", "\RealTMSPenetration3"]

    # LEVELOFSERVICE = ["A", "B", "C", "D"]
    LEVELOFSERVICE = ["A", "B", "C"]
    # LEVELOFSERVICE = ["B", "C"]
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

def metricGathering(trips, emissions, start, end, count, TYPE):
    metric = 0
    hit = 0
    if (trips.getAttribute("departLane").split("-")[0] == start):
        if (trips.getAttribute("arrivalLane").split("-")[0] == end):
            if TYPE == "waitingTime":
                metric = float(trips.getAttribute("waitingTime"))
                hit = 1
            elif TYPE == "duration":
                metric = float(trips.getAttribute("duration"))
                hit = 1
            elif TYPE == "CO2_abs":
                metric = float(emissions[count].getAttribute("CO2_abs"))
                hit = 1
            elif TYPE == "Throughput":
                if (float(trips.getAttribute("arrival")) < 3600):
                    metric = 1
                    hit = 1
    return metric, hit

def depthEfficiency():
    SCENARIO = "Collision"

    useCases = ["\RealTMSCAV"]

    # LEVELOFSERVICE = ["A", "B", "C", "D"]
    LEVELOFSERVICE = ["A"]
    # LEVELOFSERVICE = ["B", "C"]
    vehicleTypes = ["HDV", "L4-CV"]

    TYPE = "waitingTime"
    # TYPE = "duration"
    # TYPE = "CO2_abs"
    # TYPE = "Throughput"

    iteration = 0
    effiencyFilepath = SCENARIO + useCases[0] + "\Output-Files\LOS-" + LEVELOFSERVICE[0] + "\Trips-" + str(iteration) + ".xml"

    document = minidom.parse(effiencyFilepath)
    trips = document.getElementsByTagName('tripinfo')
    emissions = document.getElementsByTagName('emissions')
    count = 0
    metric = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    number = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    for trip in trips:
        temp1, temp2 = metricGathering(trip, emissions, "left", "top", count, TYPE)
        metric[0] = metric[0] + temp1
        number[0] = number[0] + temp2
        temp1, temp2 = metricGathering(trip, emissions, "left", "right", count, TYPE)
        metric[1] = metric[1] + temp1
        number[1] = number[1] + temp2
        temp1, temp2 = metricGathering(trip, emissions, "left", "bottom", count, TYPE)
        metric[2] = metric[2] + temp1
        number[2] = number[2] + temp2

        temp1, temp2 = metricGathering(trip, emissions, "top", "right", count, TYPE)
        metric[3] = metric[3] + temp1
        number[3] = number[3] + temp2
        temp1, temp2 = metricGathering(trip, emissions, "top", "bottom", count, TYPE)
        metric[4] = metric[4] + temp1
        number[4] = number[4] + temp2
        temp1, temp2 = metricGathering(trip, emissions, "top", "left", count, TYPE)
        metric[5] = metric[5] + temp1
        number[5] = number[5] + temp2

        temp1, temp2 =  metricGathering(trip, emissions, "right", "bottom", count, TYPE)
        metric[6] = metric[6] + temp1
        number[6] = number[6] + temp2
        temp1, temp2 = metricGathering(trip, emissions, "right", "left", count, TYPE)
        metric[7] = metric[7] + temp1
        number[7] = number[7] + temp2
        temp1, temp2 = metricGathering(trip, emissions, "right", "top", count, TYPE)
        metric[8] = metric[8] + temp1
        number[8] = number[8] + temp2

        temp1, temp2 = metricGathering(trip, emissions, "bottom", "left", count, TYPE)
        metric[9] = metric[9] + temp1
        number[9] = number[9] + temp2
        temp1, temp2 = metricGathering(trip, emissions, "bottom", "top", count, TYPE)
        metric[10] = metric[10] + temp1
        number[10] = number[10] + temp2
        temp1, temp2 = metricGathering(trip, emissions, "bottom", "right", count, TYPE)
        metric[11] = metric[11] + temp1
        number[11] = number[11] + temp2
        
        count = count + 1
    
    print("metric", metric)
    print("number", number)
    print("metric", sum(metric))

    if TYPE == "duration" or TYPE == "waitingTime":
        for i in range(len(metric)):
            metric[i] = metric[i] / number[i]

    print("metric", metric)
    print("number", number)
    print("metric", sum(metric))
    xAxis = "Level of Service"
    plotdata = pd.DataFrame(
            {
                "Left -> Top": metric[0],
                "Left -> Right": metric[1],
                "Left -> Bottom": metric[2],
                "Top -> Right": metric[3],
                "Top -> Bottom": metric[4],
                "Top -> Left": metric[5],
                "Right -> Bottom": metric[6],
                "Right -> Left": metric[7],
                "Right -> Top": metric[8],
                "Bottom -> Left": metric[9],
                "Bottom -> Top": metric[10],
                "Bottom -> Right": metric[11],
            }, 
            # index=["A", "B", "C", "D"]
            # index=["A", "B", "C"]
            index=[LEVELOFSERVICE[0]]
        )
    plotdata.plot(kind='bar',) #yerr=std)
    plt.rc('font', size=14)
       
    plt.xlabel(xAxis, size=20)
    # plt.yscale("log")
    # ax = plt.subplot(111)
    # chartBox = ax.get_position()
    # ax.set_position([chartBox.x0, chartBox.y0, chartBox.width*0.7, chartBox.height])
    # ax.legend(loc='upper center', bbox_to_anchor=(1.25, 0.8), shadow=True, ncol=1)
    # plt.ylabel(yAxis, size=20)
    plt.xticks(size = 18)
    plt.yticks(size = 18)
    # plt.title(title, size=20)
    plt.show()

# graphingPerformance()

depthEfficiency()




# if (trips.getAttribute("departLane").split("-") == "left"):
#             if (trips.getAttribute("arrivalLane").split("-") == "top"):
#                 if TYPE == "waitingTime":
#                     metric[0] = metric[0] + float(trips.getAttribute("waitingTime"))
#                 elif TYPE == "duration":
#                     metric[0] = metric[0] + float(trips.getAttribute("duration"))
#                 elif TYPE == "CO2_abs":
#                     metric[0] = metric[0] + float(emissions[count].getAttribute("duration"))
#                 elif TYPE == "Throughput":
#                     if (float(trips.getAttribute("arrival")) > 3600):
#                         metric[0] = metric[0] + float(emissions[count].getAttribute("duration"))