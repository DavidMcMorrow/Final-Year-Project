import random
import os
import traci
from xml.dom import minidom
import time

def settingUpVehicles(SCENARIO, USECASEFOLDER, LOS, rate):
    count = 0
    textFileToRun = SCENARIO + USECASEFOLDER + "\PreparingVehicleModels\How to use.txt"
    with open(textFileToRun) as f:
        for line in f:
            if(line != "\n"):
                line = 'cmd /c ' + line
                if(line.find('python PreparingVehicleModels/randomTrips.py') != -1):
                    line = line.rstrip()
                    line = line + " " + str(random.randint(0,9))
                    if LOS == "A":
                        line = line + " -p " + str(rate[count])#str(1.86)
                    if LOS == "B":
                        line = line + " -p " + str(rate[count]) #str(1.25)
                    if LOS == "C":
                        line = line + " -p " + str(rate[count]) # str(1.07)
                    if LOS == "D":
                        line = line + " -p " + str(rate[count]) #str(0.94)
                    if LOS == "Test":
                        line = line + " -p " + str(rate[count]) #str(0.7)
                    count = count + 1
                    # print("------------")
                    # print("line = ", line)
                    # print("------------")
    
                os.system(line)

def removeOldToC(vehiclesThatTORed):
    for veh in vehiclesThatTORed:
        temp1 = veh in traci.vehicle.getIDList()
        if temp1 == True:
            if(traci.vehicle.getTypeID(veh)[:2] == "L0"):
                vehiclesThatTORed.remove(veh)
    return vehiclesThatTORed

def collisionReRouteClockWiseFirst(edge):
    newRoute = []
    if(edge == "top"):
        newRoute = ["top-approaching", "bottom-exit"]
    elif(edge == "right"):
        newRoute = ["right-approaching", "bottom-exit"]
    elif(edge == "bottom"):
        newRoute = ["bottom-approaching", "top-exit"]
    
    return newRoute

def collisionReRouteClockWiseSecond(edge):
    newRoute = []
    if(edge == "top"):
        newRoute = ["top-approaching", "bottom-exit"]
    elif(edge == "right"):
        newRoute = ["right-approaching", "top-exit"]
    elif(edge == "bottom"):
        newRoute = ["bottom-approaching", "top-exit"]
    return newRoute

def roadworksReRouting(target):
    newRoute = []
    if(target == "top-exit"):
        newRoute = ["left-long-approaching", "preparation", "left-short-approaching", "right-exit"]
    elif(target == "right-exit"):
        newRoute = ["left-long-approaching", "preparation", "left-short-approaching", "bottom-exit"]
    # elif(target == "preparation"):
    #     newRoute = ["left-long-approaching", "preparation"]
    return newRoute

def baselineAlterOutputFiles(SCENARIO, BASELINE, LOS, ITERATION, VEHICLETYPES):
    time.sleep(10)
    for vehType in VEHICLETYPES:
        newSafetyFile = SCENARIO + "\Baseline" + BASELINE  + "\Output-Files\LOS-" + LOS + "\SSM-" + vehType + "-"+ str(ITERATION) + ".xml"        
        oldSafetyFile = SCENARIO + "\Baseline" + BASELINE + "\Output-Files\SSM-" + vehType + ".xml"

        if(os.path.exists(oldSafetyFile)):
            with open(oldSafetyFile, 'r') as firstFile:
                with open(newSafetyFile, 'w') as secondFile:
                    for line in firstFile:
                        secondFile.write(line)
    
    newTripFile = SCENARIO + "\Baseline" + BASELINE  + "\Output-Files\LOS-" + LOS + "\Trips-" + str(ITERATION) + ".xml"
    oldTripFile = SCENARIO + "\Baseline" + BASELINE + "\Output-Files\TripInfo.xml"

    with open(oldTripFile, 'r') as firstFile:
        with open(newTripFile, 'w') as secondFile:
            for line in firstFile:
                secondFile.write(line)

def flowCorrection(files, vehiclesTypes, baseline):
    for j in range(0, len(files)):
        mydoc = minidom.parse(files[j])
        routes = mydoc.getElementsByTagName('route')
        vehicles = mydoc.getElementsByTagName('vehicle')
        for i in range(0, len(routes)):
            if(routes[i].getAttribute("edges")[:1] == "l" and routes[i].getAttribute("edges")[-1] != "t"):
                result = random.randint(0, 2)
                if result == 0:
                    routes[i].setAttribute("edges", "left-long-approaching preparation left-short-approaching bottom-exit")
                elif result == 1:
                    routes[i].setAttribute("edges", "left-long-approaching preparation left-short-approaching right-exit")
                else: 
                    routes[i].setAttribute("edges", "left-long-approaching preparation left-short-approaching top-exit")

            if(routes[i].getAttribute("edges").startswith("p")):
                route = "left-long-approaching " + routes[i].getAttribute("edges")
                routes[i].setAttribute("edges", route)
            elif(routes[i].getAttribute("edges").startswith("left-short-approaching")):
                route = "left-long-approaching preparation " + routes[i].getAttribute("edges")
                routes[i].setAttribute("edges", route)

            if( routes[i].getAttribute("edges").endswith("remerging-lane")):
                route = routes[i].getAttribute("edges") + " left-exit"
                routes[i].setAttribute("edges", route)
            elif routes[i].getAttribute("edges").endswith("closed-lane"):
                route = routes[i].getAttribute("edges") + " remerging-lane left-exit"
                routes[i].setAttribute("edges", route)

            if(vehiclesTypes[j] == "L0-HDV"):
                if(routes[i].getAttribute("edges") == "left-long-approaching preparation left-short-approaching top-exit"):
                    temp = vehiclesTypes[j] + "-Left-"
                    vehicles[i].setAttribute("type", temp)
                    routes[i].setAttribute("edges", "left-long-approaching preparation")
                elif(routes[i].getAttribute("edges") == "left-long-approaching preparation left-short-approaching right-exit"):
                    temp = vehiclesTypes[j] + "-Straight-"
                    vehicles[i].setAttribute("type", temp)
            else:
                if(routes[i].getAttribute("edges") == "left-long-approaching preparation left-short-approaching top-exit"):
                    temp = vehiclesTypes[j] + "-Left-"
                    vehicles[i].setAttribute("type", temp)
                    routes[i].setAttribute("edges", "left-long-approaching preparation")
                elif(routes[i].getAttribute("edges") == "left-long-approaching preparation left-short-approaching bottom-exit"):
                    temp = vehiclesTypes[j] + "-Right-"
                    vehicles[i].setAttribute("type", temp)
                    
        with open(files[j], "w") as fs:
            fs.write(mydoc.toxml()) 
            fs.close()  

def removeVehiclesThatPassCenter(vehiclesApproachingClosure):
    for vehicle in vehiclesApproachingClosure:
        temp1 = vehicle in traci.vehicle.getIDList()
        if temp1 == True:
            temp = traci.vehicle.getLaneID(vehicle)[:7]
            if(temp == ":center"):
                vehiclesApproachingClosure.remove(vehicle)
        else:
            vehiclesApproachingClosure.remove(vehicle)
    return vehiclesApproachingClosure

