import numpy as np
import matplotlib.pyplot as plt
import timeit


def met_bisectriz(a,b,tol,No,f,type):
    i = 0
    FA = f(a)
    FB = f(b)
    salida = "No lo logré"
    while i <= No:
        if type:
            p = a+ ((b-a)/2)
        else:
            p = a - ((FA*(b-a))/(FB-FA))
        FP = f(p)
        if (FP==0) or (((b-a)/2)<tol):
            #print("Lo logré, raíz en:", p, FP)
            salida = (p, i)
            return salida
            break
        i=i+1
        if FA*FP > 0:
            a=p
            FA=FP
        else:
            b=p
            FB = FP

def NewtonRaphson(p0, tol, f, der_f, No):
    i=1
    salida="No lo logre"
    while i<No:
        p = p0 - ((f(p0))/(der_f(p0)))
        if abs(p-p0) < tol:
            #print("Lo logre. La raíz esta: ", p)
            salida = (p,i)
            break
        i = i+1
        p0 = p
    return salida


def f(l):
    return 1000000*np.exp(l) + ((435000)/(l)*((np.exp(l))-1)) - 1564000

def der_f(x):
    return 1000000*np.exp(x) + (((435000)/(x**2))*(x*np.exp(x) - np.exp(x) + 1))


def main():
    lam = np.arange(0.05,0.2,0.0001)
    a = 0.05
    b = 0.2
    tol = 1e-10
    No = 1000
    type = False

    print("********** Regula Falsi **********")
    execution_time1 = timeit.timeit(lambda: met_bisectriz(a,b,tol,No,f,type), number=10000)
    print("Tiempo de ejecución: ", execution_time1)
    raiz = met_bisectriz(a,b,tol,No,f,type)
    print("La raíz de la función es: %5.10f \nNúmero de iteraciones: %3d" % raiz)
    
    type = True

    print("********** Bisección **********")
    execution_time2 = timeit.timeit(lambda: met_bisectriz(a,b,tol,No,f,type), number=10000)
    print("Tiempo de ejecución: ", execution_time2)
    raiz = met_bisectriz(a,b,tol,No,f,type)
    print("La raíz de la función es: %5.10f \nNúmero de iteraciones: %3d" % raiz)

    print("********** Newton-Raphson **********")
    execution_time3 = timeit.timeit(lambda: NewtonRaphson(a, tol, f, der_f, No), number=10000)
    print("Tiempo de ejecución: ", execution_time3)
    raiz = NewtonRaphson(a, tol, f, der_f, No)
    print("La raíz de la función es: %5.10f \nNúmero de iteraciones: %3d" % raiz)



if __name__ == "__main__":
    main()