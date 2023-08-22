import numpy as np
import matplotlib.pyplot as plt

def f(l1):
    return -1564000 + 1000000*(np.exp(l1)) + ((435000)/(l1))*((np.exp(l1))-1)

lam = np.arange(0.05, 0.2, 0.0001)

a = 0.05
b = 0.2
M = 10
k=0
hist_a=[]
hist_b=[]
hist_p=[]

while k<M:
    k=k+1
    p = (a+b)/2
    hist_a.append(a)
    hist_b.append(b)
    hist_p.append(p)
    if f(p)==0:
        break
    if f(a)*f(p) > 0:
        a=p
    else:
        b=p

print(p)

p1 = (a+p)/2

fig, ax = plt.subplots()
ax.plot(lam, f(lam))
ax.stem(np.array([a,b]), f(np.array([a,b])), linefmt=':')
ax.stem(p, f(p), linefmt=':')
ax.stem(p1, f(p1), linefmt=':')
ax.grid(True)
plt.show()

fig, ax = plt.subplots()
ax.plot(hist_a)
ax.plot(hist_b)
ax.plot(hist_p)
ax.grid(True)
plt.show()