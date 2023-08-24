import numpy as np
import matplotlib.pyplot as plt

x = np.arange(0,3,0.0001)
y = 8*np.sin(x)*np.exp(-x)-1

fig, ax = plt.subplots()
ax.plot(x, y)
ax.grid(True)
plt.draw()
plt.waitforbuttonpress(0) # this will wait for indefinite time
plt.close(fig)