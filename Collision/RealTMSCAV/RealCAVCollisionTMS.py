import random
import os
import numpy as np
import sys
import optparse
import traci
from xml.dom import minidom

sys.path.append('c:/Users/david/OneDrive/Fifth Year/Final Year Project/SUMO/Simulation Stuff/Final-Year-Project')

from generalFunctions import (removeOldToC, collisionReRouteClockWiseFirst, collisionReRouteClockWiseSecond, baselineAlterOutputFiles, settingUpVehicles, 
                                removeVehiclesThatPassCenter, stoppingCrashedVehicles, leftExitAfterIntersectionCollisionTMS, majorDelayDetectionHandlingCollision,
                                collisionFlowCorrection, clearingLeftLaneOfCVs, monitoringSeenInLeftExit, allowingAccessToRightLaneCollision, TMSAlterOutputFiles)

def TMS(REROUTINGBOOLEAN):
    # print("Running TMS CAV")
    # TMSRightTopBottomlastVehicleDetected = ["N/A", "N/A", "N/A", "N/A"]
    TMSRightTopBottomlastVehicleDetected = ["N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A"]
    standardRightTopBottomLastVehicleDetected = ["N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A"]
    stuckInLeftExitlastVehicleDetected = ["N/A", "N/A"]
    leftExitUpwardToClastVehicleDetected = ["N/A", "N/A"]
    majorDelayLastVehicleDetected = ["N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A"]
    clearingCVsLastVehicleDetected = ["N/A", "N/A", "N/A"]
    seenInLeftExit = []
    accessToRightLaneLastDetected = ["N/A", "N/A", "N/A"]
    delayBeforeReRoute = 140
    step = 0
    vehiclesApproachingClosure = []
    vehiclesThatTORed = []
    delayBeforeReRoute = 80 ### Needs to be considered
    TIMETOPERFORMDELAYTOC = 30 ### Needs to be considered
    DETECTEDTOCTIME = 5 ### Needs to be considered
    NUMBEROFVEHICLESREROUTED = 0
    minorWaitLengthBeforeAction = 30
    TIMETOPERFORMDELAYTOC = 30 ## Consider
    
    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()
        if step == 1000:
            stoppingCrashedVehicles()

        if step > 1200 and step < 42000:
            if step%3 == 0:
                vehiclesApproachingClosure = removeVehiclesThatPassCenter(vehiclesApproachingClosure)
                vehiclesThatTORed = removeOldToC(vehiclesThatTORed)
                seenInLeftExit = monitoringSeenInLeftExit(seenInLeftExit)
                
                TMSRightTopBottomlastVehicleDetected, standardRightTopBottomLastVehicleDetected, stuckInLeftExitlastVehicleDetected, leftExitUpwardToClastVehicleDetected, vehiclesApproachingClosure, seenInLeftExit = leftExitAfterIntersectionCollisionTMS(TMSRightTopBottomlastVehicleDetected, 
                standardRightTopBottomLastVehicleDetected, stuckInLeftExitlastVehicleDetected, leftExitUpwardToClastVehicleDetected, DETECTEDTOCTIME, vehiclesApproachingClosure, seenInLeftExit)
                
                # majorDelayLastVehicleDetected, vehiclesApproachingClosure, vehiclesThatTORed, NUMBEROFVEHICLESREROUTED = majorDelayDetectionHandlingCollision(majorDelayLastVehicleDetected, vehiclesApproachingClosure, 
                # vehiclesThatTORed, delayBeforeReRoute, TIMETOPERFORMDELAYTOC, step, NUMBEROFVEHICLESREROUTED)
                clearingCVsLastVehicleDetected = clearingLeftLaneOfCVs(clearingCVsLastVehicleDetected)
                accessToRightLaneLastDetected = allowingAccessToRightLaneCollision(minorWaitLengthBeforeAction, accessToRightLaneLastDetected)
                if REROUTINGBOOLEAN == True:
                    majorDelayLastVehicleDetected, vehiclesApproachingClosure, vehiclesThatTORed, NUMBEROFVEHICLESREROUTED = majorDelayDetectionHandlingCollision(majorDelayLastVehicleDetected, vehiclesApproachingClosure, 
                    vehiclesThatTORed, delayBeforeReRoute, TIMETOPERFORMDELAYTOC, step, NUMBEROFVEHICLESREROUTED)
                
        step += 1
    print("Number of Vehicles ReRouted", NUMBEROFVEHICLESREROUTED)
    traci.close(False)
    sys.stdout.flush()
    

def collisionRealCAVTMS(sumoBinary, LOS, ITERATION, REROUTINGBOOLEAN):
    print("----------------------------------------")
    print("In collision Real TMS")
    rate = vehicleRates(LOS)
    settingUpVehicles("Collision", "\RealTMSCAV", LOS, rate)
    collisionFlowCorrection(['Collision/RealTMSCAV/Route-Files/L4-CV-Route.rou.xml'], ["L4-CV"])
    traci.start([sumoBinary, "-c", "Collision\RealTMSCAV\CollisionRealTMSCAV.sumocfg",
                                "--tripinfo-output", "Collision\RealTMSCAV\Output-Files\Tripinfo.xml", "--ignore-route-errors",
                                "--device.emissions.probability", "1", "--waiting-time-memory", "300", "-S", "-Q", "-W"])

    TMS(REROUTINGBOOLEAN)
    vehicleTypes = ["L4-CV", "HDV"]
    TMSAlterOutputFiles("Collision", "CAV", LOS, ITERATION, vehicleTypes)
    print("----------------------------------------")

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