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

from Roadworks.BaselineHDV.BaselineHDVRoadworksTMS import roadworksBaselineHDVTMS
from Roadworks.BaselineCAV.BaselineCAVRoadworksTMS import roadworksBaselineCAVTMS
from Collision.BaselineHDV.BaselineHDVCollisionTMS import collisionBaselineHDVTMS
from Collision.BaselineCAV.BaselineCAVCollisionTMS import collisionBaselineCAVTMS

# https://www.eclipse.org/lists/sumo-user/msg02526.html

# netconvert CollisionIntersection.netccfg
# netconvert RoadworksIntersection.netccfg

def get_options():
    opt_parser = optparse.OptionParser()
    opt_parser.add_option("--nogui", action="store_true",
                         default=False, help="run the commandline version of sumo")
    options, args = opt_parser.parse_args()
    return options

# SCENARIO = "Roadworks"
SCENARIO = "Collision"

# TYPE = "Baseline-HDV"
TYPE = "Baseline-CAV"

# LOS = "A"
LOS = "B"
# LOS = "C"
# LOS = "D"

ITERATION = 1
# ITERATION = 2
# ITERATION = 3

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
        if TYPE == "Baseline-HDV":
            roadworksBaselineHDVTMS(sumoBinary, LOS, ITERATION)
        elif TYPE == "Baseline-CAV":
            roadworksBaselineCAVTMS(sumoBinary, LOS, ITERATION)

    else:
        if TYPE == "Baseline-HDV":
            collisionBaselineHDVTMS(sumoBinary, LOS, ITERATION)
        elif TYPE == "Baseline-CAV":
            collisionBaselineCAVTMS(sumoBinary, LOS, ITERATION)