#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第四条独立路径（decimal 60 位点值）：在 r4b2 与 MPFR 的端点上判 Phi_90 的符号。"""
from decimal import Decimal, getcontext

getcontext().prec = 70
X0 = Decimal(695) * Decimal(2) ** 60
d = Decimal(3).ln() / Decimal(2).ln()                    # delta = ln3/ln2
C = (Decimal(162) * X0 / Decimal(97)).ln() / Decimal(2).ln()


def geom(M):
    s = Decimal(0)
    p = Decimal(1)
    for _ in range(M):
        s += p
        p *= d
    return s


def cM(M):
    return Decimal(92) / Decimal(M) * geom(M)


def phi(M, K):
    cm = cM(M)
    c1 = cM(M - 1)
    v = K / cm
    vp = K / c1
    b2 = Decimal(2) ** v - 1
    b2p = Decimal(2) ** vp - 1
    A = Decimal(97) * Decimal(92 - M) + 73 if M <= 90 else (Decimal(3) * Decimal(54) if M == 91 else Decimal(0))
    if M == 92:
        Ad = Decimal(0) - Decimal(3) / X0 * 1
        Ad = Decimal(0) - Decimal(3) / X0
    elif M == 91:
        Ad = Decimal(3) / X0 - (Decimal(97) * 2 + 73) / (Decimal(54) * X0)
    else:
        Ad = -Decimal(97) / (Decimal(54) * X0)
    return Ad + Decimal(3) / b2 - Decimal(3) / b2p + Decimal(3) * (M - 1) * b2 ** (-d) \
        - Decimal(3) * (M - 2) * b2p ** (-d)


print("delta =", d)
print("C     =", C)
print("c_90  =", cM(90))
pts = [
    ("r4b2 下端", "123124614107652692133.007231711933058876044901"),
    ("r4b2 上端", "123124614107652692133.007231919710646726095849"),
    ("MPFR 下端", "123124614107652692133.0072322914378057066853155987473655841313302516937255859375"),
    ("本证书下端", "123124614107652692133.09788522373259494290393"),
    ("本证书上端", "123124614107652692133.0107855572742165347643"),
]
for name, s in pts:
    K = Decimal(s)
    print(f"  {name}: Phi_90 = {phi(90, K):.6e}")
