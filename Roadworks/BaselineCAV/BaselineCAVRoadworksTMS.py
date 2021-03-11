import random
import os
import numpy as np
import sys
import optparse
import traci
from xml.dom import minidom

sys.path.append('c:/Users/david/OneDrive/Fifth Year/Final Year Project/SUMO/Simulation Stuff/Final-Year-Project')

from generalFunctions import removeOldToC, settingUpVehicles, baselineAlterOutputFiles, flowCorrection, removeVehiclesThatPassCenter, roadworksReRouting


def handlingLeftApproaching(vehiclesThatTORed, ENCOUNTEREDCOLLISIONTOC):
    det_vehs = traci.inductionloop.getLastStepVehicleIDs("rerouting-left-vehicles")
    for veh in det_vehs:
        result = random.randint(0,3) ## Needs to be considered
        if(result == 0):
            traci.vehicle.setVehicleClass(veh, "custom1")

    det_vehs = traci.inductionloop.getLastStepVehicleIDs("det_0")
    for veh in det_vehs:
        traci.vehicle.setParameter(veh, "device.toc.dynamicToCThreshold", 0)
        traci.vehicle.setRoute(veh, ["preparation", "left-short-approaching", "top-exit"])
    
    det_vehs = traci.inductionloop.getLastStepVehicleIDs("Issuing-ToC-in-Vehicle")
    for veh in det_vehs:
        temp = veh in vehiclesThatTORed
        if(traci.vehicle.getVehicleClass(veh) == "custom2" and temp == False):
            traci.vehicle.setParameter(veh, "device.toc.requestToC", ENCOUNTEREDCOLLISIONTOC)
            vehiclesThatTORed.append(veh)

def handlingTopRightBottom(detectors, vehiclesThatTORed, ENCOUNTEREDCOLLISIONTOC):
    for det in detectors:
        det_vehs = traci.inductionloop.getLastStepVehicleIDs(det)
        for veh in det_vehs:
            temp = veh in vehiclesThatTORed
            if temp == False and traci.vehicle.getVehicleClass(veh) != "passenger":
                result = random.randint(0,1) ## Needs to be considered
                if(result == 0):
                    traci.vehicle.setVehicleClass(veh, "passenger")
                else:
                    traci.vehicle.setParameter(veh, "device.toc.requestToC", ENCOUNTEREDCOLLISIONTOC)
                    vehiclesThatTORed.append(veh)
    return vehiclesThatTORed

def majorDelayDetection(delayBeforeReoute, vehiclesApproachingClosure, vehiclesThatTORed, ToCLeadTime, step):
    detectors = ["left-long-approaching_0", "left-long-approaching_1", "left-long-approaching_2"]
    for det in detectors:
        det_vehs = traci.inductionloop.getLastStepVehicleIDs(det)
        for veh in det_vehs:
            temp1 = traci.vehicle.getRoute(veh)[len(traci.vehicle.getRoute(veh))-1]
            temp2 = veh in vehiclesApproachingClosure
            if ((temp1 !=  "bottom-exit") and (temp2 == False)):
                vehiclesApproachingClosure.append(veh)

    if (step%9 == 0):
        for veh in vehiclesApproachingClosure:
            temp3 = traci.vehicle.getRoute(veh)[len(traci.vehicle.getRoute(veh))-1]
            if(traci.vehicle.getAccumulatedWaitingTime(veh) > delayBeforeReoute):
                vehiclesApproachingClosure, vehiclesThatTORed = reRoutingVehicles(veh, temp3, vehiclesApproachingClosure, vehiclesThatTORed, ToCLeadTime)
    return vehiclesApproachingClosure, vehiclesThatTORed

def reRoutingVehicles(veh, target, vehiclesApproachingClosure, vehiclesThatTORed, ToCLeadTime):
    tocResult = random.randint(0, 3) ## NEED TO CONSIDER THIS PROBABILITY MORE
    temp = veh in vehiclesThatTORed
    if(tocResult != 0 and temp == False and traci.vehicle.getTypeID(veh)[:2] == "L4"):
        traci.vehicle.requestToC(veh, ToCLeadTime)
        vehiclesThatTORed.append(veh)
        
    rerouteResult = random.randint(0, 3) ## NEED TO CONSIDER THIS PROBABILITY MORE
    if(rerouteResult == 0):
        traci.vehicle.setVehicleClass(veh, "passenger")
        traci.vehicle.setRoute(veh, roadworksReRouting(target))
        vehiclesApproachingClosure.remove(veh)
    return vehiclesApproachingClosure, vehiclesThatTORed

