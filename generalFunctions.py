import random
import os
import traci
from xml.dom import minidom

def settingUpVehicles(SCENARIO, USECASEFOLDER, LOS):
    textFileToRun = SCENARIO + USECASEFOLDER + "\PreparingVehicleModels\How to use.txt"
    with open(textFileToRun) as f:
        for line in f:
            if(line != "\n"):
                line = 'cmd /c ' + line
                if(line.find('python PreparingVehicleModels/randomTrips.py') != -1):
                    line = line.rstrip()
                    line = line + " " + str(random.randint(0,9))
                    if LOS == "A":
                        line = line + " -p " + str(1.86)
                    if LOS == "B":
                        line = line + " -p " + str(1.25)
                    if LOS == "C":
                        line = line + " -p " + str(1.07)
                    if LOS == "D":
                        line = line + " -p " + str(0.94)
                    if LOS == "Test":
                        line = line + " -p " + str(0.7)
    
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
    return newRoute

def baselineAlterOutputFiles(SCENARIO, BASELINE, LOS, ITERATION, VEHICLETYPES):
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
    print("HERERE")
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

            if(baseline == "HDV"):
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


############################## Roadworks TMS ##############################
############### Top Right Bottom Approach ###############
def roadworksTMSTopRightBottom(topBottomRightTMSDetectors, lastVehicleDetected):
    count = 0 
    for det in topBottomRightTMSDetectors:
        det_vehs = traci.inductionloop.getLastStepVehicleIDs(det)
        for veh in det_vehs:
            route = traci.vehicle.getRoute(veh)
            target = route[len(route) - 1]
            checkingPriorDetection = veh in lastVehicleDetected
            vehicleType = (traci.vehicle.getTypeID(veh)).split('-')[1]
            if traci.vehicle.getVehicleClass(veh) != "passenger" and target == "left-exit" and checkingPriorDetection == False and vehicleType == "CV":
                receivedTMSResult = random.randint(0, 99) ## CONSIDER
                if receivedTMSResult > 24:
                    traci.vehicle.setVehicleClass(veh, "passenger")
        count = count + 1
    return lastVehicleDetected

def lateVehicleIndidentDetectionTopRightBottom(topBottomRightLateDetectors, vehiclesThatTORed, ENCOUNTEREDCOLLISIONTOC, lastVehicleDetected):
    count = 0
    for det in topBottomRightLateDetectors:
        det_vehs = traci.inductionloop.getLastStepVehicleIDs(det)
        for veh in det_vehs:
            route = traci.vehicle.getRoute(veh)
            target = route[len(route) - 1]
            temp = veh in vehiclesThatTORed
            checkingPriorDetection = veh in lastVehicleDetected
            if temp == False and traci.vehicle.getVehicleClass(veh) != "passenger" and target == "left-exit" and checkingPriorDetection == False:
                result = random.randint(0, 10) ## CONSIDER
                if(result == 0):
                    traci.vehicle.setVehicleClass(veh, "passenger")
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
        # print("vehicleType", vehicleType)
        if traci.vehicle.getVehicleClass(veh) == "custom2" and vehicleType == "CV" and leftApproachingLastDetected != veh:
            receivedTMSResult = random.randint(0, 99)
            if receivedTMSResult > 75:
                # print("Did get TMS", veh)
                # traci.vehicle.setParameter(veh, "dynamicToCThreshold", 0)
                traci.vehicle.setVehicleClass(veh, "custom1")
                roadworksReRoutingLeftVehicles(veh)
            # else:
                # print("Didn't get TMS", veh)
        leftApproachingLastDetected = veh
    return leftApproachingLastDetected
                
def standardVehicleScenarioDetection(leftApproachingLastDetected):
    det_vehs = traci.inductionloop.getLastStepVehicleIDs("leftlaneStandardDetection")
    for veh in det_vehs:
        if traci.vehicle.getVehicleClass(veh) == "custom2" and leftApproachingLastDetected != veh:
            figuredOutScenario = random.randint(0,9) ## Needs to be considered
            if(figuredOutScenario < 3):
                # print("Did detect blockage", veh)
                # traci.vehicle.setParameter(veh, "dynamicToCThreshold", 0)
                traci.vehicle.setVehicleClass(veh, "custom1")
                roadworksReRoutingLeftVehicles(veh)
            # else:
                # print("Didn't detect blockage", veh)
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
            elif temp == False:
                # print("MADE TOC", veh)
                traci.vehicle.setParameter(veh, "device.toc.requestToC", ENCOUNTEREDCLOSURETOC)
                vehiclesThatTORed.append(veh)
        leftApproachingLastDetected = veh
    return leftApproachingLastDetected, vehiclesThatTORed

def allowingAccessToRightLaneTMS(lastVehicleDetected):
    det_vehs = traci.inductionloop.getLastStepVehicleIDs("allowingRightLaneAccessTMS")
    for veh in det_vehs:
        if lastVehicleDetected != veh:
            route = traci.vehicle.getRoute(veh)
            target = route[len(route) - 1]
            vehicleType = (traci.vehicle.getTypeID(veh)).split('-')[1]
            if target == "right-exit" and vehicleType == "CV":
                receivedTMSResult = random.randint(0, 99) ## CONSIDER
                if receivedTMSResult > 24:
                    print("GOT TMS", veh)
                    traci.vehicle.setVehicleClass(veh, "passenger")
                else:
                    print("MISSED TMS", veh)
        lastVehicleDetected = veh
    return lastVehicleDetected

def allowingAccessToRightLaneLate(lastVehicleDetected, delayRealisation, vehiclesThatTORed, TIMETOPERFORMDELAYTOC):
    det_vehs = traci.inductionloop.getLastStepVehicleIDs("allowingRightLaneAccessLate")
    for veh in det_vehs:
        if lastVehicleDetected != veh:
            route = traci.vehicle.getRoute(veh)
            target = route[len(route) - 1]
            vehicleClass = traci.vehicle.getVehicleClass(veh)
            if target == "right-exit" and traci.vehicle.getAccumulatedWaitingTime(veh) >= delayRealisation and vehicleClass == "passenger":
                vehicleType = (traci.vehicle.getTypeID(veh)).split('-')[1]
                scenarioRecognitionResult = random.randint(0, 99) ## CONSIDER
                if vehicleType != "HDV" and scenarioRecognitionResult < 24:
                     print("GOT TMS the second time", veh)
                     traci.vehicle.setVehicleClass(veh, "passenger")
                elif vehicleType != "HDV" and scenarioRecognitionResult > 90:
                    print("HAD TO ToC because of TMS", veh)
                    traci.vehicle.requestToC(veh, TIMETOPERFORMDELAYTOC)
                    vehiclesThatTORed.append(veh)
                elif vehicleType == "HDV" and scenarioRecognitionResult < 74:
                    traci.vehicle.setVehicleClass(veh, "passenger")
        lastVehicleDetected = veh
    return vehiclesThatTORed, lastVehicleDetected

############### ###############