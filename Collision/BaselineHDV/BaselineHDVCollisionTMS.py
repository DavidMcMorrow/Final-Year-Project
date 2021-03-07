import random
import os
import numpy as np
import sys
import optparse
import traci
from xml.dom import minidom

def settingUpVehicles(LOS):
    with open('Collision\BaselineHDV\PreparingVehicleModels\How to use.txt') as f:
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

def stoppingCrashedVehicles():
    traci.vehicle.setStop("crashed-car-lane-zero.0", "left-exit", 25.5, 0, 4500)
    traci.vehicle.setStop("crashed-car-lane-zero.1", "left-exit", 17.5, 0, 4500)
    traci.vehicle.setStop("crashed-car-lane-one.0", "left-exit", 25.5, 1, 4500)
    traci.vehicle.setStop("crashed-car-lane-one.1", "left-exit", 17.5, 1, 4500)

def leftExit():
    det_vehs = traci.inductionloop.getLastStepVehicleIDs("left-exit_0")
    for veh in det_vehs:
        traci.vehicle.changeLane(veh, 1, 0.1)
        if(traci.vehicle.getVehicleClass(veh) == "passenger"):   
            traci.vehicle.setVehicleClass(veh, "emergency")

    det_vehs = traci.inductionloop.getLastStepVehicleIDs("left-exit_1")
    for veh in det_vehs:
        if(traci.vehicle.getVehicleClass(veh) == "passenger"):
            traci.vehicle.setVehicleClass(veh, "emergency")

    decectorsLaterInLeftExit = ["left-exit_2", "left-exit_3"]
    for det in decectorsLaterInLeftExit:
        det_vehs = traci.inductionloop.getLastStepVehicleIDs(det)
        for veh in det_vehs:
            if(traci.vehicle.getVehicleClass(veh) == "passenger"):
                traci.vehicle.setVehicleClass(veh, "custom1")

def reRouteClockWiseFirst(edge):
    newRoute = []
    if(edge == "top"):
        newRoute = ["top-approaching", "bottom-exit"]
    elif(edge == "right"):
        newRoute = ["right-approaching", "bottom-exit"]
    elif(edge == "bottom"):
        newRoute = ["bottom-approaching", "top-exit"]
    return newRoute

def reRouteClockWiseSecond(edge):
    newRoute = []
    if(edge == "top"):
        newRoute = ["top-approaching", "bottom-exit"]
    elif(edge == "right"):
        newRoute = ["right-approaching", "top-exit"]
    elif(edge == "bottom"):
        newRoute = ["bottom-approaching", "top-exit"]
    return newRoute


def closeRightTopBottom(vehiclesApproachingClosure):
    detectors = ["close-top-approaching_0", "close-right-approaching_1", "close-bottom-approaching_2"]
    edges = ["top", "right", "bottom"]
    for i in range(0, len(detectors)-1):
        det_vehs = traci.inductionloop.getLastStepVehicleIDs(detectors[i])
        for veh in det_vehs:
            vehiclesApproachingClosure = reRoutingVehicles(veh, edges[i], vehiclesApproachingClosure)
    return vehiclesApproachingClosure  


def farRightTopBottom(delayBeforeReoute, vehiclesApproachingClosure):
    detectors = ["far-top-approaching_0", "far-top-approaching_1", "far-top-approaching_2", 
                "far-right-approaching_0", "far-right-approaching_1", "far-right-approaching_2", 
                "far-bottom-approaching_0", "far-bottom-approaching_1", "far-bottom-approaching_2"]
    edges = ["top", "right", "bottom"]
    
    for det in detectors:
        det_vehs = traci.inductionloop.getLastStepVehicleIDs(det)
        for veh in det_vehs:
            temp1 = traci.vehicle.getRoute(veh)[len(traci.vehicle.getRoute(veh))-1]
            temp2 = veh in vehiclesApproachingClosure
            if ((temp1 ==  "left-exit") and (temp2 == False)):
                vehiclesApproachingClosure.append(veh)
       
    for veh in vehiclesApproachingClosure:
        currentEdge = traci.vehicle.getLaneID(veh).split("-")
        if traci.vehicle.getAccumulatedWaitingTime(veh) > delayBeforeReoute:
            print("WAITED TOO LONG", veh)
            vehiclesApproachingClosure = reRoutingVehicles(veh, currentEdge[0], vehiclesApproachingClosure)
    return vehiclesApproachingClosure

