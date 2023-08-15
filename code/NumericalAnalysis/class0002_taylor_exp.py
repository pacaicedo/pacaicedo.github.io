def taylor_exp_ln_c2(x):
    return 0.69315 + (0.5*(x-2)) - ((1.0/8.0)*((x-2)**2)) + ((1.0/24.0)*((x-2)**3)) - ((1.0/64.0)*((x-2)**4))

def taylor_expansion_ln(x):
    return ((1/1)*(x-1))-((1/(2*(1**2)))*(x-1)**2)+ ((2/(6*(1**3)))*(x-1)**3)-((6/(24*(1**4)))*(x-1)**4)

def error_exp_taylor_ln_c2(xi):
    return -0.118098*(xi**(-5))

def error_taylor_expansion(x):
    return ((24*x**(-5))/120)*(0.1**5)

print(taylor_exp_ln_c2(1.1))
print(taylor_expansion_ln(1.1))

import numpy as np
import matplotlib.pyplot as plt

v1 = np.arange(1,1.1,0.00001)
v2 = np.arange(1.1,2,0.00001)

e1 = error_taylor_expansion(v1)
e2 = error_exp_taylor_ln_c2(v2)

fig, ax = plt.subplots()
ax.plot(v1,e1)
ax.plot(v2,e2)
plt.show()