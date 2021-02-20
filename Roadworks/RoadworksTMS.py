import os
import numpy as np
import sys
import optparse
from sumolib import checkBinary  # Checks for the binary in environ vars
import traci
import matplotlib.pyplot as plt

def runRoadWorksTMS():
    print("RoadWorks")
    step = 0
    
    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()
        #print(step)
        det_vehs = traci.inductionloop.getLastStepVehicleIDs("det_0")
        for veh in det_vehs:
            print("veh", veh)
            print("veh", traci.vehicle.getVehicleClass(veh))
            # traci.vehicle.changeLane(veh, 0, 100)
            # traci.vehicle.requestToC(veh, 0)
            
        # det_vehs = traci.inductionloop.getLastStepVehicleIDs("det_1")
        # for veh in det_vehs:
        #     traci.vehicle.changeLane(veh, 0, 100)
        #     # traci.vehicle.requestToC(veh, 0)
            
        # det_vehs = traci.inductionloop.getLastStepVehicleIDs("det_2")
        # for veh in det_vehs:
        #     traci.vehicle.changeLane(veh, 0, 100)
        #     # traci.vehicle.requestToC(veh, 0)

        # det_vehs = traci.inductionloop.getLastStepVehicleIDs("det_3")
        # for veh in det_vehs:
        #     print("veh", veh)
        #     # traci.vehicle.changeLane(veh, 0, 100)
        #     traci.vehicle.requestToC(veh, 0)
        step += 1

    traci.close()
    sys.stdout.flush()