def TMSAlterOutputFiles(SCENARIO, penetration, LOS, ITERATION, VEHICLETYPES):
    time.sleep(10)
    for vehType in VEHICLETYPES:
        newSafetyFile = SCENARIO + "\RealTMS" + penetration  + "\Output-Files\LOS-" + LOS + "\SSM-" + vehType + "-"+ str(ITERATION) + ".xml"        
        oldSafetyFile = SCENARIO + "\RealTMS" + penetration + "\Output-Files\SSM-" + vehType + ".xml"
        print("newSafetyFile", newSafetyFile)
        if(os.path.exists(oldSafetyFile)):
            with open(oldSafetyFile, 'r') as firstFile:
                with open(newSafetyFile, 'w') as secondFile:
                    for line in firstFile:
                        secondFile.write(line)
    
    newTripFile = SCENARIO + "\RealTMS" + penetration  + "\Output-Files\LOS-" + LOS + "\Trips-" + str(ITERATION) + ".xml"
    oldTripFile = SCENARIO + "\RealTMS" + penetration + "\Output-Files\TripInfo.xml"

    with open(oldTripFile, 'r') as firstFile:
        with open(newTripFile, 'w') as secondFile:
            for line in firstFile:
                secondFile.write(line)
############### ###############







############### Penetration Rates ###############
def vehiclePenetrationRates1(LOS):
    if LOS == "A":
        rate = [36, 36, 12, 12, 3]
    if LOS == "B":
        rate = [26, 26, 8.4, 8.4, 2.15]
    if LOS == "C":
        rate = [20, 20, 7, 7, 1.76]
    if LOS == "D":
        rate = [19, 19, 6.2, 6.2, 1.57]
    # if LOS == "Test":
    #     print("HERE")
    #     rate = [3.1, 2.5, 2.2, 2, 2.32]
    return rate

def vehiclePenetrationRates2(LOS):
    if LOS == "A":
        rate = [18, 18, 9, 9, 4.65]
    if LOS == "B":
        rate = [12, 12, 6.2, 6.2, 3.21]
    if LOS == "C":
        rate = [11, 11, 5, 5, 2.69]
    if LOS == "D":
        rate = [9.5, 9.5, 4.75, 4.75, 2.32]
    # if LOS == "Test":
    #     print("HERE")
    #     rate = [3.1, 2.5, 2.2, 2, 2.35]
    return rate

def vehiclePenetrationRates3(LOS):
    if LOS == "A":
        rate = [12, 12, 6, 6, 18]
    if LOS == "B":
        rate = [8.4, 8.4, 4.2, 4.2, 12]
    if LOS == "C":
        rate = [7, 7, 3.5, 3.5, 11]
    if LOS == "D":
        rate = [6.2, 6.2, 3.1, 3.1, 9.5]
    # if LOS == "Test":
    #     print("HERE")
    #     rate = [3.1, 2.5, 2.2, 2, 2.35]
    return rate
############### ###############









############### Roadworks Baseline Caller Functions ###############
def handlingLeftApproachingBaseline(vehiclesThatTORed, ENCOUNTEREDCLOSURETOC, leftApproachingLastDetected): 
    # leftApproachingLastDetected[0] = leftUpStreamTMS(leftApproachingLastDetected[0])
    leftApproachingLastDetected[0] = standardVehicleScenarioDetection(leftApproachingLastDetected[0])
    # vehiclesThatTORed, leftApproachingLastDetected[2] = issuingToCToVehiclesTMS(vehiclesThatTORed, TMSISSUEDTOC, leftApproachingLastDetected[2])
    leftApproachingLastDetected[1], vehiclesThatTORed = lateVehicleIncidentDetection(ENCOUNTEREDCLOSURETOC, leftApproachingLastDetected[1], vehiclesThatTORed)
    return leftApproachingLastDetected

def handlingTopRightBottomBaseline(topBottomRightLateDetectors, vehiclesThatTORed, ENCOUNTEREDCLOSURETOC, topBottomRightLateLastDetected): 
    vehiclesThatTORed, topBottomRightLateLastDetected = lateVehicleIndidentDetectionTopRightBottom(topBottomRightLateDetectors, vehiclesThatTORed, ENCOUNTEREDCLOSURETOC, topBottomRightLateLastDetected)
    return vehiclesThatTORed, topBottomRightLateLastDetected

def roadWorksMajorDelayDetectionBaseline(delayBeforeReRoute, vehiclesApproachingClosure, vehiclesThatTORed, TIMETOPERFORMDELAYTOC, step, majorDelayDetectionLastDetected, majorDelayDetectors, NUMBEROFVEHICLESREROUTED):
    vehiclesApproachingClosure, majorDelayDetectionLastDetected = addingVehicleToDelayDetection(majorDelayDetectors, vehiclesApproachingClosure, "bottom-exit", majorDelayDetectionLastDetected)
    vehiclesApproachingClosure, vehiclesThatTORed, NUMBEROFVEHICLESREROUTED = detectingMajorDelay(vehiclesApproachingClosure, vehiclesThatTORed, delayBeforeReRoute, TIMETOPERFORMDELAYTOC, step, NUMBEROFVEHICLESREROUTED)
    return vehiclesApproachingClosure, vehiclesThatTORed, majorDelayDetectionLastDetected, NUMBEROFVEHICLESREROUTED

def allowingAccessToRightLaneBaseline(minorWaitLengthBeforeAction, vehiclesThatTORed, accessToRightLaneLastDetected, TIMETOPERFORMDELAYTOC):
    # accessToRightLaneLastDetected[0] = allowingAccessToRightLaneTMS(accessToRightLaneLastDetected[0])
    vehiclesThatTORed, accessToRightLaneLastDetected[0] = allowingAccessToRightLaneLate(accessToRightLaneLastDetected[0], minorWaitLengthBeforeAction, vehiclesThatTORed, TIMETOPERFORMDELAYTOC)
    return vehiclesThatTORed, accessToRightLaneLastDetected
############### ###############

############################## Roadworks TMS ##############################
############### Caller Functions ###############
def handlingTopRightBottom(topBottomRightLateDetectors, topBottomRightTMSDetectors, vehiclesThatTORed, ENCOUNTEREDCOLLISIONTOC, topBottomRightLateLastDetected, topBottomRightTMSLastDetected):
    topBottomRightTMSLastDetected = roadworksTMSTopRightBottom(topBottomRightTMSDetectors, topBottomRightTMSLastDetected)
    # vehiclesThatTORed, leftApproachingLastDetected[2] = issuingToCToVehiclesTMSTopRightBottom(vehiclesThatTORed, TMSISSUEDTOC, leftApproachingLastDetected[2])
    vehiclesThatTORed, topBottomRightLateLastDetected = lateVehicleIndidentDetectionTopRightBottom(topBottomRightLateDetectors, vehiclesThatTORed, ENCOUNTEREDCOLLISIONTOC, topBottomRightLateLastDetected)    
    return vehiclesThatTORed, topBottomRightLateLastDetected, topBottomRightTMSLastDetected

