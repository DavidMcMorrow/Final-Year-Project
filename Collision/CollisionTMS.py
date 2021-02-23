import os
import sys
import optparse
from sumolib import checkBinary  # Checks for the binary in environ vars
import traci
# ../PreparingVehicleModels/L4-CV.add.xml, ../PreparingVehicleModels/L2-CV.add.xml, ../PreparingVehicleModels/L0-HDV.add.xml, 
#         ../PreparingVehicleModels/L2-Non-CV.add.xml, ../PreparingVehicleModels/L4-Non-CV.add.xml"


def runCollisionTMS():
    print("Collision")
    step = 0
    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()
        print(step)
        if step == 100:
            traci.vehicle.setStop("crashed-car-lane-zero.0", "left-exit", 25, 0, 1000)
            traci.vehicle.setStop("crashed-car-lane-zero.1", "left-exit", 20, 0, 1000)
            traci.vehicle.setStop("crashed-car-lane-one.0", "left-exit", 25, 1, 1000)
            traci.vehicle.setStop("crashed-car-lane-one.1", "left-exit", 20, 1, 1000)
            
        step += 1
        

    traci.close()
    sys.stdout.flush()