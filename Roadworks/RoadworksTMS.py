import os
import sys
import optparse
from sumolib import checkBinary  # Checks for the binary in environ vars
import traci

def runRoadWorksTMS():
    print("RoadWorks")
    step = 0
    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()
        print(step)
        step += 1

    traci.close()
    sys.stdout.flush()