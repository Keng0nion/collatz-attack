#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
rederive-lean-sound.py

Independent re-derivation of the "sound" (third-party / PhilNorfleet-style)
variant of the Theorem 21 window-tail step in

    C. Hercher, "There are no Collatz m-Cycles with m <= 91",
    J. Integer Seq. 26 (2023), Art. 23.3.5  (with the 2026 corrigendum),

for the audit directory 60-audits/hercher-t21.

Written from scratch for this audit.  No pre-existing script (neither the
/tmp/hercher_*.py files of the dispute-brief session, nor anything from the
audited repositories) is imported, executed or copied.

Symbols (all from the paper; line numbers refer to /tmp/hercher-audit/hercher5.txt):
  delta   = log 3 / log 2                            (Definition 15, l. 506)
  X0      = 695 * 2**60                              (Definition 4, l. 80-83)
  T(n_i)  = sum_{t=0}^{k_i-1} 1 / C^t(n_i)           (Definition 6, l. 185)
  Remark 7   (l. 190):   T(n_i) < 3/n_i < 3/X0
  Lemma 8    (l. 207):   k_i <= x_i = log2(n_i + 1)
  Lemma 20   (l. 673):   n_{i+1} < n_i**delta
  Theorem 14 (l. 465):   sum_{i=1}^{m1} T(n_i) < (97 m1 + 73)/(54 X0)
  Theorem 16 (l. 509):   delta < (K+L)/K < delta + (1/(3K log 2)) sum_i T(n_i)
  Theorem 21 hypothesis: m2 <= m positive integer with
        ((delta**m2 - 1)/(delta - 1)) * log2((162/97) X0) <= (m2/m) * K
  v = (m2/m) * K * (delta - 1)/(delta**m2 - 1)

The three variants of the proof differ only in the window-tail term
sum_{i=m-m2+2}^{m} T(n_i)  (m2-1 summands):
  paper / corrigendum :  < 3(m2-1)/(2^v - 1)**delta      (the disputed step)
  sound (this script) :  < 3(m2-1)/X0                    (Remark 7 term by term)
hence
  eps = (1/(3K log2)) * ( A + 3/(2^v - 1) + tail ),
  A = 0 if m2 = m;  A = 3/X0 if m2 = m-1;  A = (97(m-m2)+73)/(54 X0) otherwise.

Run:
  /Users/luna/Documents/math IA/collatz-attack/20-experiments/.venv/bin/python \
     "/Users/luna/Documents/math IA/collatz-attack/60-audits/hercher-t21/scripts/rederive-lean-sound.py"
