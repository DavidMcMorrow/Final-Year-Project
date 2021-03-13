import random
import os
import traci
from xml.dom import minidom
import sys
import numpy as np

sys.path.append('c:/Users/david/OneDrive/Fifth Year/Final Year Project/SUMO/Simulation Stuff/Final-Year-Project')

from generalFunctions import (settingUpVehicles, flowCorrection, removeOldToC, roadworksTMSTopRightBottom, lateVehicleIndidentDetectionTopRightBottom, 
roadworksReRoutingLeftVehicles, leftUpStreamTMS, standardVehicleScenarioDetection, issuingToCToVehiclesTMS, lateVehicleIncidentDetection)

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
    leftApproachingLastDetected[3] = lateVehicleIncidentDetection(ENCOUNTEREDCLOSURETOC, leftApproachingLastDetected[3])
    return leftApproachingLastDetected
    

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
    # vehiclesApproachingClosure = []
    vehiclesThatTORed = []
    leftApproachingLastDetected = ["n/a", "n/a", "n/a", "n/a"]
    topBottomRightLateLastDetected = ["n/a", "n/a", "n/a", "n/a", "n/a", "n/a", "n/a", "n/a", "n/a",]
    topBottomRightTMSLastDetected = ["n/a", "n/a", "n/a", "n/a", "n/a", "n/a", "n/a", "n/a", "n/a",]
    # delayBeforeReoute = 120
    # TIMETOPERFORMDELAYTOC = 30
    ENCOUNTEREDCLOSURETOC = 3 # CONSIDER
    TMSISSUEDTOC = 5            # CONSIDER
    # delayBeforeToC = 20
    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()
    #     # vehiclesApproachingClosure = removeVehiclesNoLongerPresent(vehiclesApproachingClosure)
    #     # vehiclesThatTORed = removeVehiclesNoLongerPresent(vehiclesThatTORed)
    #     vehiclesApproachingClosure = removeVehiclesThatPassCenter(vehiclesApproachingClosure)
        vehiclesThatTORed = removeOldToC(vehiclesThatTORed)
    
        # if (step%2 == 0):
            

        
        if(step%3 == 0):
            leftApproachingLastDetected = handlingLeftApproaching(vehiclesThatTORed, TMSISSUEDTOC, ENCOUNTEREDCLOSURETOC, leftApproachingLastDetected)
            vehiclesThatTORed, topBottomRightLateLastDetected, topBottomRightTMSLastDetected = handlingTopRightBottom(topBottomRightLateDetectors, topBottomRightTMSDetectors, vehiclesThatTORed, 
                                                                ENCOUNTEREDCLOSURETOC, topBottomRightLateLastDetected, topBottomRightTMSLastDetected)
    #         vehiclesApproachingClosure, vehiclesThatTORed = majorDelayDetection(delayBeforeReoute, vehiclesApproachingClosure, vehiclesThatTORed, TIMETOPERFORMDELAYTOC, step)
            # vehiclesThatTORed, vehiclesApproachingClosure = allowingAccessToRightLane(delayBeforeToC, TIMETOPERFORMDELAYTOC, vehiclesThatTORed, vehiclesApproachingClosure)

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