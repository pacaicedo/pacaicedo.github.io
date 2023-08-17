def factorial(x):
    output = 1
    for k in range(1,x+1):
        output = output*k
    return output

print(factorial(5))

def sin_taylor_expansion(x,n):
    pi = 3.141592653589793238462643383279502884197169399375105820974944
    x = pi*x/180
    output = 0
    for k in range(0, n):
        term = (((-1)**k)/factorial(2*k + 1))*(x**(2*k+1))
        output = output+term
    return output

v_est = sin_taylor_expansion(30,5)

print(v_est)

print("Error Relativo:", abs(0.5-v_est)/0.5)