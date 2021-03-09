import os
import numpy as np
import sys
import optparse
from sumolib import checkBinary  # Checks for the binary in environ vars
import traci
import matplotlib.pyplot as plt
import random
from xml.dom import minidom

sys.path.append('c:/Users/david/OneDrive/Fifth Year/Final Year Project/SUMO/Simulation Stuff/Final-Year-Project')

from generalFunctions import roadworksReRouting, baselineAlterOutputFiles, settingUpVehicles

# def settingUpVehicles(LOS):
#     with open('Roadworks\BaselineHDV\PreparingVehicleModels\How to use.txt') as f:
#         for line in f:
#             if(line != "\n"):
#                 line = 'cmd /c ' + line
#                 if(line.find('python PreparingVehicleModels/randomTrips.py') != -1):
#                     line = line.rstrip()
#                     line = line + " " + str(random.randint(0,9))
#                     if LOS == "A":
#                         line = line + " -p " + str(1.86)
#                     if LOS == "B":
#                         line = line + " -p " + str(1.25)
#                     if LOS == "C":
#                         line = line + " -p " + str(1.07)
#                     if LOS == "D":
#                         line = line + " -p " + str(0.94)
#                     if LOS == "Test":
#                         line = line + " -p " + str(0.7)
                        
#                 os.system(line)

def flowCorrection():
    files = ['Roadworks/BaselineHDV/Route-Files/L0-HDV-Route.rou.xml']
    for j in range(0, len(files)):
        mydoc = minidom.parse(files[j])
        routes = mydoc.getElementsByTagName('route')
        vehicles = mydoc.getElementsByTagName('vehicle')
    
        for i in range(0, len(routes)):
            if(routes[i].getAttribute("edges")[:1] == "l" and routes[i].getAttribute("edges")[-1] != "t"):
                result = random.randint(0, 2)
                if result == 0:
                    routes[i].setAttribute("edges", "left-long-approaching preparation left-short-approaching bottom-exit")
                elif result == 1:
                    routes[i].setAttribute("edges", "left-long-approaching preparation left-short-approaching right-exit")
                else: 
                    routes[i].setAttribute("edges", "left-long-approaching preparation left-short-approaching top-exit")

            if(routes[i].getAttribute("edges").startswith("p")):
                route = "left-long-approaching " + routes[i].getAttribute("edges")
                routes[i].setAttribute("edges", route)
            if(routes[i].getAttribute("edges").startswith("left-short-approaching")):
                route = "left-long-approaching preparation " + routes[i].getAttribute("edges")
                routes[i].setAttribute("edges", route)
            if(routes[i].getAttribute("edges") == "left-long-approaching preparation left-short-approaching top-exit"):
                vehicles[i].setAttribute("type", "L0-HDV-Left")
                routes[i].setAttribute("edges", "left-long-approaching preparation")
            if(routes[i].getAttribute("edges") == "left-long-approaching preparation left-short-approaching right-exit"):
                vehicles[i].setAttribute("type", "L0-HDV-Straight")

            # print("routes[i].getAttribute(edges)[:0]", routes[i].getAttribute("edges")[:1])
        with open(files[j], "w") as fs:
            fs.write(mydoc.toxml()) 
            fs.close()  

def handlingLeftBlockedApproach():
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

def allowingStraightVehiclesInRightLane():
    detectors = ["det_2", "det_3"]
    for det in detectors:
        det_vehs = traci.inductionloop.getLastStepVehicleIDs(det)
        for veh in det_vehs:       
            if(traci.vehicle.getRoute(veh) == ("left-long-approaching", "preparation", "left-short-approaching", "right-exit")):
                traci.vehicle.setVehicleClass(veh, "passenger")

def majorDelayDetection(delayBeforeReoute, vehiclesApproachingClosure):
    detectors = ["left-long-approaching_0", "left-long-approaching_1", "left-long-approaching_2"]
    for det in detectors:
        det_vehs = traci.inductionloop.getLastStepVehicleIDs(det)
        for veh in det_vehs:
            temp1 = traci.vehicle.getRoute(veh)[len(traci.vehicle.getRoute(veh))-1]
            temp2 = veh in vehiclesApproachingClosure
            if ((temp1 !=  "bottom-exit") and (temp2 == False)):
                vehiclesApproachingClosure.append(veh)
       
    for veh in vehiclesApproachingClosure:
        temp1 = traci.vehicle.getRoute(veh)[len(traci.vehicle.getRoute(veh))-1]
        if traci.vehicle.getAccumulatedWaitingTime(veh) > delayBeforeReoute:
            print("WAITED TOO LONG", veh)
            vehiclesApproachingClosure = reRoutingVehicles(veh, temp1, vehiclesApproachingClosure)
    return vehiclesApproachingClosure

def reRoutingVehicles(veh, target, vehiclesApproachingClosure):
    rerouteResult = random.randint(0,3) ## NEED TO CONSIDER THIS PROBABILITY MORE
    if(rerouteResult == 0):
        traci.vehicle.setVehicleClass(veh, "passenger")
        traci.vehicle.setRoute(veh, roadworksReRouting(target))
        vehiclesApproachingClosure.remove(veh)
        # vehiclesApproachingClosure = removeVehiclesThatAreReRouted(vehiclesApproachingClosure, veh)
    return vehiclesApproachingClosure

def TMS():
    print("Running Baseline")
    step = 0
    delayBeforeReoute = 120 
    vehiclesApproachingClosure = []
    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()
        vehiclesApproachingClosure = removeVehiclesThatPassCenter(vehiclesApproachingClosure)
        if(step%3 == 0):
            handlingLeftBlockedApproach()
            allowingStraightVehiclesInRightLane()
            vehiclesApproachingClosure = majorDelayDetection(delayBeforeReoute, vehiclesApproachingClosure)
        step += 1
    traci.close(False)
    sys.stdout.flush()

def roadworksBaselineHDVTMS(sumoBinary, LOS, ITERATION):
    # settingUpVehicles(LOS)
    settingUpVehicles("Roadworks", "\BaselineHDV", LOS)
    flowCorrection()
    
    #traci starts sumo as a subprocess and then this script connects and runs
    traci.start([sumoBinary, "-c", "Roadworks\BaselineHDV\RoadworksBaselineHDV.sumocfg",
                "--tripinfo-output", "Roadworks\BaselineHDV\Output-Files\TripInfo.xml", "--ignore-route-errors",
                "--device.emissions.probability", "1", "--waiting-time-memory", "300"])

    TMS()
    baselineAlterOutputFiles("Roadworks", "HDV", LOS, ITERATION, ["HDV"])
    
def removeVehiclesThatPassCenter(vehiclesApproachingClosure):
    for vehicle in vehiclesApproachingClosure:
        temp = traci.vehicle.getLaneID(vehicle)[:7]
        if(temp == ":center"):
            vehiclesApproachingClosure.remove(vehicle)
    return vehiclesApproachingClosure

# def removeVehiclesThatAreReRouted(vehiclesApproachingClosure, veh):
#     for waitingVehicle in vehiclesApproachingClosure:
#         if(waitingVehicle == veh):
#             vehiclesApproachingClosure.remove(waitingVehicle)
#     return vehiclesApproachingClosure


# automate file name creation
# do the same for trip-info.xml