import random
import os
import numpy as np
import sys
import optparse
import traci
from xml.dom import minidom

sys.path.append('c:/Users/david/OneDrive/Fifth Year/Final Year Project/SUMO/Simulation Stuff/Final-Year-Project')

from generalFunctions import (removeOldToC, collisionReRouteClockWiseFirst, collisionReRouteClockWiseSecond, baselineAlterOutputFiles, settingUpVehicles, 
                                removeVehiclesThatPassCenter, stoppingCrashedVehicles, leftExitAfterIntersectionCollisionTMSBaseline, 
                                majorDelayDetectionHandlingCollision, collisionFlowCorrection, clearingLeftLaneOfCVs, monitoringSeenInLeftExit, 
                                allowingAccessToRightLaneCollisionBaseline, vehiclePenetrationRates3,TMSAlterOutputFiles)

def TMS():
    print("Running Baseline P3")
    TMSRightTopBottomlastVehicleDetected = ["N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A"]
    standardRightTopBottomLastVehicleDetected = ["N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A"]
    stuckInLeftExitlastVehicleDetected = ["N/A", "N/A"]
    leftExitUpwardToClastVehicleDetected = ["N/A", "N/A"]
    majorDelayLastVehicleDetected = ["N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A"]
    clearingCVsLastVehicleDetected = ["N/A", "N/A", "N/A"]
    seenInLeftExit = []
    accessToRightLaneLastDetected = ["N/A", "N/A"]
    
    step = 0
    vehiclesApproachingClosure = []
    vehiclesThatTORed = []
    delayBeforeReRoute = 80 ### Needs to be considered
    TIMETOPERFORMDELAYTOC = 30 ### Needs to be considered
    DETECTEDTOCTIME = 5 ### Needs to be considered
    NUMBEROFVEHICLESREROUTED = 0
    minorWaitLengthBeforeAction = 30
    
    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()
        if step == 1000:
            stoppingCrashedVehicles()

        if step > 1200 and step < 42000:
            if step%3 == 0:
                # vehiclesApproachingClosure = removeVehiclesThatPassCenter(vehiclesApproachingClosure)
                # vehiclesThatTORed = removeOldToC(vehiclesThatTORed)
                seenInLeftExit = monitoringSeenInLeftExit(seenInLeftExit)
                
                standardRightTopBottomLastVehicleDetected, stuckInLeftExitlastVehicleDetected, leftExitUpwardToClastVehicleDetected, vehiclesApproachingClosure, seenInLeftExit = leftExitAfterIntersectionCollisionTMSBaseline(standardRightTopBottomLastVehicleDetected, 
                stuckInLeftExitlastVehicleDetected, leftExitUpwardToClastVehicleDetected, DETECTEDTOCTIME, vehiclesApproachingClosure, seenInLeftExit)
                
                # majorDelayLastVehicleDetected, vehiclesApproachingClosure, vehiclesThatTORed, NUMBEROFVEHICLESREROUTED = majorDelayDetectionHandlingCollision(majorDelayLastVehicleDetected, vehiclesApproachingClosure, 
                # vehiclesThatTORed, delayBeforeReRoute, TIMETOPERFORMDELAYTOC, step, NUMBEROFVEHICLESREROUTED)
                # clearingCVsLastVehicleDetected = clearingLeftLaneOfCVs(clearingCVsLastVehicleDetected)
                accessToRightLaneLastDetected = allowingAccessToRightLaneCollisionBaseline(minorWaitLengthBeforeAction, accessToRightLaneLastDetected)
        step += 1
    # print("Number of Vehicles ReRouted", NUMBEROFVEHICLESREROUTED)
    traci.close(False)
    sys.stdout.flush()
    

def collisionBaselinePenetration3(sumoBinary, LOS, ITERATION):
    print("----------------------------------------")
    print("HERE P1")
    files = ['Collision/BaselinePenetration3/Route-Files/L4-CV-Route.rou.xml', 'Collision/BaselinePenetration3/Route-Files/L4-AV-Route.rou.xml', 
            'Collision/BaselinePenetration3/Route-Files/L2-CV-Route.rou.xml', 'Collision/BaselinePenetration3/Route-Files/L2-AV-Route.rou.xml',
            'Collision/BaselinePenetration3/Route-Files/L0-HDV-Route.rou.xml']
    vehicleTypes = ["L4-CV", "L4-AV", "L2-CV", "L2-AV", "L0-HDV"]
    rate = vehiclePenetrationRates3(LOS)
    settingUpVehicles("Collision", "\BaselinePenetration3", LOS, rate)
    collisionFlowCorrection(['Collision/BaselinePenetration3/Route-Files/L4-CV-Route.rou.xml'], ["L4-CV"])
    collisionFlowCorrection(['Collision/BaselinePenetration3/Route-Files/L4-AV-Route.rou.xml'], ["L4-AV"])
    collisionFlowCorrection(['Collision/BaselinePenetration3/Route-Files/L2-CV-Route.rou.xml'], ["L2-CV"])
    collisionFlowCorrection(['Collision/BaselinePenetration3/Route-Files/L2-AV-Route.rou.xml'], ["L2-AV"])
    collisionFlowCorrection(['Collision/BaselinePenetration3/Route-Files/L0-HDV-Route.rou.xml'], ["L0-HDV"])
    
    # #traci starts sumo as a subprocess and then this script connects and runs
    traci.start([sumoBinary, "-c", "Collision\BaselinePenetration3\CollisionBaselineTMSPenetration3.sumocfg",
                "--tripinfo-output", "Collision\BaselinePenetration3\Output-Files\TripInfo.xml", "--ignore-route-errors",
                "--device.emissions.probability", "1", "--waiting-time-memory", "300", "-S",  "-W"])

    TMS()
    baselineAlterOutputFiles("Collision", "Penetration3", LOS, ITERATION, vehicleTypes)
