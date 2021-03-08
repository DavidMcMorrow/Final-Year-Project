import random
import os
import traci

# def settingUpVehicles1(filename, LOS):
#     print("HERE in gen fucntion")
#     with open('Roadworks\BaselineCAV\PreparingVehicleModels\How to use.txt') as f:
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



def removeOldToC(vehiclesThatTORed):
    for veh in vehiclesThatTORed:
        if(traci.vehicle.getTypeID(veh)[:2] == "L0"):
            vehiclesThatTORed.remove(veh)
    return vehiclesThatTORed


def reRouteClockWiseFirst(edge):
    newRoute = []
    if(edge == "top"):
        newRoute = ["top-approaching", "bottom-exit"]
    elif(edge == "right"):
        newRoute = ["right-approaching", "bottom-exit"]
    elif(edge == "bottom"):
        newRoute = ["bottom-approaching", "top-exit"]
    return newRoute

def reRouteClockWiseSecond(edge):
    newRoute = []
    if(edge == "top"):
        newRoute = ["top-approaching", "bottom-exit"]
    elif(edge == "right"):
        newRoute = ["right-approaching", "top-exit"]
    elif(edge == "bottom"):
        newRoute = ["bottom-approaching", "top-exit"]
    return newRoute

    