def TMS():
    print("Running Baseline")
    step = 0
    detectors = ["det_4", "det_5", "det_6"]
    vehiclesApproachingClosure = []
    vehiclesThatTORed = []
    delayBeforeReoute = 120
    TIMETOPERFORMDELAYTOC = 30
    ENCOUNTEREDCOLLISIONTOC = 3
    delayBeforeToC = 20
    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()
        # vehiclesApproachingClosure = removeVehiclesNoLongerPresent(vehiclesApproachingClosure)
        # vehiclesThatTORed = removeVehiclesNoLongerPresent(vehiclesThatTORed)
        vehiclesApproachingClosure = removeVehiclesThatPassCenter(vehiclesApproachingClosure)
        vehiclesThatTORed = removeOldToC(vehiclesThatTORed)
    
        if (step%2 == 0):
            handlingLeftApproaching(vehiclesThatTORed, ENCOUNTEREDCOLLISIONTOC)
            

        if(step%3 == 0):
            vehiclesThatTORed = handlingTopRightBottom(detectors, vehiclesThatTORed, ENCOUNTEREDCOLLISIONTOC)
            vehiclesApproachingClosure, vehiclesThatTORed = majorDelayDetection(delayBeforeReoute, vehiclesApproachingClosure, vehiclesThatTORed, TIMETOPERFORMDELAYTOC, step)
            vehiclesThatTORed, vehiclesApproachingClosure = allowingAccessToRightLane(delayBeforeToC, TIMETOPERFORMDELAYTOC, vehiclesThatTORed, vehiclesApproachingClosure)

        step += 1

    traci.close(False)
    sys.stdout.flush()

def roadworksBaselineCAVTMS(sumoBinary, LOS, ITERATION):
    settingUpVehicles("Roadworks", "\BaselineCAV", LOS)
    flowCorrection(['Roadworks/BaselineCAV/Route-Files/L4-CV-Route.rou.xml'], ["L4-CV"], "CAV")
    
    #traci starts sumo as a subprocess and then this script connects and runs
    traci.start([sumoBinary, "-c", "Roadworks\BaselineCAV\RoadworksBaselineCAV.sumocfg",
                "--tripinfo-output", "Roadworks\BaselineCAV\Output-Files\TripInfo.xml", "--ignore-route-errors",
                "--device.emissions.probability", "1", "--waiting-time-memory", "300"])

    TMS()
    baselineAlterOutputFiles("Roadworks", "CAV", LOS, ITERATION, ["L4-CV", "HDV"])


def allowingAccessToRightLane(delayBeforeToC, TIMETOPERFORMDELAYTOC, vehiclesThatTORed, vehiclesApproachingClosure):
    det_vehs = traci.inductionloop.getLastStepVehicleIDs("det_2")
    for veh in det_vehs:
        temp = veh in vehiclesApproachingClosure
        if temp == True:
            vehiclesApproachingClosure.remove(veh)
        if(traci.vehicle.getRoute(veh)[len(traci.vehicle.getRoute(veh))-1] ==  "right-exit" and traci.vehicle.getTypeID(veh)[:2] == "L4"):
            temp = veh in vehiclesThatTORed
            if(traci.vehicle.getAccumulatedWaitingTime(veh) >= delayBeforeToC and temp == False and traci.vehicle.getVehicleClass(veh) != "passenger"):
                ToCResult = random.randint(0, 1)
                if(ToCResult == 0):
                    traci.vehicle.requestToC(veh, TIMETOPERFORMDELAYTOC)
                    vehiclesThatTORed.append(veh)
                else:
                    traci.vehicle.setVehicleClass(veh, "passenger")

    return vehiclesThatTORed, vehiclesApproachingClosure

