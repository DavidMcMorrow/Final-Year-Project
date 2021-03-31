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
from Roadworks.BaselinePenetration1.BaselinePenetration1RoadworksTMS import roadworksBaselinePenetration1
from Roadworks.BaselinePenetration2.BaselinePenetration2RoadworksTMS import roadworksBaselinePenetration2
from Roadworks.BaselinePenetration3.BaselinePenetration3RoadworksTMS import roadworksBaselinePenetration3
from Roadworks.RealTMSCAV.RealCAVRoadworksTMS import roadworksRealTMSCAV
from Roadworks.RealTMSPenetration1.RealPenetration1RoadworksTMS import RoadworksRealTMSPenetration1
from Roadworks.RealTMSPenetration2.RealPenetration2RoadworksTMS import RoadworksRealTMSPenetration2
from Roadworks.RealTMSPenetration3.RealPenetration3RoadworksTMS import RoadworksRealTMSPenetration3

from Collision.BaselineHDV.BaselineHDVCollisionTMS import collisionBaselineHDVTMS
from Collision.BaselineCAV.BaselineCAVCollisionTMS import collisionBaselineCAVTMS
from Collision.BaselinePenetration1.BaselinePenetration1CollisionTMS import collisionBaselinePenetration1
from Collision.BaselinePenetration2.BaselinePenetration2CollisionTMS import collisionBaselinePenetration2
from Collision.BaselinePenetration3.BaselinePenetration3CollisionTMS import collisionBaselinePenetration3
from Collision.RealTMSCAV.RealCAVCollisionTMS import collisionRealCAVTMS
from Collision.RealTMSPenetration1.RealPenetration1CollisionTMS import collisionRealTMSPenetration1
from Collision.RealTMSPenetration2.RealPenetration2CollisionTMS import collisionRealTMSPenetration2
from Collision.RealTMSPenetration3.RealPenetration3CollisionTMS import collisionRealTMSPenetration3


# https://www.eclipse.org/lists/sumo-user/msg02526.html

# netconvert CollisionIntersection.netccfg
# netconvert RoadworksIntersection.netccfg

def get_options():
    opt_parser = optparse.OptionParser()
    opt_parser.add_option("--nogui", action="store_true",
                         default=False, help="run the commandline version of sumo")
    options, args = opt_parser.parse_args()
    return options

def runningTheScenariosDeveloping(SCENARIO, TYPE, sumoBinary, LOS, ITERATION, REROUTINGBOOLEAN):
    if SCENARIO == "Roadworks":
        if TYPE == "Baseline-HDV":
            roadworksBaselineHDVTMS(sumoBinary, LOS, ITERATION)
        elif TYPE == "Baseline-CAV":
            roadworksBaselineCAVTMS(sumoBinary, LOS, ITERATION)
        elif TYPE == "Baseline-Penetration1":
            roadworksBaselinePenetration1(sumoBinary, LOS, ITERATION)
        elif TYPE == "Baseline-Penetration2":
            roadworksBaselinePenetration2(sumoBinary, LOS, ITERATION)
        elif TYPE == "Baseline-Penetration3":
            roadworksBaselinePenetration3(sumoBinary, LOS, ITERATION)
        elif TYPE == "TMS-CAV":
            roadworksRealTMSCAV(sumoBinary, LOS, ITERATION)
        elif TYPE == "Penetration1":
            RoadworksRealTMSPenetration1(sumoBinary, LOS, ITERATION)
        elif TYPE == "Penetration2":
            RoadworksRealTMSPenetration2(sumoBinary, LOS, ITERATION)
        elif TYPE == "Penetration3":
            RoadworksRealTMSPenetration3(sumoBinary, LOS, ITERATION)

    else:
        if TYPE == "Baseline-HDV":
            collisionBaselineHDVTMS(sumoBinary, LOS, ITERATION, REROUTINGBOOLEAN)
        elif TYPE == "Baseline-CAV":
            collisionBaselineCAVTMS(sumoBinary, LOS, ITERATION, REROUTINGBOOLEAN)
        elif TYPE == "Baseline-Penetration1":
            collisionBaselinePenetration1(sumoBinary, LOS, ITERATION, REROUTINGBOOLEAN)
        elif TYPE == "Baseline-Penetration2":
            collisionBaselinePenetration2(sumoBinary, LOS, ITERATION, REROUTINGBOOLEAN)
        elif TYPE == "Baseline-Penetration3":
            collisionBaselinePenetration3(sumoBinary, LOS, ITERATION, REROUTINGBOOLEAN)
        elif TYPE == "TMS-CAV":
            collisionRealCAVTMS(sumoBinary, LOS, ITERATION, REROUTINGBOOLEAN)
        elif TYPE == "Penetration1":
           collisionRealTMSPenetration1(sumoBinary, LOS, ITERATION, REROUTINGBOOLEAN)
        elif TYPE == "Penetration2":
            collisionRealTMSPenetration2(sumoBinary, LOS, ITERATION, REROUTINGBOOLEAN)
        elif TYPE == "Penetration3":
            collisionRealTMSPenetration3(sumoBinary, LOS, ITERATION, REROUTINGBOOLEAN)

