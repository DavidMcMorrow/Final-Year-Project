import random
import os
import numpy as np
import sys
import optparse
import traci
from xml.dom import minidom

sys.path.append('c:/Users/david/OneDrive/Fifth Year/Final Year Project/SUMO/Simulation Stuff/Final-Year-Project')

from generalFunctions import (removeOldToC, collisionReRouteClockWiseFirst, collisionReRouteClockWiseSecond, baselineAlterOutputFiles, settingUpVehicles, 
                                removeVehiclesThatPassCenter, stoppingCrashedVehicles, leftExitAfterIntersectionCollisionTMS, majorDelayDetection)

# def closeRightTopBottom(vehiclesApproachingClosure, vehiclesThatTORed, DETECTINGISSUE):
#     detectors = ["close-top-approaching_0", "close-right-approaching_1", "close-bottom-approaching_2"]
#     edges = ["top", "right", "bottom"]
#     for i in range(0, len(detectors)-1):
#         det_vehs = traci.inductionloop.getLastStepVehicleIDs(detectors[i])
#         for veh in det_vehs:
#             if traci.vehicle.getRoute(veh)[1] != "left-exit":
#                 vehiclesApproachingClosure, vehiclesThatTORed = reRoutingVehicles(veh, edges[i], vehiclesApproachingClosure, vehiclesThatTORed, DETECTINGISSUE)
#     return vehiclesApproachingClosure, vehiclesThatTORed

def farRightTopBottom(delayBeforeReoute, vehiclesApproachingClosure, vehiclesThatTORed, MAJOYDELAYTRIGGEREDTOC):
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
            vehiclesApproachingClosure, vehiclesThatTORed = reRoutingVehicles(veh, currentEdge[0], vehiclesApproachingClosure, vehiclesThatTORed, MAJOYDELAYTRIGGEREDTOC)
    return vehiclesApproachingClosure, vehiclesThatTORed

def TMS():
    # print("Running TMS CAV")
    # TMSRightTopBottomlastVehicleDetected = ["N/A", "N/A", "N/A", "N/A"]
    TMSRightTopBottomlastVehicleDetected = ["N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A"]
    standardRightTopBottomLastVehicleDetected = ["N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A"]
    stuckInLeftExitlastVehicleDetected = ["N/A", "N/A"]
    leftExitUpwardToClastVehicleDetected = ["N/A", "N/A"]
    majorDelayLastVehicleDetected = ["N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A"]
    
    step = 0
    vehiclesApproachingClosure = []
    vehiclesThatTORed = []
    delayBeforeReoute = 120 ### Needs to be considered
    MAJOYDELAYTRIGGEREDTOC = 20 ### Needs to be considered
    DETECTEDTOCTIME = 5 ### Needs to be considered
    
    # approachingLeftLane
    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()
        
        vehiclesApproachingClosure = removeVehiclesThatPassCenter(vehiclesApproachingClosure)
        vehiclesThatTORed = removeOldToC(vehiclesThatTORed)
        
        if step == 1000:
            stoppingCrashedVehicles()

        if step > 1200:
            if step%3 == 0:
                TMSRightTopBottomlastVehicleDetected, standardRightTopBottomLastVehicleDetected, stuckInLeftExitlastVehicleDetected, leftExitUpwardToClastVehicleDetected = leftExitAfterIntersectionCollisionTMS(TMSRightTopBottomlastVehicleDetected, 
                standardRightTopBottomLastVehicleDetected, stuckInLeftExitlastVehicleDetected, leftExitUpwardToClastVehicleDetected, DETECTEDTOCTIME)
                # vehiclesApproachingClosure, vehiclesThatTORed = closeRightTopBottom(vehiclesApproachingClosure, vehiclesThatTORed, DETECTINGISSUE)
                # vehiclesApproachingClosure, vehiclesThatTORed = farRightTopBottom(delayBeforeReoute, vehiclesApproachingClosure, vehiclesThatTORed, MAJOYDELAYTRIGGEREDTOC)

                majorDelayLastVehicleDetected = majorDelayDetection(majorDelayLastVehicleDetected)
                ##
                
        step += 1

    traci.close(False)
    sys.stdout.flush()
    

def collisionRealCAVTMS(sumoBinary, LOS, ITERATION):
    print("In collision Real TMS")
    rate = vehicleRates(LOS)
    settingUpVehicles("Collision", "\RealTMSCAV", LOS, rate)
    traci.start([sumoBinary, "-c", "Collision\RealTMSCAV\CollisionRealTMSCAV.sumocfg",
                                "--tripinfo-output", "Collision\RealTMSCAV\Output-Files\Tripinfo.xml", "--ignore-route-errors",
                                "--device.emissions.probability", "1", "--waiting-time-memory", "300"])

    TMS()
    # baselineAlterOutputFiles("Collision", "CAV", LOS, ITERATION, ["L4-CV", "HDV"])

def reRoutingVehicles(veh, edge, vehiclesApproachingClosure, vehiclesThatTORed, ToCLeadTime):
    tocResult = random.randint(0,3) ## NEED TO CONSIDER THIS PROBABILITY MORE
    temp = veh in vehiclesThatTORed
    if(tocResult != 0 and temp == False and traci.vehicle.getTypeID(veh)[:2] == "L4"):
        traci.vehicle.requestToC(veh, ToCLeadTime)
        vehiclesThatTORed.append(veh)

    rerouteResult = random.randint(0,3) ## NEED TO CONSIDER THIS PROBABILITY MORE
    if traci.vehicle.getRoute(veh)[1] == "left-exit":
        if(rerouteResult == 0):
            directionResult = random.randint(0,1) 
            if(directionResult == 0):
                traci.vehicle.setRoute(veh, collisionReRouteClockWiseFirst(edge))
                vehiclesApproachingClosure.remove(veh)
            else:
                traci.vehicle.setRoute(veh, collisionReRouteClockWiseSecond(edge))
                vehiclesApproachingClosure.remove(veh)
    return vehiclesApproachingClosure, vehiclesThatTORed

def vehicleRates(LOS):
    if LOS == "A":
        rate = [1.86]
    if LOS == "B":
        rate = [1.25]
    if LOS == "C":
        rate = [1.07]
    if LOS == "D":
        rate = [0.94]
    if LOS == "Test":
        rate = [0.7]
    return rate