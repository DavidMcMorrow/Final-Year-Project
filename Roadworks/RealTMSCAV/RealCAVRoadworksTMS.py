import random
import os
import traci
from xml.dom import minidom
import sys
import numpy as np

sys.path.append('c:/Users/david/OneDrive/Fifth Year/Final Year Project/SUMO/Simulation Stuff/Final-Year-Project')

from generalFunctions import settingUpVehicles, flowCorrection, removeOldToC, roadworksTMSTopRightBottom, naturalHandlingTopRightBottom, roadworksReRoutingLeftVehicles

def handlingTopRightBottom(lateDetectors, topBottomLeftTMSDetectors, vehiclesThatTORed, ENCOUNTEREDCOLLISIONTOC):
    roadworksTMSTopRightBottom(topBottomLeftTMSDetectors)
    vehiclesThatTORed = naturalHandlingTopRightBottom(lateDetectors, vehiclesThatTORed, ENCOUNTEREDCOLLISIONTOC)    
    return vehiclesThatTORed

def handlingLeftApproaching(vehiclesThatTORed, ENCOUNTEREDCOLLISIONTOC):
    det_vehs = traci.inductionloop.getLastStepVehicleIDs("rerouting-left-vehicles")
    for veh in det_vehs:
        roadworksReRoutingLeftVehicles(veh)
        vehicleType = (traci.vehicle.getTypeID(veh)).split('-')[1]
        if traci.vehicle.getVehicleClass(veh) == "custom2" and vehicleType == "CV":
            receivedTMSResult = random.randint(0, 99)
            if receivedTMSResult > 50:
                traci.vehicle.setVehicleClass(veh, "custom1")
            else:
                traci.vehicle.setParameter(veh, "device.toc.dynamicToCThreshold", 0)
            
            

    # det_vehs = traci.inductionloop.getLastStepVehicleIDs("det_0")
    # for veh in det_vehs:
    #     roadworksReRoutingLeftVehicles(veh)
    #     result = random.randint(0,3) ## Needs to be considered
    #     if(result == 0):
    #         traci.vehicle.setVehicleClass(veh, "custom1")

    # det_vehs = traci.inductionloop.getLastStepVehicleIDs("Issuing-ToC-in-Vehicle")
    # for veh in det_vehs:
    #     roadworksReRoutingLeftVehicles(veh)
    #     temp = veh in vehiclesThatTORed
    #     if(traci.vehicle.getVehicleClass(veh) == "custom2" and temp == False):
    #         traci.vehicle.setParameter(veh, "device.toc.requestToC", ENCOUNTEREDCOLLISIONTOC)
    #         vehiclesThatTORed.append(veh)

def TMS():
    print("Running Baseline")
    step = 0
    lateDetectors = ["intersectionTop", "intersectionRight", "intersectionBottom"]
    topBottomLeftTMSDetectors = ["advanceTop_0", "advanceTop_1", "advanceTop_2", 
                                "advanceRight_0", "advanceRight_1", "advanceRight_2", 
                                "advanceBottom_0", "advanceBottom_1", "advanceBottom_2"
                                ]
    # vehiclesApproachingClosure = []
    vehiclesThatTORed = []
    # delayBeforeReoute = 120
    # TIMETOPERFORMDELAYTOC = 30
    ENCOUNTEREDCOLLISIONTOC = 3 ## Needs to be considered
    # delayBeforeToC = 20
    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()
    #     # vehiclesApproachingClosure = removeVehiclesNoLongerPresent(vehiclesApproachingClosure)
    #     # vehiclesThatTORed = removeVehiclesNoLongerPresent(vehiclesThatTORed)
    #     vehiclesApproachingClosure = removeVehiclesThatPassCenter(vehiclesApproachingClosure)
        vehiclesThatTORed = removeOldToC(vehiclesThatTORed)
    
        if (step%2 == 0):
            handlingLeftApproaching(vehiclesThatTORed, ENCOUNTEREDCOLLISIONTOC)

        
        if(step%3 == 0):
            vehiclesThatTORed = handlingTopRightBottom(lateDetectors, topBottomLeftTMSDetectors, vehiclesThatTORed, ENCOUNTEREDCOLLISIONTOC)
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