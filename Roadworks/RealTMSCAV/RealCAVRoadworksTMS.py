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

def leftUpStreamTMS(leftApproachingLastDetected):
    det_vehs = traci.inductionloop.getLastStepVehicleIDs("rerouting-left-vehicles")
    for veh in det_vehs:
        vehicleType = (traci.vehicle.getTypeID(veh)).split('-')[1]
        if traci.vehicle.getVehicleClass(veh) == "custom2" and vehicleType == "CV" and leftApproachingLastDetected != veh:
            receivedTMSResult = random.randint(0, 99)
            if receivedTMSResult > 75:
                # print("Did get TMS", veh)
                # traci.vehicle.setParameter(veh, "dynamicToCThreshold", 0)
                traci.vehicle.setVehicleClass(veh, "custom1")
                roadworksReRoutingLeftVehicles(veh)
            # else:
                # print("Didn't get TMS", veh)
        leftApproachingLastDetected = veh
    return leftApproachingLastDetected
                

def standardVehicleScenarioDetection(leftApproachingLastDetected):
    det_vehs = traci.inductionloop.getLastStepVehicleIDs("leftlaneStandardDetection")
    for veh in det_vehs:
        if traci.vehicle.getVehicleClass(veh) == "custom2" and leftApproachingLastDetected != veh:
            figuredOutScenario = random.randint(0,9) ## Needs to be considered
            if(figuredOutScenario < 3):
                # print("Did detect blockage", veh)
                # traci.vehicle.setParameter(veh, "dynamicToCThreshold", 0)
                traci.vehicle.setVehicleClass(veh, "custom1")
                roadworksReRoutingLeftVehicles(veh)
            # else:
                # print("Didn't detect blockage", veh)
        leftApproachingLastDetected = veh
    return leftApproachingLastDetected
    
def issuingToCToVehiclesTMS(vehiclesThatTORed, TMSISSUEDTOC, leftApproachingLastDetected):
    det_vehs = traci.inductionloop.getLastStepVehicleIDs("issuingToCInVehicleTMS")
    for veh in det_vehs:
        temp = veh in vehiclesThatTORed
        vehicleType = (traci.vehicle.getTypeID(veh)).split('-')[1]
        receivedToCAdvice = random.randint(0,9)
        if( (temp == False) and (vehicleType == "CV") and (receivedToCAdvice < 3) and (leftApproachingLastDetected != veh)):
            # print("Received ToC Advice", veh)
            roadworksReRoutingLeftVehicles(veh)
            traci.vehicle.setParameter(veh, "device.toc.requestToC", TMSISSUEDTOC)
            vehiclesThatTORed.append(veh)

        if vehicleType == "HDV":
            receivedToCAdvice = random.randint(0,9) ## Needs to be considered
            if(receivedToCAdvice < 4 and leftApproachingLastDetected != veh):
                roadworksReRoutingLeftVehicles(veh)
                traci.vehicle.setVehicleClass(veh, "custom1")
        leftApproachingLastDetected = veh
    return vehiclesThatTORed, leftApproachingLastDetected

def lateVehicleIncidentDetection(ENCOUNTEREDCLOSURETOC, leftApproachingLastDetected):
    det_vehs = traci.inductionloop.getLastStepVehicleIDs("allVehiclesToC")
    for veh in det_vehs:
        if leftApproachingLastDetected != veh:
            vehicleType = (traci.vehicle.getTypeID(veh)).split('-')[1]
            roadworksReRoutingLeftVehicles(veh)
            if vehicleType == "HDV":
                traci.vehicle.setVehicleClass(veh, "custom1")
            else:
                traci.vehicle.setParameter(veh, "device.toc.requestToC", ENCOUNTEREDCLOSURETOC)
        leftApproachingLastDetected = veh
    return leftApproachingLastDetected

def handlingLeftApproaching(vehiclesThatTORed, TMSISSUEDTOC, ENCOUNTEREDCLOSURETOC,leftApproachingLastDetected):
    leftApproachingLastDetected[0] = leftUpStreamTMS(leftApproachingLastDetected[0])
    leftApproachingLastDetected[1] = standardVehicleScenarioDetection(leftApproachingLastDetected[1])
    vehiclesThatTORed, leftApproachingLastDetected[2] = issuingToCToVehiclesTMS(vehiclesThatTORed, TMSISSUEDTOC, leftApproachingLastDetected[2])
    leftApproachingLastDetected[3] = lateVehicleIncidentDetection(ENCOUNTEREDCLOSURETOC, leftApproachingLastDetected[3])
    return leftApproachingLastDetected
    

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
    leftApproachingLastDetected = ["n/a", "n/a", "n/a", "n/a"]
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
            vehiclesThatTORed = handlingTopRightBottom(lateDetectors, topBottomLeftTMSDetectors, vehiclesThatTORed, ENCOUNTEREDCLOSURETOC)
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