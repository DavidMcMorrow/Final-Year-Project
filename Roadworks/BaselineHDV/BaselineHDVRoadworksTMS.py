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

from generalFunctions import roadworksReRouting, baselineAlterOutputFiles, settingUpVehicles, flowCorrection, removeVehiclesThatPassCenter


def handlingLeftBlockedApproach():
    det_vehs = traci.inductionloop.getLastStepVehicleIDs("det_0")
    for veh in det_vehs:
        traci.vehicle.setRoute(veh, ["preparation", "left-short-approaching", "top-exit"])
        result = random.randint(0,1)
        if(result == 0):
            traci.vehicle.setVehicleClass(veh, "passenger")

    det_vehs = traci.inductionloop.getLastStepVehicleIDs("det_1")
    for veh in det_vehs:
        traci.vehicle.setRoute(veh, ["preparation", "left-short-approaching", "top-exit"])
        traci.vehicle.setVehicleClass(veh, "passenger")

def allowingStraightVehiclesInRightLane():
    detectors = ["det_2", "det_3"]
    for det in detectors:
        det_vehs = traci.inductionloop.getLastStepVehicleIDs(det)
        for veh in det_vehs:       
            if(traci.vehicle.getRoute(veh) == ("left-long-approaching", "preparation", "left-short-approaching", "right-exit")):
                traci.vehicle.setVehicleClass(veh, "passenger")

def majorDelayDetection(delayBeforeReoute, vehiclesApproachingClosure, step):
    detectors = ["left-long-approaching_0", "left-long-approaching_1", "left-long-approaching_2"]
    for det in detectors:
        det_vehs = traci.inductionloop.getLastStepVehicleIDs(det)
        for veh in det_vehs:
            temp1 = traci.vehicle.getRoute(veh)[len(traci.vehicle.getRoute(veh))-1]
            temp2 = veh in vehiclesApproachingClosure
            if ((temp1 !=  "bottom-exit") and (temp2 == False)):
                vehiclesApproachingClosure.append(veh)
                
    if(step%9 == 0):
        for veh in vehiclesApproachingClosure:
            temp1 = traci.vehicle.getRoute(veh)[len(traci.vehicle.getRoute(veh))-1]
            if traci.vehicle.getAccumulatedWaitingTime(veh) > delayBeforeReoute:
                print("WAITED TOO LONG", veh)
                vehiclesApproachingClosure = reRoutingVehicles(veh, temp1, vehiclesApproachingClosure)
    return vehiclesApproachingClosure

def reRoutingVehicles(veh, target, vehiclesApproachingClosure):
    rerouteResult = random.randint(0,3) ## NEED TO CONSIDER THIS PROBABILITY MORE
    if(rerouteResult == 0):
        traci.vehicle.setVehicleClass(veh, "passenger")
        print("ABOUT TO BE REROUTED")
        traci.vehicle.setRoute(veh, roadworksReRouting(target))
        vehiclesApproachingClosure.remove(veh)
    return vehiclesApproachingClosure

def TMS():
    print("Running Baseline")
    step = 0
    delayBeforeReoute = 120 
    vehiclesApproachingClosure = []
    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()
        vehiclesApproachingClosure = removeVehiclesThatPassCenter(vehiclesApproachingClosure)
        if(step%3 == 0):
            handlingLeftBlockedApproach()
            allowingStraightVehiclesInRightLane()
            vehiclesApproachingClosure = majorDelayDetection(delayBeforeReoute, vehiclesApproachingClosure, step)
        step += 1
    traci.close(False)
    sys.stdout.flush()

def roadworksBaselineHDVTMS(sumoBinary, LOS, ITERATION):
    # settingUpVehicles(LOS)
    settingUpVehicles("Roadworks", "\BaselineHDV", LOS)
    flowCorrection(['Roadworks/BaselineHDV/Route-Files/L0-HDV-Route.rou.xml'], ['L0-HDV'], "HDV")
    
    #traci starts sumo as a subprocess and then this script connects and runs
    traci.start([sumoBinary, "-c", "Roadworks\BaselineHDV\RoadworksBaselineHDV.sumocfg",
                "--tripinfo-output", "Roadworks\BaselineHDV\Output-Files\TripInfo.xml", "--ignore-route-errors",
                "--device.emissions.probability", "1", "--waiting-time-memory", "300"])

    TMS()
    baselineAlterOutputFiles("Roadworks", "HDV", LOS, ITERATION, ["HDV"])
    


# automate file name creation
# do the same for trip-info.xml