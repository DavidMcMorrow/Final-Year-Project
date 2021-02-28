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
    #vehicleTypes = ["L2-CV-Left", "L2-Non-CV-Left", "L4-Non-CV-Left", "L4-CV-Left"]
    # vehicleTypes = ["L0-HDV-Left"]
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
            if(routes[i].getAttribute("edges") == "left-long-approaching preparation left-short-approaching right-exit"):
                vehicles[i].setAttribute("type", "L4-CV-Straight")

        with open(files[j], "w") as fs:
            fs.write(mydoc.toxml()) 
            fs.close()  

def handlingLeftApproaching(vehiclesThatTORed, listOfMRM):
    det_vehs = traci.inductionloop.getLastStepVehicleIDs("det_0")
    for veh in det_vehs:
        traci.vehicle.setRoute(veh, ["preparation", "left-short-approaching", "top-exit"])
        if(findValue(listOfMRM, veh) == False and (traci.vehicle.getVehicleClass(veh) != "custom1" or traci.vehicle.getVehicleClass(veh) != "passenger")):
            result = random.randint(0,0)
            if(result == 0):
                traci.vehicle.setVehicleClass(veh, "custom1")
            else:
                print("veh LEFT", traci.vehicle.getTypeID(veh))
                traci.vehicle.requestToC(veh, -10)
                vehiclesThatTORed.append(veh)

def handlingTopRightBottom(detectors, vehiclesThatTORed, listOfMRM):
    for det in detectors:
        det_vehs = traci.inductionloop.getLastStepVehicleIDs(det)
        for veh in det_vehs:
            # print("veh OTHER", veh)
            if(traci.vehicle.getVehicleClass(veh) != "passenger" and findValue(listOfMRM, veh) == False):
                result = random.randint(0,16)
                if(result == 0):
                    traci.vehicle.setVehicleClass(veh, "passenger")
                else:
                    print("veh OTHER", traci.vehicle.getTypeID(veh))
                    traci.vehicle.requestToC(veh, -10)
                    vehiclesThatTORed.append(veh)

def roadworksBaselineCAVTMS():
    print("Running Baseline")
    step = 0
    detectors = ["det_4", "det_5", "det_6"]
    detectors2 = ["det_2", "det_3"]
    MRMdetectors = ["det_7", "det_8", "det_9"]
    listOfMRM = []
    vehiclesThatTORed = []
    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()

        if(len(vehiclesThatTORed) > 0):
            for tor in vehiclesThatTORed:
                if(traci.vehicle.getVehicleClass(tor) != "passenger"):
                    print("MRM in", tor)
                    listOfMRM.append(MRM(tor, step-1))

        if(len(listOfMRM) > 0):
            print("MRM OCCURRED")
            for mrm in listOfMRM:
                print("checking", mrm.ID)
                print("traci.vehicle.getVehicleClass(mrm.ID)", traci.vehicle.getVehicleClass(mrm.ID))
                if(traci.vehicle.getVehicleClass(mrm.ID) != "passenger"):
                    time = step - mrm.step
                    print("time", time)
                    rand = random.randint(time, 601)
                    print("rand", rand)
                    if(rand == 601):
                        print("RE REQUESTED TOC")
                        traci.vehicle.requestToC(mrm.ID, -10)
                        mrm.step = step
                else:
                    print("REMOVING OLD MRM - 1", listOfMRM)
                    listOfMRM.remove(mrm)
                    print("REMOVING OLD MRM - 2", listOfMRM)
        vehiclesThatTORed = []
    
        if(step%3 == 0):
            handlingLeftApproaching(vehiclesThatTORed, listOfMRM)
            handlingTopRightBottom(detectors, vehiclesThatTORed, listOfMRM)
            
            # for det in detectors2:
            #     det_vehs = traci.inductionloop.getLastStepVehicleIDs(det)
            #     for veh in det_vehs:       
            #         if(traci.vehicle.getRoute(veh) == ("left-long-approaching", "preparation", "left-short-approaching", "right-exit")):
            #             traci.vehicle.setVehicleClass(veh, "custom1")
        # if(step%60 == 0):
        #     for det in detectors:
        #         det_vehs = traci.inductionloop.getLastStepVehicleIDs(det)
        #         for veh in det_vehs:
        #             if(traci.vehicle.getVehicleClass(veh) == "custom1"):
        #                 traci.vehicle.requestToC(veh, -10)
                        

        # if(step%60 == 0):
        #     det_vehs = traci.inductionloop.getLastStepVehicleIDs("det_1")
        #     for veh in det_vehs:
        #         if(traci.vehicle.getVehicleClass(veh) == "custom2"):
        #             traci.vehicle.requestToC(veh, -10)
                    
        step += 1

    traci.close(False)
    sys.stdout.flush()

def alterOutputFilesNames(LOS, ITERATION):
    safetyFile = "Roadworks\BaselineCAV\Output-Files\LOS-" + LOS + "\SSM-HDV-"+ str(ITERATION) + ".xml"
    tripFile = "Roadworks\BaselineCAV\Output-Files\LOS-" + LOS + "\Trips-HDV-"+ str(ITERATION) + ".xml"
    
    
    count = 0 
    with open("Roadworks\BaselineCAV\Output-Files\SSM-CAV.xml", 'r') as firstFile:
        with open(safetyFile, 'w') as secondFile:
            for line in firstFile:
                secondFile.write(line)

    with open("Roadworks\BaselineCAV\Output-Files\RoadworksTripInfo.xml", 'r') as firstFile:
        with open(tripFile, 'w') as secondFile:
            for line in firstFile:
                secondFile.write(line)


def runBaselineCAV(sumoBinary, LOS, ITERATION):
    settingUpVehicles(LOS)
    flowCorrection()
    
    
    #traci starts sumo as a subprocess and then this script connects and runs
    traci.start([sumoBinary, "-c", "Roadworks\BaselineCAV\RoadworksBaselineCAV.sumocfg",
                "--tripinfo-output", "Roadworks\BaselineCAV\Output-Files\RoadworksTripInfo.xml", "--ignore-route-errors",
                "--device.emissions.probability", "1"])

    roadworksBaselineCAVTMS()
    alterOutputFilesNames(LOS, ITERATION)

def findValue(listOfValues, value):
    for temp in listOfValues:
        if temp.ID == value:
            return True
    return False


