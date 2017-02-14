#!/usr/bin/env python
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
from pylab import cm
import matplotlib.pyplot as plt


fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
x = [0,2,4,6,8,10,12]
y = [4,6,8,10]
#x=4*x
#y=[4,4,4,4,4,4,4,6,6,6,6,6,6,6,8,8,8,8,8,8,8,10,10,10,10,10,10,10]
X, Y = np.meshgrid(x, y)
print "size of X is: ", X.shape
print "size of Y is: ", Y.shape
Z=[]
Z.append([-58,-61,-66,-83,-69,-63,-58])
Z.append([-66, -69, -74, -86, -74, -69.5, -66.5])
Z.append([-75, -76, -81, -90, -85, -75.5, -72])
Z.append([-76, -80, -84, -91, -88, -83, -78])
print Z
#ax.plot_surface(X, Y, Z,cmap=cm.RdBu,vmin=-100, vmax=-50)
ax.plot_trisurf(X.flatten(), Y.flatten(), np.array(Z).flatten(), color="Red", cmap='winter', shade=True, linewidth="0.7")
ax.set_xlabel('X coordinate')
ax.set_ylabel('Y coordinate')
ax.set_zlabel('Power')

# Plotting Power vs x,y,z in the case of single antenna
"""fig2 = plt.figure()
ax2 = fig2.add_subplot(111, projection='3d')

Z2 = []
Z2.append([-58,-59.5,-65,-71,-76,-80,-84])
Z2.append([-65,-67,-71,-75.5,-80,-83,-85.5])
Z2.append([-72,-73,-75,-79,-82,-84,-87])
Z2.append([-75,-77,-80,-81,-84,-85.5,-90])

ax2.plot_trisurf(X.flatten(), Y.flatten(), np.array(Z2).flatten(), color="Red", cmap='hot', shade=True, linewidth="0.7")
ax2.set_xlabel('X coordinate')
ax2.set_ylabel('Y coordinate')
ax2.set_zlabel('Power')"""

plt.show()