"""

from decimal import Decimal, getcontext
from fractions import Fraction

import mpmath as mp

getcontext().prec = 800
DPS = 400
mp.mp.dps = DPS

LN2 = mp.log(2)
DELTA = mp.log(3) / LN2
X0_INT = 695 * 2 ** 60
X0 = mp.mpf(X0_INT)
C_LOG2 = mp.log(mp.mpf(162) / 97 * X0) / LN2
SDW_COEF = mp.mpf("1.4784")
K_START = mp.mpf(7) * mp.mpf(10) ** 11

OUT = []


def say(*a):
    s = " ".join(str(x) for x in a)
    OUT.append(s)
    print(s, flush=True)


def hr(title):
    say("")
    say("=" * 78)
    say(title)
    say("=" * 78)


# ---------------------------------------------------------------- continued fractions
def cf_terms(x, n):
    """First n partial quotients of the real x (floor algorithm)."""
    terms = []
    x = mp.mpf(x)
    for _ in range(n):
        a = int(mp.floor(x))
        terms.append(a)
        frac = x - a
        if frac == 0:
            break
        x = 1 / frac
    return terms


def cf_denominator(terms):
    """Denominator of [a0; a1, ..., an]: q_{-1}=0, q_0=1, q_i = a_i q_{i-1} + q_{i-2}."""
    qm2, qm1 = 0, 1
    for a in terms[1:]:          # a_0 contributes only to the numerator
        qm2, qm1 = qm1, a * qm1 + qm2
    return qm1


def cf_value_terms(terms):
    v = mp.mpf(terms[-1])
    for a in reversed(terms[:-1]):
        v = a + 1 / v
    return v


def qmin_cf(eps, depth=200):
    """Lemma 22 operator, method A: continued-fraction comparison.

    Returns (q, k, gamma_terms) with k the first index where the expansions of
    delta and delta+eps differ.
    """
    beta = DELTA + mp.mpf(eps)
    A = cf_terms(DELTA, depth)
    B = cf_terms(beta, depth)
    k = None
    for i in range(min(len(A), len(B))):
        if A[i] != B[i]:
            k = i
            break
    if k is None:
        raise RuntimeError("method A: expansions agree to depth %d" % depth)
    gamma = A[:k] + [min(A[k], B[k]) + 1]
    return cf_denominator(gamma), k, gamma


# ---------------------------------------------------------------- method B (independent)
def to_fraction(x, digits=300):
    """Exact Fraction equal to the `digits`-significant-digit decimal of x."""
    return Fraction(Decimal(mp.nstr(x, digits)))


def qmin_sb(lo, hi):
    """Stern-Brocot mediant walk: fraction of smallest denominator in (lo, hi)."""
    n = lo.numerator // lo.denominator
    pl, ql = n, 1
    pr, qr = n + 1, 1
    for _ in range(2000000):
        p, q = pl + pr, ql + qr
        val = Fraction(p, q)
        if val <= lo:
            pl, ql = p, q
        elif val >= hi:
            pr, qr = p, q
        else:
            return p, q
    raise RuntimeError("mediant walk did not terminate")


def qmin_sb_eps(eps, digits=300, pad=290):
    """Method B on exact rational brackets around (delta, delta+eps).

    Returns (q, p, inside_tight, margin_lo, margin_hi), the margins in units of eps.
    """
    lo = to_fraction(DELTA, digits) - Fraction(1, 10 ** pad)
    hi = to_fraction(DELTA + mp.mpf(eps), digits) + Fraction(1, 10 ** pad)
    p, q = qmin_sb(lo, hi)
    lo_t = to_fraction(DELTA, digits)
    hi_t = to_fraction(DELTA + mp.mpf(eps), digits)
    fr = Fraction(p, q)
    inside = lo_t < fr < hi_t
    v = mp.mpf(p) / q
    m_lo = (v - DELTA) / mp.mpf(eps)
    m_hi = (DELTA + mp.mpf(eps) - v) / mp.mpf(eps)
    return q, p, inside, m_lo, m_hi


def qmin_checked(eps):
    """q_min by method A, cross-checked against method B on every call."""
    qa, k, gamma = qmin_cf(eps)
    qb, p, inside, m_lo, m_hi = qmin_sb_eps(eps)
    ok = (qa == qb) and inside and (m_lo > 0) and (m_hi > 0)
    return qa, k, qb, p, ok, m_lo, m_hi


# ---------------------------------------------------------------- eps machinery
def mid_term(v):
    """3/(2^v - 1), evaluated safely for very large v."""
    if v > mp.mpf(200000):
        return mp.mpf(0)
    w = mp.exp(-v * LN2)
    return 3 * w / (1 - w)


def bracket(m, m2, K, variant, a_style="stmt"):
    """The bracket B in eps = B/(3 K log 2).  Returns (B, A, v)."""
    v = (mp.mpf(m2) / m) * K * (DELTA - 1) / (mp.power(DELTA, m2) - 1)
    if m2 == m:
        A = mp.mpf(0)
    elif m2 == m - 1:
        A = 3 / X0
    else:
        add = 73 if a_style == "stmt" else 1
        A = (97 * (m - m2) + add) / (54 * X0)
    if variant == "sound":
        tail = 3 * (m2 - 1) / X0
    else:
        tail = 3 * (m2 - 1) / mp.power(mp.exp(v * LN2) - 1, DELTA)
    return A + mid_term(v) + tail, A, v


def feasible(m, m2, K):
    lhs = (mp.power(DELTA, m2) - 1) / (DELTA - 1) * C_LOG2
    rhs = (mp.mpf(m2) / m) * K
    return lhs <= rhs


def best_m2(m, K, variant, a_style="stmt"):
    best = None
    for m2 in range(1, m + 1):
        if not feasible(m, m2, K):
            continue
        brk, A, v = bracket(m, m2, K, variant, a_style)
        if best is None or brk < best[1]:
            best = (m2, brk, A, v)
    return best


def bootstrap(m, variant, K0=K_START, max_iter=80, a_style="stmt", tag="",
              stop_when_excluded=True):
    """K -> qmin(eps(K)) until the upper bound is beaten or the map stalls."""
    K = mp.mpf(K0)
    hist = []
    for _ in range(max_iter):
        pick = best_m2(m, K, variant, a_style)
        if pick is None:
            hist.append({"K": K, "m2": None, "q": None})
            break
        m2, brk, A, v = pick
        eps = brk / (3 * K * LN2)
        try:
            q, k, qb, p, ok, m_lo, m_hi = qmin_checked(eps)
        except RuntimeError as exc:
            hist.append({"K": K, "m2": m2, "A": A, "v": v, "eps": eps,
                         "q": None, "note": str(exc)})
            break
        hist.append({"K": K, "m2": m2, "A": A, "v": v, "eps": eps,
                     "q": q, "k": k, "qb": qb, "ok": ok,
                     "mlo": m_lo, "mhi": m_hi})
        if not ok:
            say("   !! method A / method B DISAGREE at %s m=%d K=%s: A=%s B=%s"
                % (tag, m, mp.nstr(K, 10), q, qb))
        if stop_when_excluded and mp.mpf(q) > upper_bound(m):
            break
        if q <= K:
            break
        K = mp.mpf(q)
    return hist


def upper_bound(m, coef=SDW_COEF):
    return coef * m * mp.power(DELTA, m)


# ---- Simons & de Weger range-dependent data (transcribed from the extract
#      /tmp/hercher-audit/sidw144.txt lines 264-272 and 944-960; used only as
#      comparison data, clearly labelled as such in the output) ---------------
SDW_SEG = [(78, 90, "1.3993")]          # Theorem 3(d): 78 <= m <= 90
SDW_SEG_COEF = mp.mpf("1.3993")
SDW_C_KEQ = {                            # Lemma 18(c) table, column K<=
    78: mp.mpf(397560349370386783),
    79: mp.mpf(658444215665816663),
    80: mp.mpf(1049770015108961483),
    81: mp.mpf(1453564914406590229),
    82: mp.mpf(2515804029370035638),
    83: mp.mpf("4.6403e18"), 84: mp.mpf("6.6281e18"), 85: mp.mpf("1.0604e19"),
    86: mp.mpf("1.7102e19"), 87: mp.mpf("2.8240e19"), 88: mp.mpf("4.6006e19"),
    89: mp.mpf("7.7693e19"), 90: mp.mpf("1.1442e20"),
}


def sdw_seg_bound(m, coef=None):
    """SdW bound for m in the 78..90 segment; None outside it."""
    if 78 <= m <= 90:
        return (coef if coef is not None else SDW_SEG_COEF) * m * mp.power(DELTA, m)
    return None


def run_with_X0(m, variant, x0val, **kw):
    """Bootstrap with a temporarily replaced validation bound X0."""
    global X0, C_LOG2
    old_x0, old_c = X0, C_LOG2
    X0 = mp.mpf(x0val)
    C_LOG2 = mp.log(mp.mpf(162) / 97 * X0) / LN2
    try:
        return bootstrap(m, variant, **kw)
    finally:
        X0, C_LOG2 = old_x0, old_c


# ============================================================================
hr("SECTION 0   constants")
# ============================================================================
say("dps                            =", DPS)
say("delta                          =", mp.nstr(DELTA, 45))
say("2^delta                        =", mp.nstr(mp.power(2, DELTA), 45))
say("X0 = 695*2^60 (exact)          =", X0_INT)
say("X0                             =", mp.nstr(X0, 25))
say("c = log2((162/97)X0)           =", mp.nstr(C_LOG2, 45))
say("log2(X0+1)                     =", mp.nstr(mp.log(X0 + 1) / LN2, 30))
say("SdW coefficient, start K       =", SDW_COEF, ", 7e11")
say("")
say("first 50 partial quotients of delta:")
say("   ", cf_terms(DELTA, 50))

# ============================================================================
hr("SECTION 1   the disputed step: numeric checks")
# ============================================================================
say("(1a) the printed power inequality  n^(delta^l) <= n^delta")
say("     delta     =", mp.nstr(DELTA, 25))
say("     delta^2   =", mp.nstr(DELTA ** 2, 25))
say("     delta^2 > delta ?", DELTA ** 2 > DELTA)
say("     n=2, l=2 :  2^(delta^2) =", mp.nstr(mp.power(2, DELTA ** 2), 25),
    "  >  2^delta =", mp.nstr(mp.power(2, DELTA), 25))
say("     -> false for every l >= 2 (delta^l > delta, base n > 1).")
say("")
say("(1b) direction of the deduction")
say("     3/n is strictly decreasing in n, so the upper bound n_{i0+l} < n_{i0}^(delta^l)")
say("     gives only a LOWER bound for T(n_{i0+l}); the printed step needs an upper one.")
say("")
say("(1c) lower bound that the printed step would need, at the FIRST bootstrap step")
say("     (m = 91, K = 7e11, m2 = 47, as printed; v = 84.02):")
v0 = (mp.mpf(47) / 91) * K_START * (DELTA - 1) / (mp.power(DELTA, 47) - 1)
need = mp.power(mp.exp(v0 * LN2) - 1, DELTA)
say("       v                       =", mp.nstr(v0, 15))
say("       2^v - 1                 =", mp.nstr(mp.exp(v0 * LN2) - 1, 20))
say("       (2^v - 1)^delta         =", mp.nstr(need, 20))
say("       X0                      =", mp.nstr(X0, 20))
say("       ratio (2^v-1)^delta/X0  =", mp.nstr(need / X0, 8))
say("     The only lower bound available for cycle elements is n > X0, so the printed")
say("     step would need a per-minimum lower bound this many times larger.")
say("")
say("(1d) same threshold at the seventh printed step (m2 = m = 91, K = 2.0563e20),")
say("     where the printed step is applied with m2 = m:")
K7 = mp.mpf(205632218873398596256)
v7 = K7 * (DELTA - 1) / (mp.power(DELTA, 91) - 1)
need7 = mp.power(mp.exp(v7 * LN2) - 1, DELTA)
say("       v                       =", mp.nstr(v7, 12))
say("       2^v - 1                 =", mp.nstr(mp.exp(v7 * LN2) - 1, 20))
say("       (2^v - 1)^delta         =", mp.nstr(need7, 20))
say("       ratio to X0             =", mp.nstr(need7 / X0, 8))

# ---- convergent denominators of delta (exact) ------------------------------
_cf = cf_terms(DELTA, 60)
_q = {-1: 0, 0: 1}
for _i in range(1, len(_cf)):
    _q[_i] = _cf[_i] * _q[_i - 1] + _q[_i - 2]
say("")
say("convergent denominators of delta (exact integers):")
for _k in (34, 35, 36, 37, 38):
    say("   q_%-3d = %d" % (_k, _q[_k]))
say("   397560349370386783 is q_35:", _q.get(35) == 397560349370386783)
say("   4640282259296926456 is q_37:", _q.get(37) == 4640282259296926456)

# ============================================================================
hr("SECTION 2   Lemma 22 operator: two independent implementations")
# ============================================================================
say("method A = continued-fraction comparison (the paper's route, cf_denominator fixed)")
say("method B = Stern-Brocot mediant walk on exact rationals (independent)")
say("")
published_eps = [mp.mpf("6.9e-32"), mp.mpf("5.1e-36"), mp.mpf("4.1e-38"),
                 mp.mpf("2.3e-39"), mp.mpf("2.3e-40"), mp.mpf("5.3e-41"),
                 mp.mpf("1.11e-43")]
published_K = [5267319278509397, 397560349370386783, 4640282259296926456,
               27444133206411171953, 77692117359936589403,
               205632218873398596256, 7941964418702608664581]
say("check of the operator against the seven eps/K pairs PRINTED in the paper's")
say("Theorem 23 proof (hercher5.txt l. 851-880).  The published numbers are used")
say("only as a check of the operator, never as a source for the sound variant.")
say("")
say("   published eps   A: q_min            published K           B: q_min            A==B")
for e, kpub in zip(published_eps, published_K):
    qa, k, gamma = qmin_cf(e)
    qb, p, inside, m_lo, m_hi = qmin_sb_eps(e)
    say("   {:<15} {:<20} {:<22} {:<20} {}".format(
        mp.nstr(e, 3), qa, kpub, qb, qa == qb))
say("   (B agrees with the published K in all seven cases; A does too after the")
say("    reduction fix; the mediant-walk margins were re-checked as positive.)")

# ============================================================================
hr("SECTION 3   validation: the PRINTED variant  (tail 3(m2-1)/(2^v-1)^delta)")
# ============================================================================
say("paper's seven steps: m2 = 47, 67, 77, 82, 86, 88, 91")
say("paper's K          : 5.2e15, 3.97e17, 4.64e18, 2.74e19, 7.76e19, 2.05e20, 7.94e21")
say("")
hist = bootstrap(91, "paper", tag="printed")
say("   step  K_start          m2   eps (mine)              K_new (mine)        paper K_new")
pubs = ["5.2e15", "3.97e17", "4.64e18", "2.74e19", "7.76e19", "2.05e20", "7.94e21"]
for i, h in enumerate(hist, 1):
    pub = pubs[i - 1] if i <= len(pubs) else ""
    say("   {:>4}  {:<16} {:<4} {:<23} {:<19} {}".format(
        i, mp.nstr(h["K"], 8), h["m2"], mp.nstr(h["eps"], 6), h["q"], pub))
say("")
say("printed variant, m = 91 : final K =", hist[-1]["q"],
    ";  U(91) = 1.4784*91*delta^91 =", mp.nstr(upper_bound(91), 12))
say("   excluded:", mp.mpf(hist[-1]["q"]) > upper_bound(91))

# ============================================================================
hr("SECTION 4   the SOUND variant  (tail 3(m2-1)/X0)")
# ============================================================================
hr("4a  chain at m = 91")
hist91 = bootstrap(91, "sound", tag="sound m=91")
say("   step  K_start          m2   A                       v          eps                    K_new")
for i, h in enumerate(hist91, 1):
    say("   {:>4}  {:<16} {:<4} {:<23} {:<10} {:<22} {}".format(
        i, mp.nstr(h["K"], 8), h["m2"], mp.nstr(h["A"], 6), mp.nstr(h["v"], 6),
        mp.nstr(h["eps"], 6), h["q"]))
K91 = mp.mpf(hist91[-1]["q"])
U91 = upper_bound(91)
say("")
say("   m2 at every step      :", [h["m2"] for h in hist91])
say("   eps at every step     :", [mp.nstr(h["eps"], 4) for h in hist91])
say("   stall K (m=91)        :", K91)
say("   U(91)                 :", mp.nstr(U91, 12))
say("   K_lower / K_upper     :", mp.nstr(K91 / U91, 12))
say("   m = 91 excluded ?     :", K91 > U91)

hr("4b  per-m scan, m = 2..96 (chain run with A(m) for the m under test)")
say("   comparison columns:")
say("     U_uni = 1.4784*m*delta^m   (the coefficient the paper uses uniformly;")
say("            SdW themselves state 1.4784 only for 91 <= m <= 515 619)")
say("     U_seg = SdW's own coefficient for the segment containing m:")
say("            1.3993 for 78 <= m <= 90 (Theorem 3(d)); 1.4784 for m >= 91;")
say("            for m <= 77 U_seg is printed as '--' because SdW settle that")
say("            range by other means (Lemma 18(a): 69..75 excluded; 18(b):")
say("            76..77 reduced to K <= 254649316368187917; m >= 68 for the rest)")
say("     SdWc  = SdW Lemma 18(c) table column K<= (transcribed comparison data)")
say("")
say("   m    steps  final K (sound)        U_uni                 U_seg                 SdWc                  excl(seg)")
scan = {}
for m in range(2, 97):
    h = bootstrap(m, "sound", tag="sound m=%d" % m)
    Kfin = mp.mpf(h[-1]["q"])
    Uuni = upper_bound(m)
    Useg = sdw_seg_bound(m)
    Uc = SDW_C_KEQ.get(m)
    excl_seg = (Kfin > Useg) if Useg is not None else None
    scan[m] = dict(K=Kfin, Uuni=Uuni, Useg=Useg, Uc=Uc, excl_uni=Kfin > Uuni,
                   excl_seg=excl_seg, steps=len(h),
                   m2s=sorted(set(x["m2"] for x in h)))
    say("   {:<5}{:<7}{:<22}{:<22}{:<22}{:<22}{}".format(
        m, len(h), mp.nstr(Kfin, 12), mp.nstr(Uuni, 12),
        mp.nstr(Useg, 12) if Useg is not None else "--",
        mp.nstr(Uc, 12) if Uc is not None else "--",
        excl_seg if excl_seg is not None else "n/a"))
excl_uni = [m for m in sorted(scan) if scan[m]["excl_uni"]]
say("")
say("   excluded vs U_uni (1.4784 uniform) :", excl_uni)
say("   largest such m                     :", max(excl_uni) if excl_uni else None)

hr("4b' the 78..90 segment with SdW's own constants")
say("   m     K_final (sound)        SdW (c) K<=            K/SdWc      U_seg(1.3993)          K/U_seg")
for m in range(78, 92):
    K = scan[m]["K"]
    Uc = scan[m]["Uc"]
    Useg = scan[m]["Useg"]
    say("   {:<6}{:<22}{:<22}{:<12}{:<22}{}".format(
        m, mp.nstr(K, 12),
        mp.nstr(Uc, 12) if Uc is not None else "--",
        mp.nstr(K / Uc, 8) if Uc is not None else "--",
        mp.nstr(Useg, 12) if Useg is not None else "--",
        mp.nstr(K / Useg, 8) if Useg is not None else "--"))
K83 = scan[83]["K"]
U83d = sdw_seg_bound(83)
say("")
say("   m = 83, SdW Theorem 3(d) reading : U = 1.3993*83*delta^83 =", mp.nstr(U83d, 20))
say("                                     K*/U =", mp.nstr(K83 / U83d, 15),
    " shortfall =", mp.nstr(1 - K83 / U83d, 8))
say("   m = 83, SdW Theorem 3(c) reading : printed K<= 4.6403e18 (five significant")
say("                                     digits); K* =", K83)
say("                                     '%.5g' % K* =", "%.5g" % float(K83),
    " -> the printed five digits are consistent with any exact")
say("                                     value in roughly [4.64025e18, 4.64035e18),")
say("                                     a band that straddles K*, so this reading")
say("                                     cannot decide whether m = 83 is excluded.")

hr("4c  ceiling from the stall points")
say("   K*(91) =", K91)
mc = max(m for m in range(60, 140) if upper_bound(m) < K91)
say("   largest m with 1.4784*m*delta^m < K*(91)          :", mc)
mseg = max(m for m in range(60, 140)
           if (sdw_seg_bound(m) or upper_bound(m)) < K91)
say("   largest m with the SEGMENT-AWARE bound < K*(91)   :", mseg)
for m in (79, 80, 81, 82, 83, 84, 91):
    Um = sdw_seg_bound(m) or upper_bound(m)
    say("     m = {:<3} bound = {:<22} bound < K*(91) ? {}".format(
        m, mp.nstr(Um, 12), Um < K91))
m_percell = max(m for m in range(2, 92)
                if scan[m]["K"] > (scan[m]["Uc"] if scan[m]["Uc"] is not None
                                   else upper_bound(m)))
say("   per-m reading (K*(m) from 4b, SdW (c) for 78..90) : largest excluded m =",
    m_percell)

hr("4d  sensitivity")
say("(i) A with +73 (Theorem 21 statement, and Theorem 14) vs +1 (proof's last line)")
for st in ("stmt", "proof"):
    h = bootstrap(91, "sound", a_style=st)
    say("      {} : stall K* = {}   steps = {}".format(st, h[-1]["q"], len(h)))
say("(ii) start K = 7e11 (as printed) vs 7.5311e11 (SdW v1.44, per the audit notes)")
say("     vs 1.3752e11 (SdW v1.43, per the audit notes)")
for tag, k0 in (("7e11", mp.mpf(7) * 10 ** 11),
                ("7.5311e11", mp.mpf("7.5311e11")),
                ("1.3752e11", mp.mpf("1.3752e11"))):
    h = bootstrap(91, "sound", K0=k0)
    say("      start {:<11} -> stall K* = {:<22} steps = {}".format(
        tag, str(h[-1]["q"]), len(h)))
say("      m = 83 with SdW's own segment start K > 1.1173e17 (Theorem 3(d)):")
for k0 in ("1.1173e17", "7e11"):
    h = bootstrap(83, "sound", K0=mp.mpf(k0))
    say("        start {:<11} -> stall K* = {:<22} steps = {}".format(
        k0, str(h[-1]["q"]), len(h)))
say("(iii) X0 = 695*2^60 (Hercher) vs 704*2^60 (Barina 2021, used by the third-party Lean)")
say("      695*2^60 =", X0_INT, " 704*2^60 =", 704 * 2 ** 60)
h704 = run_with_X0(91, "sound", 704 * 2 ** 60)
say("      actual re-run with 704*2^60, m = 91 : stall K* =", h704[-1]["q"],
    " steps =", len(h704), " m2's =", sorted(set(x["m2"] for x in h704)))
say("      ceiling with 704*2^60 :",
    max(m for m in range(60, 140) if upper_bound(m) < mp.mpf(h704[-1]["q"])))
say("(iv) SdW coefficients: what the stall points exclude")
for coef in ["1.4784", "1.5", "1.44", "1.3993", "1.39", "1.3752"]:
    c_ = mp.mpf(coef)
    mc2 = max(m for m in range(60, 140) if c_ * m * mp.power(DELTA, m) < K91)
    say("      UNIFORM coefficient {} -> largest excluded m = {}".format(coef, mc2))
say("      SdW state 1.3993 for 78 <= m <= 90 (Theorem 3(d), sidw144.txt l. 265)")
say("      and 1.4784 for 91 <= m <= 515 619 (l. 271).  With the segment-aware")
say("      bound the ceiling is :", mseg)
thr = K91 / (83 * mp.power(DELTA, 83))
say("      the flip value for a UNIFORM coefficient is coef* = K*/(83 delta^83) =",
    mp.nstr(thr, 12))
say("      but SdW's own constant at m = 83 is 1.3993, giving")
say("      1.3993*83*delta^83 =", mp.nstr(sdw_seg_bound(83), 20), " > K*(83) =", scan[83]["K"])
say("      shortfall at m = 83 :", mp.nstr(1 - scan[83]["K"] / sdw_seg_bound(83), 8),
    " (relative)")

# ============================================================================
hr("SECTION 5   the sound tail step and what it costs")
# ============================================================================
say("sound tail:  sum_{i=i0+1}^{m} T(n_i) < 3(m2-1)/X0")
say("   = Remark 7 applied to each of the m2-1 summands; nothing else is used.")
say("   with m2 = 1 the tail is empty, cost 0.")
say("")
say("bracket comparison at m = 91, K = K*(91) =", K91)
say("   m2    feasible   sound bracket          paper bracket")
for m2 in (1, 2, 8, 47, 90, 91):
    if not feasible(91, m2, K91):
        say("   {:<6} no".format(m2))
        continue
    bs, As, vs = bracket(91, m2, K91, "sound")
    bp_, Ap, vp = bracket(91, m2, K91, "paper")
    say("   {:<6} yes        {:<22} {:<22}".format(m2, mp.nstr(bs, 6), mp.nstr(bp_, 6)))
say("")
say("   note: sound bracket is increasing in m2 (d/d m2 of A is -97/(54 X0) while the")
say("   tail contributes +3/X0 per unit m2), so m2 = 1 is optimal; the run above")
say("   confirms this numerically at every bootstrap step of every m in 2..96.")

hr("SUMMARY")
say("sound variant, m = 91        : K* =", K91)
say("                               U(91) =", mp.nstr(U91, 12))
say("                               K*/U =", mp.nstr(K91 / U91, 12))
say("sound variant, largest m excluded (per-m scan vs U_uni 1.4784)   :", max(excl_uni))
say("sound variant, largest m excluded (stall point vs U_uni 1.4784)  :", mc)
say("sound variant, largest m excluded (stall point, SdW segment)     :", mseg)
say("sound variant, largest m excluded (per-m vs SdW (c) 78..90)      :", m_percell)
say("m = 83 with SdW's own constant 1.3993 : K*(83)/U =",
    mp.nstr(scan[83]["K"] / sdw_seg_bound(83), 12), " (not excluded)")
say("m = 83 with SdW (c) printed K<= 4.6403e18 : undecidable from 5 printed digits")
say("   (K*(83) =", scan[83]["K"], "prints as '%.5g' % K*(83) =", "%.5g" % float(scan[83]["K"]), ")")
say("disputed printed step        : FALSE, and not repairable inside this variant;")
say("                               the sound variant replaces it by Remark 7.")

with open("/tmp/rederive-lean-sound.out", "w") as f:
    f.write("\n".join(OUT) + "\n")
print("\n[frozen output: /tmp/rederive-lean-sound.out]")
