import sys
sys.path.insert(0, "/Users/luna/Documents/math IA/collatz-attack/70-research/cycle-1/scripts")
from fractions import Fraction as F
from mpmath import mp, mpf
import r4x_core as R
import r4x_rig_helpers as H

mp.dps = 300
delta = mp.log(3) / mp.log(2)
print("delta =", mp.nstr(delta, 60))

A = R.cf_digits(delta, 60)
print("CF digits (raw):", A[:50])


def Qs(a, n):
    """standard convergent denominators Q_j = denom([a_0;...;a_j])"""
    Q = [1, a[1]]
    for j in range(2, n + 1):
        Q.append(a[j] * Q[j - 1] + Q[j - 2])
    return Q


def Ps(a, n):
    P = [a[0], a[0] * a[1] + 1]
    for j in range(2, n + 1):
        P.append(a[j] * P[j - 1] + P[j - 2])
    return P


Q = Qs(A, 50)
P = Ps(A, 50)
targets = {77692117359936589403: "77692117359936589403",
           127940101513462006853: "127940101513462006853",
           205632218873398596256: "K*",
           5267319278509397: "Psi(L)",
           397560349370386783: "397560349370386783"}
print()
for j in range(28, 51):
    mark = ""
    if Q[j] in targets:
        mark = "  <== " + targets[Q[j]]
    print("Q_%d = %d%s" % (j, Q[j], mark))
print()
print("P_j / Q_j for j=40..46:")
for j in range(40, 47):
    print("  j=%d  P=%d  Q=%d  (P/Q %s delta)" % (j, P[j], Q[j], ">" if mpf(P[j]) / Q[j] > delta else "<"))
print()
print("semiconvergents [A_0;...;A_{j-1}, m] : den = m*Q_{j-1} + Q_{j-2}")
for j in range(40, 47):
    for m in range(1, 4):
        num = m * P[j - 1] + P[j - 2]
        den = m * Q[j - 1] + Q[j - 2]
        v = mpf(num) / den
        print("  j=%d m=%d  %d/%d  (%s delta)  %s" % (
            j, m, num, den, ">" if v > delta else "<",
            "<== K*" if den == 205632218873398596256 else ("<== 7769...403" if den == 77692117359936589403 else "")))
