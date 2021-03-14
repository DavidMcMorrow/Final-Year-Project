import random
import os
import traci
from xml.dom import minidom
import sys
import numpy as np

sys.path.append('c:/Users/david/OneDrive/Fifth Year/Final Year Project/SUMO/Simulation Stuff/Final-Year-Project')

from generalFunctions import (settingUpVehicles, flowCorrection, removeOldToC, roadworksTMSTopRightBottom, lateVehicleIndidentDetectionTopRightBottom, 
roadworksReRoutingLeftVehicles, leftUpStreamTMS, standardVehicleScenarioDetection, issuingToCToVehiclesTMS, lateVehicleIncidentDetection, removeVehiclesThatPassCenter,
allowingAccessToRightLaneTMS, allowingAccessToRightLaneLate, addingVehicleToDelayDetection, detectingMajorDelay)

def handlingTopRightBottom(topBottomRightLateDetectors, topBottomRightTMSDetectors, vehiclesThatTORed, ENCOUNTEREDCOLLISIONTOC, topBottomRightLateLastDetected, topBottomRightTMSLastDetected):
    topBottomRightTMSLastDetected = roadworksTMSTopRightBottom(topBottomRightTMSDetectors, topBottomRightTMSLastDetected)
    # vehiclesThatTORed, leftApproachingLastDetected[2] = issuingToCToVehiclesTMSTopRightBottom(vehiclesThatTORed, TMSISSUEDTOC, leftApproachingLastDetected[2])
    vehiclesThatTORed, topBottomRightLateLastDetected = lateVehicleIndidentDetectionTopRightBottom(topBottomRightLateDetectors, vehiclesThatTORed, 
                                                        ENCOUNTEREDCOLLISIONTOC, topBottomRightLateLastDetected)    
    return vehiclesThatTORed, topBottomRightLateLastDetected, topBottomRightTMSLastDetected

def handlingLeftApproaching(vehiclesThatTORed, TMSISSUEDTOC, ENCOUNTEREDCLOSURETOC,leftApproachingLastDetected):
    leftApproachingLastDetected[0] = leftUpStreamTMS(leftApproachingLastDetected[0])
    leftApproachingLastDetected[1] = standardVehicleScenarioDetection(leftApproachingLastDetected[1])
    vehiclesThatTORed, leftApproachingLastDetected[2] = issuingToCToVehiclesTMS(vehiclesThatTORed, TMSISSUEDTOC, leftApproachingLastDetected[2])
    leftApproachingLastDetected[3], vehiclesThatTORed = lateVehicleIncidentDetection(ENCOUNTEREDCLOSURETOC, leftApproachingLastDetected[3], vehiclesThatTORed)
    return leftApproachingLastDetected

def allowingAccessToRightLane(minorWaitLengthBeforeAction, vehiclesThatTORed, accessToRightLaneLastDetected, TIMETOPERFORMDELAYTOC):
    accessToRightLaneLastDetected[0] = allowingAccessToRightLaneTMS(accessToRightLaneLastDetected[0])
    vehiclesThatTORed, accessToRightLaneLastDetected[1] = allowingAccessToRightLaneLate(accessToRightLaneLastDetected[1], minorWaitLengthBeforeAction, vehiclesThatTORed, TIMETOPERFORMDELAYTOC)
    return vehiclesThatTORed, accessToRightLaneLastDetected

def roadWorksMajorDelayDetection(delayBeforeReRoute, vehiclesApproachingClosure, vehiclesThatTORed, TIMETOPERFORMDELAYTOC, step, majorDelayDetectionLastDetected, majorDelayDetectors):
    vehiclesApproachingClosure, majorDelayDetectionLastDetected = addingVehicleToDelayDetection(majorDelayDetectors, vehiclesApproachingClosure, "bottom-exit", majorDelayDetectionLastDetected)
    vehiclesApproachingClosure, vehiclesThatTORed = detectingMajorDelay(vehiclesApproachingClosure, vehiclesThatTORed, delayBeforeReRoute, TIMETOPERFORMDELAYTOC, step)
    return vehiclesApproachingClosure, vehiclesThatTORed, majorDelayDetectionLastDetected
    