def runningTheScenariosSimulation(SCENARIO, TYPE, sumoBinary, LOS, ITERATION, REROUTINGBOOLEAN):
    for typeOfTraffic in TYPES:
        for los in LOS:
            for i in range(0, ITERATION):
                name = typeOfTraffic + " " + los + " " + str(i)
                print("About to run ", name)
                if SCENARIO == "Roadworks":
                    if typeOfTraffic == "Baseline-HDV":
                        roadworksBaselineHDVTMS(sumoBinary, los, i)
                    elif typeOfTraffic == "Baseline-CAV":
                        roadworksBaselineCAVTMS(sumoBinary, los, i)
                    elif typeOfTraffic == "Baseline-Penetration1":
                        roadworksBaselinePenetration1(sumoBinary, los, i)
                    elif typeOfTraffic == "Baseline-Penetration2":
                        roadworksBaselinePenetration2(sumoBinary, los, i)
                    elif typeOfTraffic == "Baseline-Penetration3":
                        roadworksBaselinePenetration3(sumoBinary, los, i)
                    elif typeOfTraffic == "TMS-CAV":
                        roadworksRealTMSCAV(sumoBinary, los, i)
                    elif typeOfTraffic == "Penetration1":
                        RoadworksRealTMSPenetration1(sumoBinary, los, i)
                    elif typeOfTraffic == "Penetration2":
                        RoadworksRealTMSPenetration2(sumoBinary, los, i)
                    elif typeOfTraffic == "Penetration3":
                        RoadworksRealTMSPenetration3(sumoBinary, los, i)

                else:
                    if typeOfTraffic == "Baseline-HDV":
                        collisionBaselineHDVTMS(sumoBinary, los, i, REROUTINGBOOLEAN)
                    elif typeOfTraffic == "Baseline-CAV":
                        collisionBaselineCAVTMS(sumoBinary, los, i, REROUTINGBOOLEAN)
                    elif typeOfTraffic == "Baseline-Penetration1":
                        collisionBaselinePenetration1(sumoBinary, los, i, REROUTINGBOOLEAN)
                    elif typeOfTraffic == "Baseline-Penetration2":
                        collisionBaselinePenetration2(sumoBinary, los, i, REROUTINGBOOLEAN)
                    elif typeOfTraffic == "Baseline-Penetration3":
                        collisionBaselinePenetration3(sumoBinary, los, i, REROUTINGBOOLEAN)
                    elif typeOfTraffic == "TMS-CAV":
                        collisionRealCAVTMS(sumoBinary, los, i, REROUTINGBOOLEAN)
                    elif typeOfTraffic == "Penetration1":
                       collisionRealTMSPenetration1(sumoBinary, los, i, REROUTINGBOOLEAN)
                    elif typeOfTraffic == "Penetration2":
                        collisionRealTMSPenetration2(sumoBinary, los, i, REROUTINGBOOLEAN)
                    elif typeOfTraffic == "Penetration3":
                        collisionRealTMSPenetration3(sumoBinary, los, i, REROUTINGBOOLEAN)
                print("Finished running", name)

# SCENARIO = "Roadworks"
SCENARIO = "Collision"

TYPES = ["Baseline-HDV", "Baseline-CAV", "TMS-CAV", "Baseline-Penetration1", "Penetration1", "Baseline-Penetration2", "Penetration2", "Baseline-Penetration3", "Penetration3"]
# TYPES = ["Baseline-HDV", "Baseline-CAV", "TMS-CAV", "Baseline-Penetration1", "Penetration1", "Baseline-Penetration2", "Penetration2"]
# TYPES = [ "Penetration3"]
# LOS = ["A", "B", "C", "D"]
LOS = ["A", "B"]

ffff
# ITERATION = 1
# ITERATION = 2
ITERATION = 3

REROUTINGBOOLEAN = False

# we need to import some python modules from the $SUMO_HOME/tools directory
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")


# main entry point
if __name__ == "__main__":
    options = get_options()
    sumoBinary = checkBinary('sumo')
    # check binary
    # if options.nogui:
    #     sumoBinary = checkBinary('sumo')
    # else:
    #     sumoBinary = checkBinary('sumo-gui')

    # runningTheScenariosDeveloping(SCENARIO, TYPES[0], sumoBinary, LOS[0], ITERATION, REROUTINGBOOLEAN)
    runningTheScenariosSimulation(SCENARIO, TYPES, sumoBinary, LOS, ITERATION, REROUTINGBOOLEAN)
    