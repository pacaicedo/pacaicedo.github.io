import numpy as np
import matplotlib.pyplot as plt

lam = np.arange(0.05,0.2,0.0001)

def f(l):
    return 1000000*np.exp(l) + ((435000)/(l)*((np.exp(l))-1)) - 1564000

valor = np.array([0.05, 0.2])
print(f(valor))

fig, ax = plt.subplots()
ax.plot(lam, f(lam))
ax.stem(valor, f(valor), linefmt=':')
ax.grid(True)
plt.show()



a = 0.05
b = 0.2
tol = 1e-2
No = 1000
i=1


vec_a=[]
vec_b=[]
vec_p=[]


FA = f(a)
while i <= No:
    p = a+ ((b-a)/2)
    vec_a.append(a)
    vec_b.append(b)
    vec_p.append(p)

    FP = f(p)
    if (FP==0) or (((b-a)/2)<tol):
        print("Lo logré, raíz en:", p, FP)
        break
    i=i+1
    if FA*FP > 0:
        a=p
        FA=FP
    else:
        b=p
print("Termine: ", i)

print(len(vec_a))

fig, ax = plt.subplots()
ax.plot(vec_a)
ax.plot(vec_b)
ax.plot(vec_p)
plt.show()

fig, ax = plt.subplots()
ax.plot(lam, f(lam))
ax.stem(np.array(vec_p), f(np.array(vec_p)), linefmt=':')
ax.grid(True)
plt.show()