def handlingLeftApproaching(vehiclesThatTORed, TMSISSUEDTOC, ENCOUNTEREDCLOSURETOC,leftApproachingLastDetected):
    leftApproachingLastDetected[0] = leftUpStreamTMS(leftApproachingLastDetected[0])
    leftApproachingLastDetected[1] = standardVehicleScenarioDetection(leftApproachingLastDetected[1])
    # vehiclesThatTORed, leftApproachingLastDetected[2] = issuingToCToVehiclesTMS(vehiclesThatTORed, TMSISSUEDTOC, leftApproachingLastDetected[2])
    leftApproachingLastDetected[3], vehiclesThatTORed = lateVehicleIncidentDetection(ENCOUNTEREDCLOSURETOC, leftApproachingLastDetected[3], vehiclesThatTORed)
    return leftApproachingLastDetected

def allowingAccessToRightLane(minorWaitLengthBeforeAction, vehiclesThatTORed, accessToRightLaneLastDetected, TIMETOPERFORMDELAYTOC):
    accessToRightLaneLastDetected = allowingAccessToRightLaneTMS(accessToRightLaneLastDetected)
    vehiclesThatTORed, accessToRightLaneLastDetected[1] = allowingAccessToRightLaneLate(accessToRightLaneLastDetected[1], minorWaitLengthBeforeAction, vehiclesThatTORed, TIMETOPERFORMDELAYTOC)
    return vehiclesThatTORed, accessToRightLaneLastDetected

def roadWorksMajorDelayDetection(delayBeforeReRoute, vehiclesApproachingClosure, vehiclesThatTORed, TIMETOPERFORMDELAYTOC, step, majorDelayDetectionLastDetected, majorDelayDetectors, NUMBEROFVEHICLESREROUTED):
    vehiclesApproachingClosure, majorDelayDetectionLastDetected = addingVehicleToDelayDetection(majorDelayDetectors, vehiclesApproachingClosure, "bottom-exit", majorDelayDetectionLastDetected)
    vehiclesApproachingClosure, vehiclesThatTORed, NUMBEROFVEHICLESREROUTED = detectingMajorDelay(vehiclesApproachingClosure, vehiclesThatTORed, delayBeforeReRoute, TIMETOPERFORMDELAYTOC, step, NUMBEROFVEHICLESREROUTED)
    return vehiclesApproachingClosure, vehiclesThatTORed, majorDelayDetectionLastDetected, NUMBEROFVEHICLESREROUTED

############### Top Right Bottom Approach ###############
def roadworksTMSTopRightBottom(topBottomRightTMSDetectors, lastVehicleDetected): 
    for det in topBottomRightTMSDetectors:
        det_vehs = traci.inductionloop.getLastStepVehicleIDs(det)
        for veh in det_vehs:
            route = traci.vehicle.getRoute(veh)
            target = route[len(route) - 1]
            checkingPriorDetection = veh in lastVehicleDetected
            vehicleType = (traci.vehicle.getTypeID(veh)).split('-')[1]
            if traci.vehicle.getVehicleClass(veh) != "passenger" and target == "left-exit" and checkingPriorDetection == False and vehicleType == "CV":
                receivedTMSResult = random.randint(0, 99) ## CONSIDER
                if receivedTMSResult < 99:
                    traci.vehicle.setVehicleClass(veh, "passenger")

    return lastVehicleDetected

def lateVehicleIndidentDetectionTopRightBottom(topBottomRightLateDetectors, vehiclesThatTORed, ENCOUNTEREDCOLLISIONTOC, lastVehicleDetected):
    for det in topBottomRightLateDetectors:
        det_vehs = traci.inductionloop.getLastStepVehicleIDs(det)
        for veh in det_vehs:
            route = traci.vehicle.getRoute(veh)
            target = route[len(route) - 1]
            temp = veh in vehiclesThatTORed
            checkingPriorDetection = veh in lastVehicleDetected
            vehicleType = (traci.vehicle.getTypeID(veh)).split('-')[1]
            if temp == False and traci.vehicle.getVehicleClass(veh) != "passenger" and target == "left-exit" and vehicleType != "HDV" :
                result = random.randint(0, 99) ## CONSIDER
                waitingTime = traci.vehicle.getWaitingTime(veh)
                if(result < 0 and checkingPriorDetection == False):
                    traci.vehicle.setVehicleClass(veh, "passenger")
                # elif waitingTime > 5:
                #     traci.vehicle.setParameter(veh, "device.toc.requestToC", ENCOUNTEREDCOLLISIONTOC)
                #     vehiclesThatTORed.append(veh)
                else: 
                    traci.vehicle.setParameter(veh, "device.toc.requestToC", ENCOUNTEREDCOLLISIONTOC)
                    vehiclesThatTORed.append(veh)
    return vehiclesThatTORed, lastVehicleDetected

############### ###############

############### Left-Approach Left Lane ###############
def roadworksReRoutingLeftVehicles(veh):
    route = traci.vehicle.getRoute(veh)
    target = route[len(route) - 1]
    if(target == "preparation"):
        traci.vehicle.setRoute(veh, ["preparation", "left-short-approaching", "top-exit"])

def leftUpStreamTMS(leftApproachingLastDetected):
    det_vehs = traci.inductionloop.getLastStepVehicleIDs("rerouting-left-vehicles")
    for veh in det_vehs:
        vehicleType = (traci.vehicle.getTypeID(veh)).split('-')[1]
        if traci.vehicle.getVehicleClass(veh) == "custom2" and vehicleType == "CV" and leftApproachingLastDetected != veh:
            receivedTMSResult = random.randint(0, 99)
            if receivedTMSResult < 99:
                # print("Did get TMS", veh)
                traci.vehicle.setParameter(veh, "device.toc.dynamicToCThreshold", 0)
                traci.vehicle.setVehicleClass(veh, "custom1")
                roadworksReRoutingLeftVehicles(veh)
                traci.vehicle.updateBestLanes(veh)
            # else:
                # print("Didn't get TMS", veh)
        leftApproachingLastDetected = veh
    return leftApproachingLastDetected
                
def standardVehicleScenarioDetection(leftApproachingLastDetected):
    det_vehs = traci.inductionloop.getLastStepVehicleIDs("leftlaneStandardDetection")
    for veh in det_vehs:
        if traci.vehicle.getVehicleClass(veh) == "custom2" and leftApproachingLastDetected != veh:
            typeOfVehicle = traci.vehicle.getTypeID(veh)[:2]
            # print("getTypeID", traci.vehicle.getTypeID(veh)[:2])
            # print("veh", veh)
            figuredOutScenario = random.randint(0,99) ## Needs to be considered
            # print("figuredOutScenario", figuredOutScenario)
            if(figuredOutScenario < 0 and (typeOfVehicle == "L4" or typeOfVehicle == "L2")):
                # print("Did detect blockage", veh)
                if traci.vehicle.getParameter(veh, "has.toc.device") == "true":
                    traci.vehicle.setParameter(veh, "device.toc.dynamicToCThreshold", 0)
                traci.vehicle.setVehicleClass(veh, "custom1")
                roadworksReRoutingLeftVehicles(veh)
                traci.vehicle.updateBestLanes(veh)
            # else:
            #     print("Didn't detect blockage", veh)
            elif (figuredOutScenario < 99 and typeOfVehicle == "L0"):
                traci.vehicle.setVehicleClass(veh, "custom1")
                roadworksReRoutingLeftVehicles(veh)
                traci.vehicle.updateBestLanes(veh)

        leftApproachingLastDetected = veh
    return leftApproachingLastDetected
    
