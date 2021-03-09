import random
import os
import traci
from xml.dom import minidom

def settingUpVehicles(SCENARIO, USECASEFOLDER, LOS):
    textFileToRun = SCENARIO + USECASEFOLDER + "\PreparingVehicleModels\How to use.txt"
    with open(textFileToRun) as f:
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

def removeOldToC(vehiclesThatTORed):
    for veh in vehiclesThatTORed:
        if(traci.vehicle.getTypeID(veh)[:2] == "L0"):
            vehiclesThatTORed.remove(veh)
    return vehiclesThatTORed

def collisionReRouteClockWiseFirst(edge):
    newRoute = []
    if(edge == "top"):
        newRoute = ["top-approaching", "bottom-exit"]
    elif(edge == "right"):
        newRoute = ["right-approaching", "bottom-exit"]
    elif(edge == "bottom"):
        newRoute = ["bottom-approaching", "top-exit"]
    
    return newRoute

def collisionReRouteClockWiseSecond(edge):
    newRoute = []
    if(edge == "top"):
        newRoute = ["top-approaching", "bottom-exit"]
    elif(edge == "right"):
        newRoute = ["right-approaching", "top-exit"]
    elif(edge == "bottom"):
        newRoute = ["bottom-approaching", "top-exit"]
    return newRoute

def roadworksReRouting(target):
    newRoute = []
    if(target == "top-exit"):
        newRoute = ["left-long-approaching", "preparation", "left-short-approaching", "right-exit"]
    elif(target == "right-exit"):
        newRoute = ["left-long-approaching", "preparation", "left-short-approaching", "bottom-exit"]
    return newRoute

def baselineAlterOutputFiles(SCENARIO, BASELINE, LOS, ITERATION, VEHICLETYPES):
    for vehType in VEHICLETYPES:
        newSafetyFile = SCENARIO + "\Baseline" + BASELINE  + "\Output-Files\LOS-" + LOS + "\SSM-" + vehType + "-"+ str(ITERATION) + ".xml"        
        oldSafetyFile = SCENARIO + "\Baseline" + BASELINE + "\Output-Files\SSM-" + vehType + ".xml"

        if(os.path.exists(oldSafetyFile)):
            with open(oldSafetyFile, 'r') as firstFile:
                with open(newSafetyFile, 'w') as secondFile:
                    for line in firstFile:
                        secondFile.write(line)
    
    newTripFile = SCENARIO + "\Baseline" + BASELINE  + "\Output-Files\LOS-" + LOS + "\Trips-" + str(ITERATION) + ".xml"
    oldTripFile = SCENARIO + "\Baseline" + BASELINE + "\Output-Files\TripInfo.xml"

    with open(oldTripFile, 'r') as firstFile:
        with open(newTripFile, 'w') as secondFile:
            for line in firstFile:
                secondFile.write(line)

def flowCorrection(files, vehiclesTypes, baseline):
    print("HERERE")
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
            elif(routes[i].getAttribute("edges").startswith("left-short-approaching")):
                route = "left-long-approaching preparation " + routes[i].getAttribute("edges")
                routes[i].setAttribute("edges", route)

            if(baseline == "HDV"):
                if(routes[i].getAttribute("edges") == "left-long-approaching preparation left-short-approaching top-exit"):
                    temp = vehiclesTypes[j] + "-Left"
                    vehicles[i].setAttribute("type", temp)
                    routes[i].setAttribute("edges", "left-long-approaching preparation")
                elif(routes[i].getAttribute("edges") == "left-long-approaching preparation left-short-approaching right-exit"):
                    temp = vehiclesTypes[j] + "-Straight"
                    vehicles[i].setAttribute("type", temp)
            else:
                if(routes[i].getAttribute("edges") == "left-long-approaching preparation left-short-approaching top-exit"):
                    temp = vehiclesTypes[j] + "-Left"
                    vehicles[i].setAttribute("type", temp)
                    routes[i].setAttribute("edges", "left-long-approaching preparation")
                elif(routes[i].getAttribute("edges") == "left-long-approaching preparation left-short-approaching bottom-exit"):
                    temp = vehiclesTypes[j] + "-Right"
                    vehicles[i].setAttribute("type", temp)
                    
        with open(files[j], "w") as fs:
            fs.write(mydoc.toxml()) 
            fs.close()  

def removeVehiclesThatPassCenter(vehiclesApproachingClosure):
    for vehicle in vehiclesApproachingClosure:
        temp1 = vehicle in traci.vehicle.getIDList()
        if temp1 == True:
            temp = traci.vehicle.getLaneID(vehicle)[:7]
            if(temp == ":center"):
                vehiclesApproachingClosure.remove(vehicle)
        else:
            vehiclesApproachingClosure.remove(vehicle)
    return vehiclesApproachingClosure

