import os
import numpy as np
import sys
import optparse
from sumolib import checkBinary  # Checks for the binary in environ vars
import traci
import matplotlib.pyplot as plt
import random
from xml.dom import minidom

def settingUpVehicles(LOS):
    with open('Roadworks\BaselineHDV\PreparingVehicleModels\How to use.txt') as f:
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

def flowCorrection():
    files = ['Roadworks/BaselineHDV/Route-Files/L0-HDV-Route.rou.xml']
    #vehicleTypes = ["L2-CV-Left", "L2-Non-CV-Left", "L4-Non-CV-Left", "L4-CV-Left"]
    # vehicleTypes = ["L0-HDV-Left"]
    for j in range(0, len(files)):
        mydoc = minidom.parse(files[j])
        routes = mydoc.getElementsByTagName('route')
        vehicles = mydoc.getElementsByTagName('vehicle')
    
        for i in range(0, len(routes)):
            if(routes[i].getAttribute("edges").startswith("p")):
                route = "left-long-approaching " + routes[i].getAttribute("edges")
                routes[i].setAttribute("edges", route)
            if(routes[i].getAttribute("edges").startswith("left-short-approaching")):
                route = "left-long-approaching preparation " + routes[i].getAttribute("edges")
                routes[i].setAttribute("edges", route)
            if(routes[i].getAttribute("edges") == "left-long-approaching preparation left-short-approaching top-exit"):
                vehicles[i].setAttribute("type", "L0-HDV-Left")
                routes[i].setAttribute("edges", "left-long-approaching preparation")
            if(routes[i].getAttribute("edges") == "left-long-approaching preparation left-short-approaching bottom-exit"):
                vehicles[i].setAttribute("type", "L0-HDV-Right")

        with open(files[j], "w") as fs:
            fs.write(mydoc.toxml()) 
            fs.close()  



def roadworksBaselineHDVTMS():
    print("Running Baseline")
    step = 0
    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()
        if(step%3 == 0):
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

            detectors = ["det_2", "det_3"]
            for det in detectors:
                det_vehs = traci.inductionloop.getLastStepVehicleIDs(det)
                for veh in det_vehs:       
                    if(traci.vehicle.getRoute(veh) == ("left-long-approaching", "preparation", "left-short-approaching", "right-exit")):
                        traci.vehicle.setVehicleClass(veh, "custom1")
        step += 1

    traci.close()
    sys.stdout.flush()

def runBaselineHDV(sumoBinary, LOS):
    settingUpVehicles(LOS)
    flowCorrection()
    #traci starts sumo as a subprocess and then this script connects and runs
    traci.start([sumoBinary, "-c", "Roadworks\BaselineHDV\RoadworksBaselineHDV.sumocfg",
                "--tripinfo-output", "Roadworks\BaselineHDV\Output-Files\RoadworksTripinfoNEW.xml", "--ignore-route-errors"])
    roadworksBaselineHDVTMS()