def issuingToCToVehiclesTMS(vehiclesThatTORed, TMSISSUEDTOC, leftApproachingLastDetected):
    det_vehs = traci.inductionloop.getLastStepVehicleIDs("issuingToCInVehicleTMS")
    for veh in det_vehs:
        temp = veh in vehiclesThatTORed
        vehicleType = (traci.vehicle.getTypeID(veh)).split('-')[1]
        # print("vehicleType", vehicleType)
        receivedToCAdvice = random.randint(0,9)
        if( (temp == False) and (vehicleType == "CV") and (receivedToCAdvice < 3) and (leftApproachingLastDetected != veh)):
            # print("Received ToC Advice", veh)
            roadworksReRoutingLeftVehicles(veh)
            traci.vehicle.setParameter(veh, "device.toc.requestToC", TMSISSUEDTOC)
            vehiclesThatTORed.append(veh)
            traci.vehicle.updateBestLanes(veh)

        if vehicleType == "HDV":
            receivedToCAdvice = random.randint(0,9) ## Needs to be considered
            if(receivedToCAdvice < 4 and leftApproachingLastDetected != veh):
                roadworksReRoutingLeftVehicles(veh)
                traci.vehicle.setVehicleClass(veh, "custom1")
        leftApproachingLastDetected = veh
    return vehiclesThatTORed, leftApproachingLastDetected

def lateVehicleIncidentDetection(ENCOUNTEREDCLOSURETOC, leftApproachingLastDetected, vehiclesThatTORed):
    det_vehs = traci.inductionloop.getLastStepVehicleIDs("allVehiclesToC")
    for veh in det_vehs:
        if leftApproachingLastDetected != veh:
            vehicleType = (traci.vehicle.getTypeID(veh)).split('-')[1]
            roadworksReRoutingLeftVehicles(veh)
            temp = veh in vehiclesThatTORed
            if vehicleType == "HDV":
                traci.vehicle.setVehicleClass(veh, "custom1")
            traci.vehicle.updateBestLanes(veh)
            # elif temp == False:
            #     # print("MADE TOC", veh)
            #     traci.vehicle.setParameter(veh, "device.toc.requestToC", ENCOUNTEREDCLOSURETOC)
            #     vehiclesThatTORed.append(veh)
            #     traci.vehicle.updateBestLanes(veh)
        leftApproachingLastDetected = veh
    return leftApproachingLastDetected, vehiclesThatTORed

############### Remaining functionality in left lane ###############
def allowingAccessToRightLaneTMS(lastVehicleDetected):
    detectors = ["allowingRightLaneAccessTMS", "allowingRightLaneAccess2TMS"]
    count = 0
    for det in detectors:
        det_vehs = traci.inductionloop.getLastStepVehicleIDs(det)
        for veh in det_vehs:
            if lastVehicleDetected[count] != veh:
                route = traci.vehicle.getRoute(veh)
                target = route[len(route) - 1]
                vehicleType = (traci.vehicle.getTypeID(veh)).split('-')[1]
                if target == "right-exit" and vehicleType == "CV":
                    receivedTMSResult = random.randint(0, 99) ## CONSIDER
                    if receivedTMSResult < 99:
                        # print("GOT TMS", veh)
                        traci.vehicle.setVehicleClass(veh, "passenger")
                        traci.vehicle.updateBestLanes(veh)
                    # else:
                    #     print("MISSED TMS", veh)
                lastVehicleDetected[count] = veh
        count = count + 1
    return lastVehicleDetected

def allowingAccessToRightLaneLate(lastVehicleDetected, delayRealisation, vehiclesThatTORed, TIMETOPERFORMDELAYTOC):
    det_vehs = traci.inductionloop.getLastStepVehicleIDs("allowingRightLaneAccessLate")
    for veh in det_vehs:
        if lastVehicleDetected != veh:
            route = traci.vehicle.getRoute(veh)
            target = route[len(route) - 1]
            vehicleClass = traci.vehicle.getVehicleClass(veh)
            if target == "right-exit" and traci.vehicle.getAccumulatedWaitingTime(veh) >= delayRealisation and vehicleClass != "passenger":
                vehicleType = (traci.vehicle.getTypeID(veh)).split('-')[1]
                scenarioRecognitionResult = random.randint(0, 99) ## CONSIDER
                if vehicleType != "HDV" and scenarioRecognitionResult < 0:
                    #  print("GOT TMS the second time", veh)
                     traci.vehicle.setVehicleClass(veh, "passenger")
                     traci.vehicle.updateBestLanes(veh)
                elif vehicleType != "HDV" and scenarioRecognitionResult > 99:
                    # print("HAD TO ToC because of TMS", veh)
                    traci.vehicle.requestToC(veh, TIMETOPERFORMDELAYTOC)
                    vehiclesThatTORed.append(veh)
                    traci.vehicle.updateBestLanes(veh)
                elif vehicleType == "HDV" and scenarioRecognitionResult < 99:
                    # print("GOT THE MESSAGE", veh)
                    traci.vehicle.setVehicleClass(veh, "passenger")
                    traci.vehicle.updateBestLanes(veh)
                # else:
                #     print("JUST MISSED THE MESSAGE", veh)
        lastVehicleDetected = veh
    return vehiclesThatTORed, lastVehicleDetected

def addingVehicleToDelayDetection(majorDelayDetectors, vehiclesApproachingClosure, exitBeingIgnored, majorDelayDetectionLastDetected):
    count = 0
    for det in majorDelayDetectors:
        det_vehs = traci.inductionloop.getLastStepVehicleIDs(det)
        for veh in det_vehs:
            if veh != majorDelayDetectionLastDetected[count]:
                temp1 = traci.vehicle.getRoute(veh)[len(traci.vehicle.getRoute(veh))-1]
                temp2 = veh in vehiclesApproachingClosure
                if ((temp1 != exitBeingIgnored) and (temp2 == False)):
                    vehiclesApproachingClosure.append(veh)

                majorDelayDetectionLastDetected[count] = veh
            # target = traci.vehicle.getRoute(veh)[len(traci.vehicle.getRoute(veh))-1]
            # print("target", target)
            # if (target == "preparation"):
            #     traci.vehicle.changeLane(veh, 2, 10)

        count = count + 1
    return vehiclesApproachingClosure, majorDelayDetectionLastDetected

def detectingMajorDelay(vehiclesApproachingClosure, vehiclesThatTORed, delayBeforeReRoute, ToCLeadTime, step, NUMBEROFVEHICLESREROUTED):
    if (step%6 == 0):
        for veh in vehiclesApproachingClosure:
            temp3 = traci.vehicle.getRoute(veh)[len(traci.vehicle.getRoute(veh))-1]
            if(traci.vehicle.getAccumulatedWaitingTime(veh) > delayBeforeReRoute):
                # print("MAJOR DELAY DETECTED", veh)
                vehiclesApproachingClosure, vehiclesThatTORed, NUMBEROFVEHICLESREROUTED = reRoutingVehicles(veh, temp3, vehiclesApproachingClosure, vehiclesThatTORed, ToCLeadTime, NUMBEROFVEHICLESREROUTED)
    return vehiclesApproachingClosure, vehiclesThatTORed, NUMBEROFVEHICLESREROUTED

