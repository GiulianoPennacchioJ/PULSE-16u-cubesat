# Soluzione di primo ordine del Korsch: focale 700 mm e Petzval nullo (campo piatto)
import numpy as np
from scipy.optimize import brentq
F = 700.0
def soluzione(f1, d1, e):
    m2 = (d1+e)/(f1-d1); fps = f1*m2
    R2 = 2/(1/(f1-d1) - 1/(d1+e))
    m3 = F/fps
    # Petzval: 1/R1 - 1/R2 + 1/R3 = 0  ->  R3
    inv_R3 = 1/R2 - 1/(2*f1)
    R3 = 1/inv_R3
    # terziario: 2/R3 = 1/s3 + 1/(m3 s3) -> s3
    s3 = (1 + 1/m3)*R3/2
    return dict(f1=f1, d1=d1, e=e, R1=2*f1, R2=R2, R3=R3, m2=m2, m3=m3, s3=s3, s3p=m3*s3,
                z3=e+s3, zi=e+s3-m3*s3)
if __name__ == '__main__':
    for f1 in (130, 145, 160):
        for d1 in (100, 110, 120):
            for e in (15, 30, 45):
                if d1 >= f1: continue
                s = soluzione(f1, d1, e)
                print({k: round(v, 1) for k, v in s.items()})
