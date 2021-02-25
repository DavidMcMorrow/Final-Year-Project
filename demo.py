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
    files = ['Roadworks/Route-Files/L2-CV-Route.rou.xml'
    , 'Roadworks/Route-Files/L2-Non-CV-Route.rou.xml', 'Roadworks/Route-Files/L4-Non-CV-Route.rou.xml',
    'Roadworks/Route-Files/L4-CV-Route.rou.xml'
    ]
    vehicleTypes = ["L2-CV-Left", "L2-Non-CV-Left", "L4-Non-CV-Left", "L4-CV-Left"]
    for j in range(0, len(files)):
        mydoc = minidom.parse(files[j])
        routes = mydoc.getElementsByTagName('route')
        vehicles = mydoc.getElementsByTagName('vehicle')
    
        for i in range(0, len(routes)):
            if(routes[i].getAttribute("edges") == "left-long-approaching preparation left-short-approaching top-exit"):
                vehicles[i].setAttribute("type", vehicleTypes[j])
                

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
                        line = line + " -p " + str(2.37)
                    if LOS == "B":
                        line = line + " -p " + str(1.46)
                    if LOS == "C":
                        line = line + " -p " + str(1.27)
                    if LOS == "D":
                        line = line + " -p " + str(1.18)
                    if LOS == "Test":
                        line = line + " -p " + str(0.7)
                    
                print("line", line)
                os.system(line)

SCENARIO = "Roadworks"
# SCENARIO = "Collision"
LOS = "Test"

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
        #flowCorrection()
        #traci starts sumo as a subprocess and then this script connects and runs
        traci.start([sumoBinary, "-c", "Roadworks/RoadworksIntersection.sumocfg",
                             "--tripinfo-output", "RoadworksTripinfo.xml", "--ignore-route-errors"])
        runRoadWorksTMS()
        

    if SCENARIO == "Collision":
        traci.start([sumoBinary, "-c", "Collision/CollisionIntersection.sumocfg",
                             "--tripinfo-output", "CollisionTripinfo.xml", "--ignore-route-errors"])
        runCollisionTMS()