def reRoutingVehicles(veh, target, vehiclesApproachingClosure, vehiclesThatTORed, ToCLeadTime, NUMBEROFVEHICLESREROUTED):
    shouldBeRemoved = False
    # print("traci.vehicle.getLaneID(veh)", traci.vehicle.getLaneID(veh))
    if traci.vehicle.getLaneID(veh) == "left-short-approaching_1" or traci.vehicle.getLaneID(veh) == "left-short-approaching_0":
        shouldBeRemoved = True
    else:
        tocResult = random.randint(0, 99) ## NEED TO CONSIDER THIS PROBABILITY MORE
        temp = veh in vehiclesThatTORed

        if(tocResult < 40 and temp == False and (traci.vehicle.getTypeID(veh)[:2] == "L4" or traci.vehicle.getTypeID(veh)[:2] == "L2")):
            # print("ToC due to delay", veh)
            traci.vehicle.requestToC(veh, ToCLeadTime)
            vehiclesThatTORed.append(veh)
            shouldBeRemoved = True
        
        rerouteResult = random.randint(0, 99) ## NEED TO CONSIDER THIS PROBABILITY MORE
        if(rerouteResult < 30 and target != "preparation"):
            # print("+++ReRoute due to delay", veh)
            # print("Target", target)
            traci.vehicle.setVehicleClass(veh, "passenger")
            traci.vehicle.setRoute(veh, roadworksReRouting(target))
            NUMBEROFVEHICLESREROUTED = NUMBEROFVEHICLESREROUTED + 1
            # print("NUMBEROFVEHICLESREROUTED ", NUMBEROFVEHICLESREROUTED)
            shouldBeRemoved = True
            traci.vehicle.updateBestLanes(veh)

    if shouldBeRemoved == True:
        vehiclesApproachingClosure.remove(veh)

    return vehiclesApproachingClosure, vehiclesThatTORed, NUMBEROFVEHICLESREROUTED

############### Upstream ToC ###############
def handlingToCUpstreamRoadworks(lastVehicleDetected):
    detectors= ["upstreamTMSTop_0", "upstreamTMSTop_1", 
                "upstreamTMSRight_0" , "upstreamTMSRight_1", 
                "upstreamTMSBottom_0", "upstreamTMSBottom_1", 
                "upstreamTMSLeft_0", "upstreamTMSLeft_1"]
    count = 0
    for det in detectors:
        det_vehs = traci.inductionloop.getLastStepVehicleIDs(det)
        for veh in det_vehs:
            if lastVehicleDetected[count] != veh:
                upwardToCResult = random.randint(0, 99)
                if (traci.vehicle.getTypeID(veh)[:2] == "L0" and upwardToCResult < 75 and traci.vehicle.getParameter(veh, "has.toc.device") == "true"):
                    # print("upward ToC", veh)
                    traci.vehicle.requestToC(veh, -1)
                # elif traci.vehicle.getTypeID(veh)[:2] == "L0":
                #     # print("HDV Class change", veh)
                #     traci.vehicle.setVehicleClass(veh, "passenger")
                vehicleType = (traci.vehicle.getTypeID(veh)).split('-')[1]
                
                if (traci.vehicle.getTypeID(veh)[:2] == "L4" or traci.vehicle.getTypeID(veh)[:2] == "L2"):
                    # print("CAV Class change", veh)
                    traci.vehicle.setVehicleClass(veh, "custom1")
                    if (traci.vehicle.getParameter(veh, "device.toc.dynamicToCThreshold") == 0):
                        traci.vehicle.setParameter(veh, "device.toc.dynamicToCThreshold", 9)
                lastVehicleDetected[count] = veh
        count = count + 1
    return lastVehicleDetected
############### ###############



























############################## Collision TMS ##############################
def stoppingCrashedVehicles():
    traci.vehicle.setStop("crashed-car-lane-zero.0", "left-exit-blockage", 26.5, 0, 3600)
    traci.vehicle.setStop("crashed-car-lane-zero.1", "left-exit-blockage", 18.5, 0, 3600)
    traci.vehicle.setStop("crashed-car-lane-one.0", "left-exit-blockage", 26.5, 1, 3600)
    traci.vehicle.setStop("crashed-car-lane-one.1", "left-exit-blockage", 18.5, 1, 3610)
    
def collisionFlowCorrection(files, vehiclesTypes):
    for j in range(0, len(files)):
        mydoc = minidom.parse(files[j])
        routes = mydoc.getElementsByTagName('route')
        vehicles = mydoc.getElementsByTagName('vehicle')
        for i in range(0, len(routes)):
            
            if(routes[i].getAttribute("edges").startswith("left-short-approaching")):
                route = "left-long-approaching " + routes[i].getAttribute("edges")
                routes[i].setAttribute("edges", route)

            if(routes[i].getAttribute("edges").endswith("left-short-approaching")):
                result = random.randint(0, 2)
                if result == 0:
                    route = routes[i].getAttribute("edges") + " top-exit"
                    routes[i].setAttribute("edges", route)
                elif result == 1:
                    route = routes[i].getAttribute("edges") + " right-exit"
                    routes[i].setAttribute("edges", route)
                else:
                    route = routes[i].getAttribute("edges") + " bottom-exit"
                    routes[i].setAttribute("edges", route)
                

            if(routes[i].getAttribute("edges").startswith("left-exit-blockage")):
                result = random.randint(0, 2)
                if result == 0:
                    route = "top-approaching " + routes[i].getAttribute("edges")
                    routes[i].setAttribute("edges", route)
                elif result == 1:
                    route = "right-approaching " + routes[i].getAttribute("edges")
                    routes[i].setAttribute("edges", route)
                else:
                    route = "bottom-approaching " + routes[i].getAttribute("edges")
                    routes[i].setAttribute("edges", route)

            if(routes[i].getAttribute("edges").endswith("left-exit-blockage")):
                route = routes[i].getAttribute("edges") + " left-exit"
                routes[i].setAttribute("edges", route)
                

            if(routes[i].getAttribute("edges") == "left-long-approaching left-short-approaching top-exit"):
                temp = vehiclesTypes[j] + "-Left-"
                vehicles[i].setAttribute("type", temp)
            
            if vehiclesTypes[0] == "L0-HDV":
                if(routes[i].getAttribute("edges") == "left-long-approaching left-short-approaching right-exit"):
                    temp = vehiclesTypes[j] + "-Straight-"
                    vehicles[i].setAttribute("type", temp)
            
            if vehiclesTypes[0] != "L0-HDV":
                if(routes[i].getAttribute("edges") == "left-long-approaching left-short-approaching bottom-exit"):
                    temp = vehiclesTypes[j] + "-Right-"
                    vehicles[i].setAttribute("type", temp)
            
                    
        with open(files[j], "w") as fs:
            fs.write(mydoc.toxml()) 
            fs.close()  

############### Caller Functions ###############
def allowingAccessToRightLaneCollisionBaseline(minorWaitLengthBeforeAction, accessToRightLaneLastDetected):
    accessToRightLaneLastDetected[0] = allowingAccessToRightLaneLateCollision(accessToRightLaneLastDetected[0], minorWaitLengthBeforeAction)
    return accessToRightLaneLastDetected

