import os
import numpy as np
import sys
import optparse
from sumolib import checkBinary  # Checks for the binary in environ vars
import traci
import matplotlib.pyplot as plt
import random

def getVehiclesInCorrectLanes():
    detectors = ["det_0", "det_1", "det_2"]
    for dect in detectors:
        det_vehs = traci.inductionloop.getLastStepVehicleIDs(dect)
        for veh in det_vehs:
            if(traci.vehicle.getVehicleClass(veh) == "custom2"):
                # traci.vehicle.changeLane(veh, 2, 20)
                traci.vehicle.changeTarget(veh, "preparation")

def leftApproach():
    getVehiclesInCorrectLanes()
    det_vehs = traci.inductionloop.getLastStepVehicleIDs("det_3")
    for veh in det_vehs:
        traci.vehicle.changeTarget(veh, "top-exit")
        if(random.randint(0,1) == 0):
            traci.vehicle.setVehicleClass(veh, "custom1")
        else:
            traci.vehicle.requestToC(veh, -10)

def otherApproaches():
    detectors = ["det_4", "det_5", "det_6"]
    for dect in detectors:
        det_vehs = traci.inductionloop.getLastStepVehicleIDs(dect)
        for veh in det_vehs:
            if(traci.vehicle.getVehicleClass(veh) == "custom1"):
                if(random.randint(0,1) == 0):
                    traci.vehicle.setVehicleClass(veh, "passenger")
                else:
                    traci.vehicle.requestToC(veh, -10)

def runRoadWorksTMS():
    print("RoadWorks")
    step = 0
    
    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()
        #print(step)
        leftApproach()
        otherApproaches()
            
        # det_vehs = traci.inductionloop.getLastStepVehicleIDs("det_3")
        # for veh in det_vehs:
        #     print("veh", veh)
        #     # traci.vehicle.changeLane(veh, 0, 100)
        #     traci.vehicle.requestToC(veh, 0)
        step += 1

    traci.close()
    sys.stdout.flush()