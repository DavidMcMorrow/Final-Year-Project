import os
import sys
import optparse
from sumolib import checkBinary  # Checks for the binary in environ vars
import traci
import importlib
from xml.dom import minidom
import random


from Roadworks.RoadworksTMS import runRoadWorksTMS
from Collision.CollisionTMS import runCollisionTMS

# https://www.eclipse.org/lists/sumo-user/msg02526.html

# netconvert CollisionIntersection.netccfg
# netconvert RoadworksIntersection.netccfg

def get_options():
    opt_parser = optparse.OptionParser()
    opt_parser.add_option("--nogui", action="store_true",
                         default=False, help="run the commandline version of sumo")
    options, args = opt_parser.parse_args()
    return options

def flowCorrection():
    files = ['Roadworks/Route-Files/L0-HDV-Route.rou.xml']
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
                # routes[i].setAttribute("edges", "left-long-approaching preparation")

        with open(files[j], "w") as fs:
            fs.write(mydoc.toxml()) 
            fs.close()  

def settingUpVehicles(LOS):
    with open('PreparingVehicleModels\How to use.txt') as f:
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

SCENARIO = "Roadworks"
# SCENARIO = "Collision"

LOS = "A"
# LOS = "B"
# LOS = "C"
# LOS = "D"
# LOS = "Test"

# we need to import some python modules from the $SUMO_HOME/tools directory
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")


# main entry point
if __name__ == "__main__":
    options = get_options()

    # check binary
    if options.nogui:
        sumoBinary = checkBinary('sumo')
    else:
        sumoBinary = checkBinary('sumo-gui')

    if SCENARIO == "Roadworks":
        settingUpVehicles(LOS)
        flowCorrection()
        #traci starts sumo as a subprocess and then this script connects and runs
        traci.start([sumoBinary, "-c", "Roadworks/RoadworksIntersection.sumocfg",
                             "--tripinfo-output", "RoadworksTripinfo.xml", "--ignore-route-errors"])
        runRoadWorksTMS()
        

    if SCENARIO == "Collision":
        traci.start([sumoBinary, "-c", "Collision/CollisionIntersection.sumocfg",
                             "--tripinfo-output", "CollisionTripinfo.xml", "--ignore-route-errors", "--emission-output", "TotalEmisions.xml"])
        runCollisionTMS()



# Two SCENARIO
#     Two Baselines in each
#         3 Traffic Volumes
#     Actual TMS
#         3 Pentration Rates
#             3 Volumes