def leftExitAfterIntersectionCollisionTMSBaseline(standardRightTopBottomLastVehicleDetected, stuckInLeftExitlastVehicleDetected, leftExitUpwardToClastVehicleDetected, DETECTEDTOCTIME, vehiclesApproachingClosure, seenInLeftExit):
    standardRightTopBottomLastVehicleDetected, vehiclesApproachingClosure = standardHandlingRightTopBottom(standardRightTopBottomLastVehicleDetected, DETECTEDTOCTIME, vehiclesApproachingClosure)
    stuckInLeftExitlastVehicleDetected, seenInLeftExit = standardSituationHandlingInLeftExit(stuckInLeftExitlastVehicleDetected, seenInLeftExit)  
    leftExitUpwardToClastVehicleDetected, seenInLeftExit = upwardToCDownstream(leftExitUpwardToClastVehicleDetected, seenInLeftExit)      
    return standardRightTopBottomLastVehicleDetected, stuckInLeftExitlastVehicleDetected, leftExitUpwardToClastVehicleDetected, vehiclesApproachingClosure, seenInLeftExit

def leftExitAfterIntersectionCollisionTMS(TMSRightTopBottomlastVehicleDetected, standardRightTopBottomLastVehicleDetected, stuckInLeftExitlastVehicleDetected, leftExitUpwardToClastVehicleDetected, DETECTEDTOCTIME, vehiclesApproachingClosure, seenInLeftExit):
    TMSRightTopBottomlastVehicleDetected, vehiclesApproachingClosure = TMSRightTopBottom(TMSRightTopBottomlastVehicleDetected, vehiclesApproachingClosure)
    standardRightTopBottomLastVehicleDetected, vehiclesApproachingClosure = standardHandlingRightTopBottom(standardRightTopBottomLastVehicleDetected, DETECTEDTOCTIME, vehiclesApproachingClosure)
    stuckInLeftExitlastVehicleDetected, seenInLeftExit = standardSituationHandlingInLeftExit(stuckInLeftExitlastVehicleDetected, seenInLeftExit)  
    
    leftExitUpwardToClastVehicleDetected, seenInLeftExit = upwardToCDownstream(leftExitUpwardToClastVehicleDetected, seenInLeftExit)      
     
    return TMSRightTopBottomlastVehicleDetected, standardRightTopBottomLastVehicleDetected, stuckInLeftExitlastVehicleDetected, leftExitUpwardToClastVehicleDetected, vehiclesApproachingClosure, seenInLeftExit

def majorDelayDetectionHandlingCollision(majorDelayDetectionLastDetected, vehiclesApproachingClosure, vehiclesThatTORed, delayBeforeReRoute, ToCLeadTime, step, NUMBEROFVEHICLESREROUTED):
    majorDelayDetectionLastDetected, vehiclesApproachingClosure = majorDelayVehicleDetection(majorDelayDetectionLastDetected, vehiclesApproachingClosure)
    vehiclesApproachingClosure, vehiclesThatTORed, NUMBEROFVEHICLESREROUTED = collisionDetectingMajorDelay(vehiclesApproachingClosure, vehiclesThatTORed, delayBeforeReRoute, ToCLeadTime, step, NUMBEROFVEHICLESREROUTED)
    return majorDelayDetectionLastDetected, vehiclesApproachingClosure, vehiclesThatTORed, NUMBEROFVEHICLESREROUTED

def allowingAccessToRightLaneCollision(minorWaitLengthBeforeAction, accessToRightLaneLastDetected):
    accessToRightLaneLastDetected = allowingAccessToRightLaneTMS(accessToRightLaneLastDetected)
    accessToRightLaneLastDetected[2] = allowingAccessToRightLaneLateCollision(accessToRightLaneLastDetected[2], minorWaitLengthBeforeAction)
    return accessToRightLaneLastDetected

############### Left Exit ###############
def TMSRightTopBottom(lastVehicleDetected, vehiclesApproachingClosure):
    detectors = ["TMS-top-approaching_0", "TMS-top-approaching_1", "TMS-top-approaching_2",
                "TMS-right-approaching_0", "TMS-right-approaching_1", "TMS-right-approaching_2", 
                "TMS-bottom-approaching_0", "TMS-bottom-approaching_1", "TMS-bottom-approaching_2"]
    count = 0
    for detector in detectors:
        det_vehs = traci.inductionloop.getLastStepVehicleIDs(detector)
        for veh in det_vehs:
            if(veh != lastVehicleDetected[count]):
                lastVehicleDetected[count] = veh
                route = traci.vehicle.getRoute(veh)
                target = route[len(route) - 1]
                vehicleType = (traci.vehicle.getTypeID(veh)).split('-')[1]
                receivedTMSResult = random.randint(0, 99)
                if (target == "left-exit" and vehicleType == "CV" and receivedTMSResult < 66):
                    # print("Got TMS", veh)
                    traci.vehicle.setParameter(veh, "device.toc.dynamicToCThreshold", 0)                        
        count = count + 1
    return lastVehicleDetected, vehiclesApproachingClosure

def standardHandlingRightTopBottom(lastVehicleDetected, DETECTEDTOCTIME, vehiclesApproachingClosure):
    # detectors = ["close-top-approaching_0", "close-right-approaching_1", "close-bottom-approaching_2"]
    detectors = ["close-top-approaching_0", "close-top-approaching_1", "close-top-approaching_2",
                "close-right-approaching_0", "close-right-approaching_1", "close-right-approaching_2", 
                "close-bottom-approaching_0", "close-bottom-approaching_1", "close-bottom-approaching_2",
                ]
    # edges = ["top", "right", "bottom"]
    count = 0
    for det in detectors:
        det_vehs = traci.inductionloop.getLastStepVehicleIDs(det)
        for veh in det_vehs:
            if(veh != lastVehicleDetected[count]):
                lastVehicleDetected[count] = veh
                route = traci.vehicle.getRoute(veh)
                target = route[len(route) - 1]
                if (traci.vehicle.getTypeID(veh)[:2] == "L4" or traci.vehicle.getTypeID(veh)[:2] == "L2"):
                    
                    if target == "left-exit" and traci.vehicle.getParameter(veh, "device.toc.dynamicToCThreshold") != "0.00":
                        # print("HEre - 1", veh) 
                        # print("HEre", traci.vehicle.getParameter(veh, "device.toc.dynamicToCThreshold")) 
                        detectedSituation = random.randint(0, 99)
                        if(detectedSituation < 25 ):
                            ## Detected the situation and decided best solution was to go for it
                            # print("Going for it", veh)
                            traci.vehicle.setParameter(veh, "device.toc.dynamicToCThreshold", 0)
                        # elif detectedSituation < 50:
                            ## Detected situation and decided best solution was to re-route
                            # print("Re-Routing", veh)
                            # laneID = traci.vehicle.getLaneID(veh).split('-')
                            # directionResult = random.randint(0,1) 
                            # if(directionResult == 0):
                                # traci.vehicle.setRoute(veh, collisionReRouteClockWiseFirst(laneID[0]))
                                # vehiclesApproachingClosure.remove(veh)
                            # else:
                                # traci.vehicle.setRoute(veh, collisionReRouteClockWiseSecond(laneID[0]))
                                # vehiclesApproachingClosure.remove(veh)
                            # if veh in vehiclesApproachingClosure:
                                # vehiclesApproachingClosure.remove(veh)
                        else:
                            # print("ToC", veh)
                            traci.vehicle.requestToC(veh, DETECTEDTOCTIME)      
                            traci.vehicle.updateBestLanes(veh)
        count = count + 1
    return lastVehicleDetected, vehiclesApproachingClosure

