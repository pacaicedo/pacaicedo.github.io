import numpy as np
import timeit
import matplotlib.pyplot as plt

def f(l):
    return 1000000*np.exp(l) + ((435000)/(l)*((np.exp(l))-1)) - 1564000

def met_bisectriz(a,b,tol,g,No):
    i = 0
    FA = g(a)
    while i <= No:
        p = a+ ((b-a)/2)

        FP = g(p)
        if (FP==0) or (((b-a)/2)<tol):
            #print("Lo logré, raíz en:", p, FP)
            return p,i
            break
        i=i+1
        if FA*FP > 0:
            a=p
            FA=FP
        else:
            b=p
    print("Termine: ", i)

def met_regula_falsi(a,b,tol,g,No):
    i = 0
    FA = g(a)
    FB = g(b)
    while i <= No:
        p = a - ((FA*(b-a))/(FB-FA))
        FP = g(p)
        if (FP==0) or (((b-a)/2)<tol):
            #print("Lo logré, raíz en:", p, FP)
            return p,i
            break
        i=i+1
        if FA*FP > 0:
            a=p
            FA=FP
        else:
            b=p
            FB=FP
    print("Termine: ", i)    

def main():
    a = 0.05
    b = 0.2
    tol = 1e-10
    No = 1000
    raiz1= met_bisectriz(a,b,tol,f,No)
    raiz2= met_regula_falsi(a,b,tol,f,No)

    tiempo_ejecucion01 = timeit.timeit(lambda: met_bisectriz(a,b,tol,f,No), number=10000 )
    tiempo_ejecucion02 = timeit.timeit(lambda: met_regula_falsi(a,b,tol,f,No), number=10000 )

    print("***** Bisección *****\nRaíz Ubicada en: %5.10f \nNecesité %3d iteraciones" % raiz1)
    print("Tiempo ejecución: ", tiempo_ejecucion01)
    print("***** Regula Falsi *****\nRaíz Ubicada en: %5.10f \nNecesité %3d iteraciones" % raiz2)
    print("Tiempo ejecución: ", tiempo_ejecucion02)5

     

if __name__ == "__main__":
    main()