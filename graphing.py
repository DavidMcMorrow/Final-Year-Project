from xml.dom import minidom
import matplotlib
import matplotlib.pyplot as plt
import numpy as np

mydoc1 = minidom.parse('SSM-Car-Route-Left2Right-HDV.xml')

flowOneIntiaitedConflicts = mydoc1.getElementsByTagName('conflict')

print('number of flowOneIntiaitedConflicts:')
print(len(flowOneIntiaitedConflicts))

mydoc2 = minidom.parse('SSM-EV-Route-Left2Right.xml')

flowTwoIntiaitedConflicts = mydoc2.getElementsByTagName('conflict')

print('number of flowTwoIntiaitedConflicts:')
print(len(flowTwoIntiaitedConflicts))

import matplotlib.pyplot as plt
   
Flow = ['Flow One','Flow Two']
NumberOfConflictsInitiated = [len(flowOneIntiaitedConflicts), len(flowTwoIntiaitedConflicts)]

plt.bar(Flow, NumberOfConflictsInitiated)
plt.title('Number of clnflicts and who started it')
plt.xlabel('Flow')
plt.ylabel('Number of Conflicts')
plt.show()