print(2**4)

mantisa = []

def decimal2binario(a):
    t001 = a
    while t001//2 > 0:
        mantisa.append(t001%2)
        t001 = t001//2
    mantisa.append(t001%2)
    salida = (' '.join(str(e) for e in mantisa))
    print(salida)
    return salida

a = "1011100100010000000000000000000000000000000000000000"
n = len(a)

decimal2binario(263)