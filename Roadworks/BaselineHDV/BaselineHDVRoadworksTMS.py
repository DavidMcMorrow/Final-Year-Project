import os
import numpy as np
import sys
import optparse
from sumolib import checkBinary  # Checks for the binary in environ vars
import traci
import matplotlib.pyplot as plt
import random
from xml.dom import minidom

sys.path.append('c:/Users/david/OneDrive/Fifth Year/Final Year Project/SUMO/Simulation Stuff/Final-Year-Project')

from generalFunctions import (roadworksReRouting, baselineAlterOutputFiles, settingUpVehicles, flowCorrection, removeVehiclesThatPassCenter, 
handlingLeftApproachingBaseline, handlingTopRightBottomBaseline, roadWorksMajorDelayDetectionBaseline, allowingAccessToRightLaneBaseline)

def TMS():
    step = 0
    NUMBEROFVEHICLESREROUTED = 0
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
    accessToRightLaneLastDetected = ["n/a"]
    majorDelayDetectionLastDetected = ["n/a", "n/a", "n/a"]
    minorWaitLengthBeforeAction = 20 ## Consider
    TIMETOPERFORMDELAYTOC = 30 ## Consider

    delayBeforeReRoute = 120
    
    ENCOUNTEREDCLOSURETOC = 3 # CONSIDER
    
    
    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()

        if(step%3 == 0):
            vehiclesApproachingClosure = removeVehiclesThatPassCenter(vehiclesApproachingClosure)
            # vehiclesThatTORed = removeOldToC(vehiclesThatTORed)
            leftApproachingLastDetected = handlingLeftApproachingBaseline(vehiclesThatTORed, ENCOUNTEREDCLOSURETOC, leftApproachingLastDetected)
            vehiclesThatTORed, topBottomRightLateLastDetected = handlingTopRightBottomBaseline(topBottomRightLateDetectors, vehiclesThatTORed, 
                                                                ENCOUNTEREDCLOSURETOC, topBottomRightLateLastDetected)
            # vehiclesApproachingClosure, vehiclesThatTORed, majorDelayDetectionLastDetected, NUMBEROFVEHICLESREROUTED = roadWorksMajorDelayDetectionBaseline(delayBeforeReRoute, vehiclesApproachingClosure, 
            #                                                                                 vehiclesThatTORed, TIMETOPERFORMDELAYTOC, step, majorDelayDetectionLastDetected, majorDelayDetectors, NUMBEROFVEHICLESREROUTED)
            vehiclesThatTORed, accessToRightLaneLastDetected = allowingAccessToRightLaneBaseline(minorWaitLengthBeforeAction, vehiclesThatTORed, accessToRightLaneLastDetected, TIMETOPERFORMDELAYTOC)

        step += 1
    print("Final NUMBEROFVEHICLESREROUTED = ", NUMBEROFVEHICLESREROUTED)
    traci.close(False)
    sys.stdout.flush()


def roadworksBaselineHDVTMS(sumoBinary, LOS, ITERATION):
    rate = vehicleRates(LOS)
    settingUpVehicles("Roadworks", "\BaselineHDV", LOS, rate)
    flowCorrection(['Roadworks/BaselineHDV/Route-Files/L0-HDV-Route.rou.xml'], ['L0-HDV'], "HDV")
    
    #traci starts sumo as a subprocess and then this script connects and runs
    traci.start([sumoBinary, "-c", "Roadworks\BaselineHDV\RoadworksBaselineHDV.sumocfg",
                "--tripinfo-output", "Roadworks\BaselineHDV\Output-Files\TripInfo.xml", "--ignore-route-errors",
                "--device.emissions.probability", "1", "--waiting-time-memory", "300", "-S", "-Q"])

    TMS()
    baselineAlterOutputFiles("Roadworks", "HDV", LOS, ITERATION, ["L0-HDV"])
    
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