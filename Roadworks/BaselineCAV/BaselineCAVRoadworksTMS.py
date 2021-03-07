import random
import os
import numpy as np
import sys
import optparse
import traci
from xml.dom import minidom

class MRM:
    def __init__(self, ID, step):
        self.ID = ID
        self.step = step

def settingUpVehicles(LOS):
    with open('Roadworks\BaselineCAV\PreparingVehicleModels\How to use.txt') as f:
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
    files = ['Roadworks/BaselineCAV/Route-Files/L4-CV-Route.rou.xml']
    for j in range(0, len(files)):
        mydoc = minidom.parse(files[j])
        routes = mydoc.getElementsByTagName('route')
        vehicles = mydoc.getElementsByTagName('vehicle')
    
        for i in range(0, len(routes)):
            if(routes[i].getAttribute("edges").startswith("preparation")):
                route = "left-long-approaching " + routes[i].getAttribute("edges")
                routes[i].setAttribute("edges", route)
            if(routes[i].getAttribute("edges").startswith("left-short-approaching")):
                route = "left-long-approaching preparation " + routes[i].getAttribute("edges")
                routes[i].setAttribute("edges", route)
            if(routes[i].getAttribute("edges") == "left-long-approaching preparation left-short-approaching top-exit"):
                vehicles[i].setAttribute("type", "L4-CV-Left")
                routes[i].setAttribute("edges", "left-long-approaching preparation")
            if(routes[i].getAttribute("edges") == "left-long-approaching preparation left-short-approaching bottom-exit"):
                vehicles[i].setAttribute("type", "L4-CV-Right")

        with open(files[j], "w") as fs:
            fs.write(mydoc.toxml()) 
            fs.close()  

def handlingLeftApproaching(vehiclesThatTORed, listOfMRM):
    det_vehs = traci.inductionloop.getLastStepVehicleIDs("det_0")
    for veh in det_vehs:
        traci.vehicle.setRoute(veh, ["preparation", "left-short-approaching", "top-exit"])

def handlingTopRightBottom(detectors, vehiclesThatTORed, listOfMRM):
    for det in detectors:
        det_vehs = traci.inductionloop.getLastStepVehicleIDs(det)
        for veh in det_vehs:
            if findValue(vehiclesThatTORed, veh) == False and traci.vehicle.getVehicleClass(veh) != "passenger":
                result = random.randint(0,1)
                if(result == 0):
                    traci.vehicle.setVehicleClass(veh, "passenger")
                else:
                    traci.vehicle.setParameter(veh, "device.toc.requestToC", 3)
                    vehiclesThatTORed.append(veh)

def scheduleToCAfterLongDelay(delayBeforeToC, vehiclesThatTORed):
    det_vehs = traci.inductionloop.getLastStepVehicleIDs("det_7")
    for veh in det_vehs:
        if(traci.vehicle.getRoute(veh)[len(traci.vehicle.getRoute(veh))-1] ==  "right-exit" and traci.vehicle.getTypeID(veh)[:2] != "L0"):
            if(traci.vehicle.getAccumulatedWaitingTime(veh) >= delayBeforeToC and findValue(vehiclesThatTORed, veh) == False):
                traci.vehicle.requestToC(veh, 30)
                vehiclesThatTORed.append(veh)



def TMS():
    print("Running Baseline")
    step = 0
    delayBeforeToC = 100
    detectors = ["det_4", "det_5", "det_6"]
    
    listOfMRM = []
    vehiclesThatTORed = []
    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()
    
        if(step%3 == 0):
            handlingLeftApproaching(vehiclesThatTORed, listOfMRM)
            handlingTopRightBottom(detectors, vehiclesThatTORed, listOfMRM)
            scheduleToCAfterLongDelay(delayBeforeToC, vehiclesThatTORed)
            vehiclesThatTORed = removeOldToC(vehiclesThatTORed)
        step += 1

        

    traci.close(False)
    sys.stdout.flush()

def alterOutputFilesNames(LOS, ITERATION):
    safetyFile = "Roadworks\BaselineCAV\Output-Files\LOS-" + LOS + "\SSM-HDV-"+ str(ITERATION) + ".xml"
    tripFile = "Roadworks\BaselineCAV\Output-Files\LOS-" + LOS + "\Trips-HDV-"+ str(ITERATION) + ".xml"
    
    with open("Roadworks\BaselineCAV\Output-Files\SSM-CAV.xml", 'r') as firstFile:
        with open(safetyFile, 'w') as secondFile:
            for line in firstFile:
                secondFile.write(line)

    with open("Roadworks\BaselineCAV\Output-Files\RoadworksTripInfo.xml", 'r') as firstFile:
        with open(tripFile, 'w') as secondFile:
            for line in firstFile:
                secondFile.write(line)


def roadworksBaselineCAVTMS(sumoBinary, LOS, ITERATION):
    settingUpVehicles(LOS)
    flowCorrection()
    
    #traci starts sumo as a subprocess and then this script connects and runs
    traci.start([sumoBinary, "-c", "Roadworks\BaselineCAV\RoadworksBaselineCAV.sumocfg",
                "--tripinfo-output", "Roadworks\BaselineCAV\Output-Files\RoadworksTripInfo.xml", "--ignore-route-errors",
                "--device.emissions.probability", "1", "--waiting-time-memory", "300"])

    TMS()
    alterOutputFilesNames(LOS, ITERATION)

def removeOldToC(vehiclesThatTORed):
    for i in range(0, len(vehiclesThatTORed)-1):
        if(traci.vehicle.getTypeID(vehiclesThatTORed[i])[:2] == "L0"):
            vehiclesThatTORed.pop(i)
    return vehiclesThatTORed

def findValue(listOfValues, value):
    for temp in listOfValues:
        if temp == value:
            return True
    return False


