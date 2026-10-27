import sys
sys.path.insert(0, "/Users/luna/Documents/math IA/collatz-attack/70-research/cycle-1/scripts")
from fractions import Fraction as F
from mpmath import mp, mpf
import r4x_core as R
import r4x_rig_helpers as H

KSTAR = 205632218873398596256
Q = [205632218873398596256,  # placeholder
     ]
Q42 = 127940101513462006853
Q43 = KSTAR
Q44 = 7736332199829210068325
Q41 = 77692117359936589403

R.set_dps(300)
DELTA = R.DELTA
print("delta  =", mp.nstr(DELTA, 40))
print("K*     =", KSTAR)
print("1/(Q42+Q43) =", mp.nstr(mpf(1) / (Q42 + Q43), 20))
print("1/Q44      =", mp.nstr(mpf(1) / Q44, 20))
print()

K = mpf(KSTAR)
print("K as mpf exact? ", K == KSTAR)
# feasible set
rows = []
for m2 in range(1, 93):
    lhs = R.premise_lhs(m2)          # geom(m2)*log2((162/97)X0)
    rhs = R.premise_rhs(m2, 92, K)
    feas = lhs <= rhs
    if feas:
        e = R.eps_of(m2, 92, K)
        rows.append((m2, float(e), float(lhs), float(rhs)))
print("feasible m2 count =", len(rows), " range =", rows[0][0], "..", rows[-1][0])
print("all feasible m2:", [r[0] for r in rows])
print()
best = min(rows, key=lambda r: r[1])
print("argmin m2 =", best[0], " eps =", best[1])
print("eps(91) =", [r[1] for r in rows if r[0] == 91])
print("eps(90) =", [r[1] for r in rows if r[0] == 90])
print("eps(89) =", [r[1] for r in rows if r[0] == 89])
print("eps(1)  =", [r[1] for r in rows if r[0] == 1])
print("eps(50) =", [r[1] for r in rows if r[0] == 50])
print()
# check monotone decreasing over feasible set
mono = all(rows[i][1] > rows[i + 1][1] for i in range(len(rows) - 1))
print("eps strictly decreasing over feasible set?", mono)
for i in range(len(rows) - 1):
    if not rows[i][1] > rows[i + 1][1]:
        print("  violation at", rows[i][0], rows[i][1], rows[i + 1][0], rows[i + 1][1])
print()
print("m2=92 feasible?", R.feasible(92, 92, K), " lhs-rhs =", float(R.premise_lhs(92) - R.premise_rhs(92, 92, K)))
print("m2=91 feasible?", R.feasible(91, 92, K), " lhs-rhs =", float(R.premise_lhs(91) - R.premise_rhs(91, 92, K)))
print()
v91 = R.v_of(91, 92, K)
print("v(91) =", mp.nstr(v91, 25))
print("geom(91) =", mp.nstr(R.geom(91), 25))
print("delta^91 =", mp.nstr(mp.power(DELTA, 91), 25))
print("2^v-1 =", mp.nstr(mp.power(2, v91) - 1, 20))
print("A(91) =", mp.nstr(R.A_of(91, 92), 25), " 3/X0 =", mp.nstr(mpf(3) / R.X0(), 25))
print("eps(91) =", mp.nstr(R.eps_of(91, 92, K), 25))
e = R.eps_of(91, 92, K)
print()
print("Q43*eps =", mp.nstr(Q43 * e, 20))
print("Q43*eps vs 1/(Q42+Q43):", mp.nstr(Q43 * e / (mpf(1) / (Q42 + Q43)), 12), " (need < 1)")
print("Q43*eps vs 1/Q44      :", mp.nstr(Q43 * e * Q44, 12), " (need > 1)")
gamma = F(325919355854421968365, KSTAR)
g = mpf(gamma.numerator) / gamma.denominator
print("gamma        =", mp.nstr(g, 30))
print("gamma - delta=", mp.nstr(g - DELTA, 20))
print("eps - (g-d)  =", mp.nstr(e - (g - DELTA), 20))
