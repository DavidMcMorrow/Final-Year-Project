import os
import sys
import optparse
from sumolib import checkBinary  # Checks for the binary in environ vars
import traci
import importlib

from Roadworks.RoadworksTMS import runRoadWorksTMS
from Collision.CollisionTMS import runCollisionTMS


# netconvert intersection.netccfg
# netconvert CollisionIntersection.netccfg
# netconvert RoadworksIntersection.netccfg

def get_options():
    opt_parser = optparse.OptionParser()
    opt_parser.add_option("--nogui", action="store_true",
                         default=False, help="run the commandline version of sumo")
    options, args = opt_parser.parse_args()
    return options

# contains TraCI control loop
def run():
    step = 0
    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()
        print(step)
        step += 1

    traci.close()
    sys.stdout.flush()


SCENARIO = "Roadworks"
# SCENARIO = "Collision"

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
        # traci starts sumo as a subprocess and then this script connects and runs
        traci.start([sumoBinary, "-c", "Roadworks/RoadworksIntersection.sumocfg",
                             "--tripinfo-output", "RoadworksTripinfo.xml", "--ignore-route-errors"])
        runRoadWorksTMS()
        

    if SCENARIO == "Collision":
        traci.start([sumoBinary, "-c", "Collision/CollisionIntersection.sumocfg",
                             "--tripinfo-output", "CollisionTripinfo.xml", "--ignore-route-errors"])
        runCollisionTMS()