import numpy as np
import matplotlib.pyplot as plt

def f(l):
    return 1000000*np.exp(l) + ((435000)/(l)*((np.exp(l))-1)) - 1564000

def der_f(x):
    return 1000000*np.exp(x) + (((435000)/(x**2))*(x*np.exp(x) - np.exp(x) + 1))

def g(x):
    return np.sin(x+0.5)

def der_g(x):
    return np.cos(x+0.5)

i = 1
M = 10000
p0 = 0.2
tol = 1e-10

while i<M:
    p = p0 - ((f(p0))/(der_f(p0)))
    if abs(p-p0) < tol:
        print("Lo logre. La raíz esta: ", p)
        break
    i = i+1
    p0 = p
print("Termine. N=", i)


lam = np.arange(-np.pi/2,np.pi/2, 0.001)
p0 = 0.6
p1 = p0 - ((g(p0))/(der_g(p0)))
fig, ax = plt.subplots()
ax.plot(lam, g(lam))
ax.axhline(y=0, color="red")
ax.stem(p0, g(p0), linefmt=':')
ax.axline((p0, g(p0)), slope=der_g(p0), color="black", linestyle='--')
ax.stem(p1, g(p1), linefmt=':')
ax.axline((p1, g(p1)), slope=der_g(p1), color="green", linestyle='--')
ax.grid(True)
plt.draw()
plt.waitforbuttonpress(0) # this will wait for indefinite time
plt.close(fig)



fig, ax = plt.subplots()
a = -1.2
b = 0.8
ax.plot(lam, g(lam))
ax.axhline(y=0, color="red")
ax.stem([a, b], [g(a), g(b)], linefmt=':')
ax.axline((a, g(a)), slope=(g(b)-g(a))/(b-a), color="black", linestyle='--')
ax.grid(True)
plt.draw()
plt.waitforbuttonpress(0) # this will wait for indefinite time
plt.close(fig)