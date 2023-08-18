import numpy as np
import matplotlib.pyplot as plt

x = np.arange(0,5,0.01)
f_x = 3*x-4

t = np.arange(-3,4, 0.01)
f_t = (t**2)-(t)-6

#fig, ax = plt.subplots()
#ax.plot(t, f_t)
#plt.grid(True)
#plt.show()


x1 = np.arange(-20,20,0.01)
f1_x=x1
f2_x= 10*np.cos(x1)

fig, ax = plt.subplots()
ax.plot(x1, f1_x)
ax.plot(x1, f2_x)
plt.grid(True)
plt.show()