def standardSituationHandlingInLeftExit(stuckInLeftExitlastVehicleDetected, seenInLeftExit):
    det_vehs = traci.inductionloop.getLastStepVehicleIDs("left-exit_0")
    for veh in det_vehs:
        # print("traci.vehicle.couldChangeLane(veh, 1)", traci.vehicle.couldChangeLane(veh, 1))
        # print("veh", veh)
        # traci.vehicle.setStop(veh, "left-exit-blockage", 50, 0, 0.1)
        
        laneID = traci.vehicle.getLaneID(veh).split('-')
        # print("laneID = traci.vehicle.getLaneID(veh).split('-')", laneID)
        traci.vehicle.changeLane(veh, 1, 0.1)
        
        if (traci.vehicle.getVehicleClass(veh) != "emergency"):  
            # print("veh 0", veh) 
            seenInLeftExit.append(veh)
            traci.vehicle.setVehicleClass(veh, "emergency")
            # if (traci.vehicle.getTypeID(veh)[:2] == "L4" or traci.vehicle.getTypeID(veh)[:2] == "L2"):
                # traci.vehicle.setParameter(veh, "device.toc.dynamicToCThreshold", 0)
        stuckInLeftExitlastVehicleDetected[0] = veh
                
    det_vehs = traci.inductionloop.getLastStepVehicleIDs("left-exit_1")
    for veh in det_vehs:
        # if veh != stuckInLeftExitlastVehicleDetected[1]:
       
        if(traci.vehicle.getVehicleClass(veh) != "emergency"):
            # print("veh 1", veh)
            seenInLeftExit.append(veh)
            traci.vehicle.setVehicleClass(veh, "emergency")
            # if (traci.vehicle.getTypeID(veh)[:2] == "L4" or traci.vehicle.getTypeID(veh)[:2] == "L2"):
                # traci.vehicle.setParameter(veh, "device.toc.dynamicToCThreshold", 0)
        stuckInLeftExitlastVehicleDetected[1] = veh
    return stuckInLeftExitlastVehicleDetected, seenInLeftExit

def upwardToCDownstream(lastVehicleDetected, seenInLeftExit):
    decectorsLaterInLeftExit = ["left-exit_2", "left-exit_3"]
    count = 0
    for det in decectorsLaterInLeftExit:
        det_vehs = traci.inductionloop.getLastStepVehicleIDs(det)
        for veh in det_vehs:
            if lastVehicleDetected[count] != veh:
                upwardToCResult = random.randint(0, 99)
                # print("veh", veh)
                # print("traci.vehicle.getTypeID(veh)", traci.vehicle.getTypeID(veh))
                if (traci.vehicle.getTypeID(veh)[:2] == "L0" and upwardToCResult < 75 and veh[:2] != "L0"):
                    # print("upward ToC", veh)
                    traci.vehicle.requestToC(veh, -1)
                elif veh[:2] == "L0":
                    # print("HDV Class change", veh)
                    traci.vehicle.setVehicleClass(veh, "passenger")
                # vehicleType = (traci.vehicle.getTypeID(veh)).split('-')[1]
                # print("traci.vehicle.getTypeID(veh)[:2]", traci.vehicle.getTypeID(veh))
                if (traci.vehicle.getTypeID(veh)[:2] == "L4" or traci.vehicle.getTypeID(veh)[:2] == "L2"):
                    # print("CAV Class change", veh)
                    traci.vehicle.setVehicleClass(veh, "custom1")
                    if (traci.vehicle.getParameter(veh, "device.toc.dynamicToCThreshold") == 0):
                        traci.vehicle.setParameter(veh, "device.toc.dynamicToCThreshold", 11)
                
                temp = veh in seenInLeftExit
                if temp == True:
                    # print("OUT")
                    seenInLeftExit.remove(veh)
                lastVehicleDetected[count] = veh
        count = count + 1
    return lastVehicleDetected, seenInLeftExit

def majorDelayVehicleDetection(lastVehicleDetected, vehiclesApproachingClosure):
    detectors = ["major-delay-top-approaching_0", "major-delay-top-approaching_1", "major-delay-top-approaching_2", 
                "major-delay-right-approaching_0" , "major-delay-right-approaching_1" , "major-delay-right-approaching_2" , 
                "major-delay-bottom-approaching_0", "major-delay-bottom-approaching_1", "major-delay-bottom-approaching_2"]
    count = 0
    for det in detectors:
        det_vehs = traci.inductionloop.getLastStepVehicleIDs(det)
        for veh in det_vehs:
            if veh != lastVehicleDetected[count]:
                temp1 = traci.vehicle.getRoute(veh)[len(traci.vehicle.getRoute(veh))-1]
                temp2 = veh in vehiclesApproachingClosure
                if ((temp1 == "left-exit") and (temp2 == False)):
                    vehiclesApproachingClosure.append(veh)
                lastVehicleDetected[count] = veh
        count = count + 1
    return lastVehicleDetected, vehiclesApproachingClosure

def collisionDetectingMajorDelay(vehiclesApproachingClosure, vehiclesThatTORed, delayBeforeReRoute, ToCLeadTime, step, NUMBEROFVEHICLESREROUTED):
    if (step%6 == 0):
        for vehicle in vehiclesApproachingClosure:
            target = traci.vehicle.getRoute(vehicle)[len(traci.vehicle.getRoute(vehicle))-1]
            laneID = traci.vehicle.getLaneID(vehicle).split('-')
            # print("laneID", laneID)
            
            if(traci.vehicle.getAccumulatedWaitingTime(vehicle) > 140 and target == "left-exit"):
                # print("IN IF", vehicle)
                rerouteResult = random.randint(0,99)
                if rerouteResult < 40:
                    NUMBEROFVEHICLESREROUTED = NUMBEROFVEHICLESREROUTED + 1
                    if laneID[0] != "right":
                        # print("OTHER", vehicle)
                        traci.vehicle.setRoute(vehicle, collisionReRouteClockWiseSecond(laneID[0]))
                    else:
                        if laneID[1] == "approaching_1":
                            directionResult = random.randint(0,1) 
                            if(directionResult == 0):
                                # print("In right 1", vehicle)
                                traci.vehicle.setRoute(vehicle, collisionReRouteClockWiseFirst(laneID[0]))
                            else:
                                traci.vehicle.setRoute(vehicle, collisionReRouteClockWiseSecond(laneID[0]))
                                # print("In right 1.5", vehicle)
                        elif laneID[1] == "approaching_0":
                            # print("In right 0", vehicle)
                            traci.vehicle.setRoute(vehicle, collisionReRouteClockWiseSecond(laneID[0]))
                        elif laneID[1] == "approaching_2":
                            traci.vehicle.setRoute(vehicle, collisionReRouteClockWiseFirst(laneID[0]))
                
                vehiclesApproachingClosure.remove(vehicle)

    return vehiclesApproachingClosure, vehiclesThatTORed, NUMBEROFVEHICLESREROUTED
            
