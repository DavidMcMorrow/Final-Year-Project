import os
import sys
import optparse
from sumolib import checkBinary  # Checks for the binary in environ vars
import traci



def get_options():
    opt_parser = optparse.OptionParser()
    opt_parser.add_option("--nogui", action="store_true",
                         default=False, help="run the commandline version of sumo")
    options, args = opt_parser.parse_args()
    return options

# contains TraCI control loop
def run():
    step = emisionCount = 0
    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()
        print(step)
        #if(step == 20):
            # traci.vehicle.setParameter("v0", "device.toc.requestToC", 2)
            # traci.vehicle.setRouteID("v0", "route0")
            # traci.vehicle.requestToC("v0", 200)
            # print("ID List", traci.vehicle.getIDList())
            # traci.vehicle.setParameter("Car-Route-Left2Right-HDV", "device.toc.requestToC", 2)
            # traci.vehicle.setRouteID("Car-Route-Left2Right-HDV", "route0")
            # traci.vehicle.requestToC("Car-Route-Left2Right-HDV", 200)
           

        det_vehs = traci.inductionloop.getLastStepVehicleIDs("det_0")
        for veh in det_vehs:
            print(veh)
            traci.vehicle.changeLane("v0", 2, 25)
            traci.vehicle.changeLane("Car-Route-Left2Right-HDV", 2, 25)

        det_leftRight = traci.inductionloop.getLastStepVehicleIDs("det_1")
        for veh in det_leftRight:
            print(veh)
            # traci.vehicle.changeLane(veh, 2, 2)
            traci.vehicle.requestToC(veh, 1)
            emisionCount = emisionCount + traci.vehicle.getCO2Emission(veh)
            

        step += 1

    print("emisionCount", emisionCount)

    traci.close()
    sys.stdout.flush()


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

    # traci starts sumo as a subprocess and then this script connects and runs
    traci.start([sumoBinary, "-c", "intersection.sumocfg",
                             "--tripinfo-output", "tripinfo.xml"])
    run()