def TMS():
    print("Running Baseline")
    delayBeforeReoute = 200 ### Needs to be considered
    vehiclesApproachingClosure = []
    step = 0
    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()
        vehiclesApproachingClosure = removeVehiclesThatPassCenter(vehiclesApproachingClosure)
        if step == 1000:
            stoppingCrashedVehicles()

        if step > 1200:
            if step%3 == 0:
                leftExit()
                vehiclesApproachingClosure = closeRightTopBottom(vehiclesApproachingClosure)
                vehiclesApproachingClosure = farRightTopBottom(delayBeforeReoute, vehiclesApproachingClosure)
                
        step += 1

    traci.close(False)
    sys.stdout.flush()

def alterOutputFilesNames(LOS, ITERATION):
    safetyFile = "Collision\BaselineHDV\Output-Files\LOS-" + LOS + "\SSM-HDV-"+ str(ITERATION) + ".xml"
    tripFile = "Collision\BaselineHDV\Output-Files\LOS-" + LOS + "\Trips-HDV-"+ str(ITERATION) + ".xml"
    
    with open("Collision\BaselineHDV\Output-Files\SSM-HDV.xml", 'r') as firstFile:
        with open(safetyFile, 'w') as secondFile:
            for line in firstFile:
                secondFile.write(line)

    with open("Collision\BaselineHDV\Output-Files\CollisionTripInfo.xml", 'r') as firstFile:
        with open(tripFile, 'w') as secondFile:
            for line in firstFile:
                secondFile.write(line)

def collisionBaselineHDVTMS(sumoBinary, LOS, ITERATION):
    print("here")
    settingUpVehicles(LOS)
    traci.start([sumoBinary, "-c", "Collision\BaselineHDV\CollisionIntersectionBaselineHDV.sumocfg",
                                "--tripinfo-output", "Collision\BaselineHDV\Output-Files\CollisionTripinfo.xml", "--ignore-route-errors", 
                                "--device.emissions.probability", "1", "--waiting-time-memory", "300"])

    TMS()
    alterOutputFilesNames(LOS, ITERATION)

def reRoutingVehicles(veh, edge, vehiclesApproachingClosure):
    rerouteResult = random.randint(0,3) ## NEEDS TO BE CONSIDERED
    if traci.vehicle.getRoute(veh)[1] == "left-exit":
        if(rerouteResult == 0):
            directionResult = random.randint(0,1)
            if(directionResult == 0):
                traci.vehicle.setRoute(veh, reRouteClockWiseFirst(edge))
                vehiclesApproachingClosure = removeVehiclesThatAreReRouted(vehiclesApproachingClosure, veh)
            else:
                traci.vehicle.setRoute(veh, reRouteClockWiseSecond(edge))
                vehiclesApproachingClosure = removeVehiclesThatAreReRouted(vehiclesApproachingClosure, veh)
    return vehiclesApproachingClosure

def removeVehiclesThatPassCenter(vehiclesApproachingClosure):
    count = 0
    for vehicle in vehiclesApproachingClosure:
        temp = traci.vehicle.getLaneID(vehicle)[:7]
        if(temp == ":center"):
            vehiclesApproachingClosure.pop(count)
        count = count + 1
    return vehiclesApproachingClosure

def removeVehiclesThatAreReRouted(vehiclesApproachingClosure, veh):
    for waitingVehicle in vehiclesApproachingClosure:
        if(waitingVehicle == veh):
            vehiclesApproachingClosure.remove(waitingVehicle)
    return vehiclesApproachingClosure