def reRoutingVehiclesCollision(veh, target, vehiclesApproachingClosure, vehiclesThatTORed, ToCLeadTime, NUMBEROFVEHICLESREROUTED):
    shouldBeRemoved = False
    tocResult = random.randint(0, 99) ## NEED TO CONSIDER THIS PROBABILITY MORE
    temp = veh in vehiclesThatTORed
    if(tocResult < 60 and temp == False and (traci.vehicle.getTypeID(veh)[:2] == "L4" or traci.vehicle.getTypeID(veh)[:2] == "L2")):
        # print("ToC due to delay", veh)
        traci.vehicle.requestToC(veh, ToCLeadTime)
        vehiclesThatTORed.append(veh)
        # traci.vehicle.setParameter(veh, "accumulatedWaitingTime", 20)   # (veh)
        # print("traci.vehicle.getAccumulatedWaitingTime(veh)", traci.vehicle.getAccumulatedWaitingTime(veh))
        shouldBeRemoved = True
    
    rerouteResult = random.randint(0, 99) ## NEED TO CONSIDER THIS PROBABILITY MORE
    if(rerouteResult < 60 and target == "left-exit"):
        # print("Rerouted due to delay", veh)
        laneID = traci.vehicle.getLaneID(veh).split('-')
        directionResult = random.randint(0,1) 
        if(directionResult == 0):
            traci.vehicle.setRoute(veh, collisionReRouteClockWiseFirst(laneID[0]))
        else:
            traci.vehicle.setRoute(veh, collisionReRouteClockWiseSecond(laneID[0]))
        NUMBEROFVEHICLESREROUTED = NUMBEROFVEHICLESREROUTED + 1
        shouldBeRemoved = True
        traci.vehicle.updateBestLanes(veh)

    if shouldBeRemoved == True:
        vehiclesApproachingClosure.remove(veh)

    return vehiclesApproachingClosure, vehiclesThatTORed, NUMBEROFVEHICLESREROUTED

def clearingLeftLaneOfCVs(lastVehicleDetected):
    detectors = ["TMS-left-long-approaching_0", "TMS-left-long-approaching_1", "TMS-left-long-approaching_2"]
    count = 0
    for det in detectors:
        det_vehs = traci.inductionloop.getLastStepVehicleIDs(det)
        for veh in det_vehs:
            if lastVehicleDetected[count] != veh:
                vehicleType = (traci.vehicle.getTypeID(veh)).split('-')[1]
                if traci.vehicle.getVehicleClass(veh) == "custom2" and vehicleType == "CV":
                    receivedTMSResult = random.randint(0, 99)
                    if receivedTMSResult < 99:
                        # print("TMS", veh)
                        traci.vehicle.setParameter(veh, "device.toc.dynamicToCThreshold", 0)
                        traci.vehicle.setVehicleClass(veh, "custom1")
                        traci.vehicle.updateBestLanes(veh)
                lastVehicleDetected[count] = veh
        count = count + 1

    return lastVehicleDetected

def monitoringSeenInLeftExit(seenInLeftExit):
    # if len(seenInLeftExit) != 0:
    #     print("seenInLeftExit", seenInLeftExit)
    for vehicle in seenInLeftExit:
        temp1 = vehicle in traci.vehicle.getIDList()
        if temp1 == False:
            # print("seenInLeftExit 1", seenInLeftExit)
            seenInLeftExit.remove(vehicle)
        else:
            if(traci.vehicle.getVehicleClass(vehicle) != "emergency"):
                # print("changing its class", vehicle)
                traci.vehicle.setVehicleClass(vehicle, "emergency")
            laneID = traci.vehicle.getLaneID(vehicle).split('-')
            # print("laneID[len(laneID)-1]", laneID[len(laneID)-1])
            # print("traci.vehicle.getPosition(veh)", traci.vehicle.getPosition(vehicle)[0])
            if(traci.vehicle.getPosition(vehicle)[0] > 473 and laneID[len(laneID)-1] == "blockage_0"):
                traci.vehicle.changeLane(vehicle, 1, 0.1)
                # print("veh", vehicle)
    
    return seenInLeftExit

def allowingAccessToRightLaneLateCollision(lastVehicleDetected, delayRealisation):
    # det_vehs = traci.inductionloop.getLastStepVehicleIDs("allowingRightLaneAccessLate")
    # for veh in det_vehs:
    #     if lastVehicleDetected != veh:
    #         route = traci.vehicle.getRoute(veh)
    #         target = route[len(route) - 1]
    #         vehicleClass = traci.vehicle.getVehicleClass(veh)
    #         if target == "right-exit" and traci.vehicle.getAccumulatedWaitingTime(veh) >= delayRealisation and vehicleClass != "passenger":
    #             vehicleType = (traci.vehicle.getTypeID(veh)).split('-')[1]
    #             scenarioRecognitionResult = random.randint(0, 99) ## CONSIDER
    #             if vehicleType == "HDV" and scenarioRecognitionResult < 80:
    #                 # print("GOT THE MESSAGE", veh)
    #                 traci.vehicle.setVehicleClass(veh, "passenger")
    #                 traci.vehicle.updateBestLanes(veh)
    #             # else:
    #             #     print("JUST MISSED THE MESSAGE", veh)
    #     lastVehicleDetected = veh
    return lastVehicleDetected

def collisionReRouting(lastVehicleDetected):
    detectors = ["ReRoute-top-approaching_0", "ReRoute-top-approaching_1", "ReRoute-top-approaching_2",
                "ReRoute-right-approaching_0", "ReRoute-right-approaching_1", "ReRoute-right-approaching_2", 
                "ReRoute-bottom-approaching_0", "ReRoute-bottom-approaching_1", "ReRoute-bottom-approaching_2"]
    count = 0
    for detector in detectors:
        det_vehs = traci.inductionloop.getLastStepVehicleIDs(detector)
        for veh in det_vehs:
            if(veh != lastVehicleDetected[count]):
                if target == "left-exit":
                    print("IN IF")
                    rerouteResult = random.randint(0,99)
                    if traci.vehicle.getAccumulatedWaitingTime(veh) > 120 and rerouteResult < 40:
                        laneID = traci.vehicle.getLaneID(veh).split('-')
                        if detector == "TMS-right-approaching_1":
                            directionResult = random.randint(0,1) 
                            if(directionResult == 0):
                                print("In right 1", veh)
                                traci.vehicle.setRoute(veh, collisionReRouteClockWiseFirst(laneID[0]))
                            else:
                                traci.vehicle.setRoute(veh, collisionReRouteClockWiseSecond(laneID[0]))
                                print("In right 1.5", veh)
                        elif detector == "TMS-right-approaching_0":
                            print("In right 0", veh)
                            traci.vehicle.setRoute(veh, collisionReRouteClockWiseSecond(laneID[0]))
                        elif detector == "TMS-right-approaching_2":
                            traci.vehicle.setRoute(veh, collisionReRouteClockWiseFirst(laneID[0]))
                            print("In right 2", veh)
                        else:
                            print("In Other", veh)
                            traci.vehicle.setRoute(veh, collisionReRouteClockWiseSecond(laneID[0]))