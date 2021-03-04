import random
import os
import numpy as np
import sys
import optparse
import traci
from xml.dom import minidom

def settingUpVehicles(LOS):
    with open('Collision\BaselineHDV\PreparingVehicleModels\How to use.txt') as f:
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

def stoppingCrashedVehicles():
    traci.vehicle.setStop("crashed-car-lane-zero.0", "left-exit", 25, 0, 4500)
    traci.vehicle.setStop("crashed-car-lane-zero.1", "left-exit", 20, 0, 4500)
    traci.vehicle.setStop("crashed-car-lane-one.0", "left-exit", 25, 1, 4500)
    traci.vehicle.setStop("crashed-car-lane-one.1", "left-exit", 20, 1, 4500)

def leftExit():
    det_vehs = traci.inductionloop.getLastStepVehicleIDs("left-exit_0")
    for veh in det_vehs:
        traci.vehicle.changeLane(veh, 1, 1)
        if(traci.vehicle.getVehicleClass(veh) == "passenger"):    
            traci.vehicle.setVehicleClass(veh, "emergency")

    det_vehs = traci.inductionloop.getLastStepVehicleIDs("left-exit_1")
    for veh in det_vehs:
        if(traci.vehicle.getVehicleClass(veh) == "passenger"):
            traci.vehicle.setVehicleClass(veh, "emergency")

def reRouteClockWiseSecond(edge):
    newRoute = []
    if(edge == "top"):
        newRoute = ["top-approaching", "bottom-approaching"]
    elif(edge == "right"):
        newRoute = ["right-approaching", "top-approaching"]
    elif(edge == "bottom"):
        newRoute = ["bottom-approaching", "right-approaching"]
    return newRoute

def reRouteClockWiseFirst(edge):
    newRoute = []
    if(edge == "top"):
        newRoute = ["top-approaching", "right-approaching"]
    elif(edge == "right"):
        newRoute = ["right-approaching", "bottom-approaching"]
    elif(edge == "bottom"):
        newRoute = ["bottom-approaching", "top-approaching"]
    return newRoute

def closeRightTopBottom():
    detectors = ["close-top-approaching_0", "close-right-approaching_1", "close-bottom-approaching_2"]
    edges = ["top", "right", "bottom"]
    for i in range(0, len(detectors)-1):
        det_vehs = traci.inductionloop.getLastStepVehicleIDs(detectors[i])
        for veh in det_vehs:
            rerouteResult = random.randint(0,1)
            if(rerouteResult == 0):
                directionResult = random.randint(0,1)
                if(directionResult == 0):
                    traci.vehicle.setRoute(veh, reRouteClockWiseFirst(edges[i]))
                else:
                    traci.vehicle.setRoute(veh, reRouteClockWiseSecond(edges[i]))

def TMS():
    print("Running Baseline")
    step = 0
    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()
        stoppingCrashedVehicles()
        if step == 1000:
            stoppingCrashedVehicles()

        if(step > 1250):
            leftExit()
            closeRightTopBottom()
            # farRightTopBottom()
              
        step += 1
    traci.close(False)
    sys.stdout.flush()

def collisionBaselineHDVTMS(sumoBinary, LOS, ITERATION):
    print("here")
    settingUpVehicles(LOS)
    traci.start([sumoBinary, "-c", "Collision\BaselineHDV\CollisionIntersectionBaselineHDV.sumocfg",
                                "--tripinfo-output", "Collision\BaselineHDV\Output-Files\CollisionTripinfo.xml", "--ignore-route-errors"])

    TMS()