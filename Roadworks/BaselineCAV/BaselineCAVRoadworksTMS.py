import random
import os
import numpy as np
import sys
import optparse
import traci
from xml.dom import minidom

sys.path.append('c:/Users/david/OneDrive/Fifth Year/Final Year Project/SUMO/Simulation Stuff/Final-Year-Project')

from generalFunctions import (removeOldToC, settingUpVehicles, baselineAlterOutputFiles, flowCorrection, removeVehiclesThatPassCenter, roadworksReRouting, 
handlingLeftApproachingBaseline, handlingTopRightBottomBaseline, allowingAccessToRightLaneBaseline, roadWorksMajorDelayDetectionBaseline, handlingToCUpstreamRoadworks)



def TMS():
    NUMBEROFVEHICLESREROUTED = 0
    step = 0

    topBottomRightLateDetectors = ["lateTop_0", "lateTop_1", "lateTop_2",
                                    "lateRight_0", "lateRight_1", "lateRight_2",
                                    "lateBottom_0", "lateBottom_1","lateBottom_2"
                                    ]
    
    majorDelayDetectors = ["majorDelayDetection_0", "majorDelayDetection_1", "majorDelayDetection_2"]

    # vehiclesApproachingMergedLanes = []
    vehiclesThatTORed = []
    vehiclesApproachingClosure = []
    leftApproachingLastDetected = ["n/a", "n/a"]
    topBottomRightLateLastDetected = ["n/a", "n/a", "n/a", "n/a", "n/a", "n/a", "n/a", "n/a", "n/a"]
    # topBottomRightTMSLastDetected = ["n/a", "n/a", "n/a", "n/a", "n/a", "n/a", "n/a", "n/a", "n/a"]
    upwardToCLastDetected = ["n/a", "n/a", "n/a", "n/a", "n/a", "n/a", "n/a", "n/a"]
    accessToRightLaneLastDetected = ["n/a"]
    majorDelayDetectionLastDetected = ["n/a", "n/a", "n/a"]
    minorWaitLengthBeforeAction = 20 ## Consider
    TIMETOPERFORMDELAYTOC = 30 ## Consider

    delayBeforeReRoute = 120
    
    ENCOUNTEREDCLOSURETOC = 1 # CONSIDER
    
    
    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()

        if(step%3 == 0):
            vehiclesApproachingClosure = removeVehiclesThatPassCenter(vehiclesApproachingClosure)
            vehiclesThatTORed = removeOldToC(vehiclesThatTORed)
            leftApproachingLastDetected = handlingLeftApproachingBaseline(vehiclesThatTORed, ENCOUNTEREDCLOSURETOC, leftApproachingLastDetected)
            vehiclesThatTORed, topBottomRightLateLastDetected = handlingTopRightBottomBaseline(topBottomRightLateDetectors, vehiclesThatTORed, ENCOUNTEREDCLOSURETOC, topBottomRightLateLastDetected)
            # vehiclesApproachingClosure, vehiclesThatTORed, majorDelayDetectionLastDetected, NUMBEROFVEHICLESREROUTED = roadWorksMajorDelayDetectionBaseline(delayBeforeReRoute, vehiclesApproachingClosure, 
            #                                                                                 vehiclesThatTORed, TIMETOPERFORMDELAYTOC, step, majorDelayDetectionLastDetected, majorDelayDetectors, NUMBEROFVEHICLESREROUTED)
            vehiclesThatTORed, accessToRightLaneLastDetected = allowingAccessToRightLaneBaseline(minorWaitLengthBeforeAction, vehiclesThatTORed, accessToRightLaneLastDetected, TIMETOPERFORMDELAYTOC)
            upwardToCLastDetected = handlingToCUpstreamRoadworks(upwardToCLastDetected)
        step += 1
    print("Final NUMBEROFVEHICLESREROUTED = ", NUMBEROFVEHICLESREROUTED)
    traci.close(False)
    sys.stdout.flush()

def roadworksBaselineCAVTMS(sumoBinary, LOS, ITERATION):
    rate = vehicleRates(LOS)
    settingUpVehicles("Roadworks", "\BaselineCAV", LOS, rate)
    flowCorrection(['Roadworks/BaselineCAV/Route-Files/L4-CV-Route.rou.xml'], ["L4-CV"], "CAV")
    
    #traci starts sumo as a subprocess and then this script connects and runs
    traci.start([sumoBinary, "-c", "Roadworks\BaselineCAV\RoadworksBaselineCAV.sumocfg",
                "--tripinfo-output", "Roadworks\BaselineCAV\Output-Files\TripInfo.xml", "--ignore-route-errors",
                "--device.emissions.probability", "1", "--waiting-time-memory", "300", "-S", "-Q", "-W"])

    TMS()
    baselineAlterOutputFiles("Roadworks", "CAV", LOS, ITERATION, ["L4-CV", "HDV"])

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