def TMS():
    print("Running Baseline")
    step = 0
    
    topBottomRightTMSDetectors = ["advanceTop_0", "advanceTop_1", "advanceTop_2", 
                                "advanceRight_0", "advanceRight_1", "advanceRight_2", 
                                "advanceBottom_0", "advanceBottom_1", "advanceBottom_2"
                                ]

    topBottomRightLateDetectors = ["lateTop_0", "lateTop_1", "lateTop_2",
                                    "lateRight_0", "lateRight_1", "lateRight_2",
                                    "lateBottom_0", "lateBottom_1","lateBottom_2"
                                    ]
    
    majorDelayDetectors = ["majorDelayDetection_0", "majorDelayDetection_1", "majorDelayDetection_2"]

    # vehiclesApproachingMergedLanes = []
    vehiclesThatTORed = []
    vehiclesApproachingClosure = []
    leftApproachingLastDetected = ["n/a", "n/a", "n/a", "n/a"]
    topBottomRightLateLastDetected = ["n/a", "n/a", "n/a", "n/a", "n/a", "n/a", "n/a", "n/a", "n/a"]
    topBottomRightTMSLastDetected = ["n/a", "n/a", "n/a", "n/a", "n/a", "n/a", "n/a", "n/a", "n/a"]
    accessToRightLaneLastDetected = ["n/a", "n/a"]
    majorDelayDetectionLastDetected = ["n/a", "n/a", "n/a"]
    minorWaitLengthBeforeAction = 20 ## Consider
    TIMETOPERFORMDELAYTOC = 30 ## Consider

    delayBeforeReRoute = 120
    
    ENCOUNTEREDCLOSURETOC = 3 # CONSIDER
    TMSISSUEDTOC = 5            # CONSIDER
    
    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()
        vehiclesApproachingClosure = removeVehiclesThatPassCenter(vehiclesApproachingClosure)
        vehiclesThatTORed = removeOldToC(vehiclesThatTORed)
    
        if(step%2 == 0):
            leftApproachingLastDetected = handlingLeftApproaching(vehiclesThatTORed, TMSISSUEDTOC, ENCOUNTEREDCLOSURETOC, leftApproachingLastDetected)
            vehiclesThatTORed, topBottomRightLateLastDetected, topBottomRightTMSLastDetected = handlingTopRightBottom(topBottomRightLateDetectors, topBottomRightTMSDetectors, vehiclesThatTORed, 
                                                                ENCOUNTEREDCLOSURETOC, topBottomRightLateLastDetected, topBottomRightTMSLastDetected)
            vehiclesApproachingClosure, vehiclesThatTORed, majorDelayDetectionLastDetected = roadWorksMajorDelayDetection(delayBeforeReRoute, vehiclesApproachingClosure, vehiclesThatTORed, 
            TIMETOPERFORMDELAYTOC, step, majorDelayDetectionLastDetected, majorDelayDetectors)
            vehiclesThatTORed, accessToRightLaneLastDetected = allowingAccessToRightLane(minorWaitLengthBeforeAction, vehiclesThatTORed, accessToRightLaneLastDetected, TIMETOPERFORMDELAYTOC)

        step += 1

    traci.close(False)
    sys.stdout.flush()

def roadworksRealTMSCAV(sumoBinary, LOS, ITERATION):
    print("HERE")
    settingUpVehicles("Roadworks", "\RealTMSCAV", LOS)
    flowCorrection(['Roadworks/RealTMSCAV/Route-Files/L4-CV-Route.rou.xml'], ["L4-CV"], "CAV")
    
    # #traci starts sumo as a subprocess and then this script connects and runs
    traci.start([sumoBinary, "-c", "Roadworks\RealTMSCAV\RoadworksRealTMSCAV.sumocfg",
                "--tripinfo-output", "Roadworks\RealTMSCAV\Output-Files\TripInfo.xml", "--ignore-route-errors",
                "--device.emissions.probability", "1", "--waiting-time-memory", "300"])

    TMS()
    # baselineAlterOutputFiles("Roadworks", "CAV", LOS, ITERATION, ["L4-CV", "HDV"])