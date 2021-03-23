import random
import os
import numpy as np
import sys
import optparse
import traci
from xml.dom import minidom

sys.path.append('c:/Users/david/OneDrive/Fifth Year/Final Year Project/SUMO/Simulation Stuff/Final-Year-Project')

from generalFunctions import (removeOldToC, collisionReRouteClockWiseFirst, collisionReRouteClockWiseSecond, baselineAlterOutputFiles, settingUpVehicles, 
                                removeVehiclesThatPassCenter, stoppingCrashedVehicles, collisionFlowCorrection, allowingAccessToRightLaneCollisionBaseline,
                                monitoringSeenInLeftExit, leftExitAfterIntersectionCollisionTMSBaseline)

def TMS():
    print("Running Baseline")
    step = 0
    delayBeforeReoute = 200 ### Needs to be considered
    vehiclesApproachingClosure = []
    step = 0
    minorWaitLengthBeforeAction = 30
    accessToRightLaneLastDetected = ["N/A"]
    standardRightTopBottomLastVehicleDetected = ["N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A"]
    stuckInLeftExitlastVehicleDetected = ["N/A", "N/A"]
    leftExitUpwardToClastVehicleDetected = ["N/A", "N/A"]
    seenInLeftExit = []
    vehiclesThatTORed = []
    DETECTEDTOCTIME = 5

    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()
        
        # vehiclesApproachingClosure = removeVehiclesThatPassCenter(vehiclesApproachingClosure)
        # vehiclesThatTORed = removeOldToC(vehiclesThatTORed)
        
        if step == 1000:
            stoppingCrashedVehicles()

        if (step > 1200 and step < 42000):
            if step%3 == 0:
                vehiclesApproachingClosure = removeVehiclesThatPassCenter(vehiclesApproachingClosure)
                vehiclesThatTORed = removeOldToC(vehiclesThatTORed)
                seenInLeftExit = monitoringSeenInLeftExit(seenInLeftExit)
                
                standardRightTopBottomLastVehicleDetected, stuckInLeftExitlastVehicleDetected, leftExitUpwardToClastVehicleDetected, vehiclesApproachingClosure, seenInLeftExit = leftExitAfterIntersectionCollisionTMSBaseline(standardRightTopBottomLastVehicleDetected, 
                stuckInLeftExitlastVehicleDetected, leftExitUpwardToClastVehicleDetected, DETECTEDTOCTIME, vehiclesApproachingClosure, seenInLeftExit)
                
                # majorDelayLastVehicleDetected, vehiclesApproachingClosure, vehiclesThatTORed, NUMBEROFVEHICLESREROUTED = majorDelayDetectionHandlingCollision(majorDelayLastVehicleDetected, vehiclesApproachingClosure, 
                # vehiclesThatTORed, delayBeforeReRoute, TIMETOPERFORMDELAYTOC, step, NUMBEROFVEHICLESREROUTED)
                # clearingCVsLastVehicleDetected = clearingLeftLaneOfCVs(clearingCVsLastVehicleDetected)
                accessToRightLaneLastDetected = allowingAccessToRightLaneCollisionBaseline(minorWaitLengthBeforeAction, accessToRightLaneLastDetected)
        step += 1

    traci.close(False)
    sys.stdout.flush()

def collisionBaselineCAVTMS(sumoBinary, LOS, ITERATION):
    print("here")
    rate = vehicleRates(LOS)
    settingUpVehicles("Collision", "\BaselineCAV", LOS, rate)
    collisionFlowCorrection(['Collision/BaselineCAV/Route-Files/L4-CV-Route.rou.xml'], ["L4-CV"])
    traci.start([sumoBinary, "-c", "Collision\BaselineCAV\CollisionIntersectionBaselineCAV.sumocfg",
                                "--tripinfo-output", "Collision\BaselineCAV\Output-Files\Tripinfo.xml", "--ignore-route-errors",
                                "--device.emissions.probability", "1", "--waiting-time-memory", "300", "-S", "-Q", "-W"])

    TMS()
    baselineAlterOutputFiles("Collision", "CAV", LOS, ITERATION, ["L4-CV", "L0-HDV"])

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

