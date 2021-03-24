import random
import os
import traci
from xml.dom import minidom
import sys
import numpy as np

sys.path.append('c:/Users/david/OneDrive/Fifth Year/Final Year Project/SUMO/Simulation Stuff/Final-Year-Project')

from generalFunctions import (settingUpVehicles, flowCorrection, removeOldToC, roadworksTMSTopRightBottom, lateVehicleIndidentDetectionTopRightBottom, 
roadworksReRoutingLeftVehicles, leftUpStreamTMS, standardVehicleScenarioDetection, issuingToCToVehiclesTMS, lateVehicleIncidentDetection, removeVehiclesThatPassCenter,
allowingAccessToRightLaneTMS, allowingAccessToRightLaneLate, addingVehicleToDelayDetection, detectingMajorDelay, handlingTopRightBottom, handlingLeftApproaching,
allowingAccessToRightLane, roadWorksMajorDelayDetection, TMSAlterOutputFiles, handlingToCUpstreamRoadworks)
    
def TMS():
    print("Running Baseline")
    step = 0
    NUMBEROFVEHICLESREROUTED = 0
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
    upwardToCLastDetected = ["n/a", "n/a", "n/a", "n/a", "n/a", "n/a", "n/a", "n/a"]
    accessToRightLaneLastDetected = ["n/a", "n/a"]
    majorDelayDetectionLastDetected = ["n/a", "n/a", "n/a"]
    minorWaitLengthBeforeAction = 20 ## Consider
    TIMETOPERFORMDELAYTOC = 30 ## Consider

    delayBeforeReRoute = 120
    
    ENCOUNTEREDCLOSURETOC = 3 # CONSIDER
    TMSISSUEDTOC = 5            # CONSIDER
    
    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()

        if(step%3 == 0):
            vehiclesApproachingClosure = removeVehiclesThatPassCenter(vehiclesApproachingClosure)
            vehiclesThatTORed = removeOldToC(vehiclesThatTORed)
            leftApproachingLastDetected = handlingLeftApproaching(vehiclesThatTORed, TMSISSUEDTOC, ENCOUNTEREDCLOSURETOC, leftApproachingLastDetected)
            vehiclesThatTORed, topBottomRightLateLastDetected, topBottomRightTMSLastDetected = handlingTopRightBottom(topBottomRightLateDetectors, topBottomRightTMSDetectors, vehiclesThatTORed, 
                                                                ENCOUNTEREDCLOSURETOC, topBottomRightLateLastDetected, topBottomRightTMSLastDetected)
            # vehiclesApproachingClosure, vehiclesThatTORed, majorDelayDetectionLastDetected, NUMBEROFVEHICLESREROUTED = roadWorksMajorDelayDetection(delayBeforeReRoute, vehiclesApproachingClosure, vehiclesThatTORed, 
            # TIMETOPERFORMDELAYTOC, step, majorDelayDetectionLastDetected, majorDelayDetectors, NUMBEROFVEHICLESREROUTED)
            vehiclesThatTORed, accessToRightLaneLastDetected = allowingAccessToRightLane(minorWaitLengthBeforeAction, vehiclesThatTORed, accessToRightLaneLastDetected, TIMETOPERFORMDELAYTOC)
            upwardToCLastDetected = handlingToCUpstreamRoadworks(upwardToCLastDetected)
        step += 1
    print("Final NUMBEROFVEHICLESREROUTED = ", NUMBEROFVEHICLESREROUTED)
    traci.close(False)
    sys.stdout.flush()

def roadworksRealTMSCAV(sumoBinary, LOS, ITERATION):
    print("HERE")
    rate = vehicleRates(LOS)
    settingUpVehicles("Roadworks", "\RealTMSCAV", LOS, rate)
    flowCorrection(['Roadworks/RealTMSCAV/Route-Files/L4-CV-Route.rou.xml'], ["L4-CV"], "CAV")
    
    # #traci starts sumo as a subprocess and then this script connects and runs
    traci.start([sumoBinary, "-c", "Roadworks\RealTMSCAV\RoadworksRealTMSCAV.sumocfg",
                "--tripinfo-output", "Roadworks\RealTMSCAV\Output-Files\TripInfo.xml", "--ignore-route-errors",
                "--device.emissions.probability", "1", "--waiting-time-memory", "300", "-S", "-Q"])

    TMS()
    TMSAlterOutputFiles("Roadworks", "CAV", LOS, ITERATION, ["L4-CV", "HDV"])

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