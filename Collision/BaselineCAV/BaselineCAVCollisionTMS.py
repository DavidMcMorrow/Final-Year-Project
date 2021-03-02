import random
import os
import numpy as np
import sys
import optparse
import traci
from xml.dom import minidom

def settingUpVehicles(LOS):
    with open('Collision\BaselineCAV\PreparingVehicleModels\How to use.txt') as f:
        for line in f:
            if(line != "\n"):
                line = 'cmd /c ' + line
                if(line.find('python PreparingVehicleModels/randomTrips.py') != -1):
                    line = line.rstrip()
                    line = line + " " + str(random.randint(0,9))
                    if LOS == "A":
                        line = line + " -p " + str(1.86)
                    if LOS == "B":
                        line = line + " -p " + str(1.25)
                    if LOS == "C":
                        line = line + " -p " + str(1.07)
                    if LOS == "D":
                        line = line + " -p " + str(0.94)
                    if LOS == "Test":
                        line = line + " -p " + str(0.7)
                        
                os.system(line)

def TMS():
    print("Running Baseline")
    step = 0
    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()
        step += 1

    traci.close(False)
    sys.stdout.flush()

def collisionBaselineCAVTMS(sumoBinary, LOS, ITERATION):
    print("here")
    settingUpVehicles(LOS)
    traci.start([sumoBinary, "-c", "Collision\BaselineCAV\CollisionIntersectionBaselineCAV.sumocfg",
                                "--tripinfo-output", "Collision\BaselineCAV\Output-Files\CollisionTripinfo.xml", "--ignore-route-errors"])

    TMS()