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
allowingAccessToRightLane, roadWorksMajorDelayDetection, TMSAlterOutputFiles, vehiclePenetrationRates1, handlingToCUpstreamRoadworks, 
baselineAlterOutputFiles, handlingLeftApproachingBaseline, allowingAccessToRightLaneBaseline, handlingTopRightBottomBaseline)
    
def TMS():
    print("Running Penetration Rate 1")
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
            leftApproachingLastDetected = handlingLeftApproachingBaseline(vehiclesThatTORed, ENCOUNTEREDCLOSURETOC, leftApproachingLastDetected)
            vehiclesThatTORed, topBottomRightLateLastDetected = handlingTopRightBottomBaseline(topBottomRightLateDetectors, vehiclesThatTORed, 
                                                                ENCOUNTEREDCLOSURETOC, topBottomRightLateLastDetected)
            # vehiclesApproachingClosure, vehiclesThatTORed, majorDelayDetectionLastDetected, NUMBEROFVEHICLESREROUTED = roadWorksMajorDelayDetectionBaseline(delayBeforeReRoute, vehiclesApproachingClosure, 
            #                                                                                 vehiclesThatTORed, TIMETOPERFORMDELAYTOC, step, majorDelayDetectionLastDetected, majorDelayDetectors, NUMBEROFVEHICLESREROUTED)
            vehiclesThatTORed, accessToRightLaneLastDetected = allowingAccessToRightLaneBaseline(minorWaitLengthBeforeAction, vehiclesThatTORed, accessToRightLaneLastDetected, TIMETOPERFORMDELAYTOC)
            upwardToCLastDetected = handlingToCUpstreamRoadworks(upwardToCLastDetected)
        step += 1
    print("Final NUMBEROFVEHICLESREROUTED = ", NUMBEROFVEHICLESREROUTED)
    traci.close(False)
    sys.stdout.flush()

def roadworksBaselinePenetration1(sumoBinary, LOS, ITERATION):
    print("HERE P1")
    files = ['Roadworks/BaselinePenetration1/Route-Files/L4-CV-Route.rou.xml', 'Roadworks/BaselinePenetration1/Route-Files/L4-AV-Route.rou.xml', 
            'Roadworks/BaselinePenetration1/Route-Files/L2-CV-Route.rou.xml', 'Roadworks/BaselinePenetration1/Route-Files/L2-AV-Route.rou.xml',
            'Roadworks/BaselinePenetration1/Route-Files/L0-HDV-Route.rou.xml']
    vehicleTypes = ["L4-CV", "L4-AV", "L2-CV", "L2-AV", "L0-HDV"]
    rate = vehiclePenetrationRates1(LOS)
    settingUpVehicles("Roadworks", "\BaselinePenetration1", LOS, rate)
    flowCorrection(['Roadworks/BaselinePenetration1/Route-Files/L4-CV-Route.rou.xml'], ["L4-CV"], "Penetration1")
    flowCorrection(['Roadworks/BaselinePenetration1/Route-Files/L4-AV-Route.rou.xml'], ["L4-AV"], "Penetration1")
    flowCorrection(['Roadworks/BaselinePenetration1/Route-Files/L2-CV-Route.rou.xml'], ["L2-CV"], "Penetration1")
    flowCorrection(['Roadworks/BaselinePenetration1/Route-Files/L2-AV-Route.rou.xml'], ["L2-AV"], "Penetration1")
    flowCorrection(['Roadworks/BaselinePenetration1/Route-Files/L0-HDV-Route.rou.xml'], ["L0-HDV"], "Penetration1")
    
    # #traci starts sumo as a subprocess and then this script connects and runs
    traci.start([sumoBinary, "-c", "Roadworks\BaselinePenetration1\RoadworksBaselineTMSPenetration1.sumocfg",
                "--tripinfo-output", "Roadworks\BaselinePenetration1\Output-Files\TripInfo.xml", "--ignore-route-errors",
                "--device.emissions.probability", "1", "--waiting-time-memory", "300", "-S", "-W"])

    TMS()
    baselineAlterOutputFiles("Roadworks", "Penetration1", LOS, ITERATION, vehicleTypes)

