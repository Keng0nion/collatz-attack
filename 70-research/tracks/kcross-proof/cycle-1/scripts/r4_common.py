#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""kcross-proof 第 1 轮第 4 路（反例搜索与边界压力测试）公共层。

提供：
  consts()          delta、ln2 的严格区间
  feasible_set(K)   逐一判定的可行集与未定集（精确三值）
  eps_opt(K)        约定 M 的 eps_opt 严格区间、唯一 argmin（分离判据）、各格区间
  psi_two_sided(K)  Psi_92(K) 的严格夹逼 [q_lo, q_hi]
  psi_exact(K)      仅在 q_lo == q_hi 时给整数，否则报未定
  chain(K0)         自举链 K -> Psi(K) -> ...（每一步记录夹逼）
  root_interval()   方程 eps(92,K) = gamma - delta 的严格二分区间（复算 c2r5_cert 第 5 节）
  gamma/常量        gamma = 325919355854421968365/205632218873398596256（Lemma 22 构造）

一切判定只用 kc_rig 的 Fraction 精确算术；不含浮点判决。
"""
import sys
from fractions import Fraction as F

SCRIPTS = "/Users/luna/Documents/math IA/collatz-attack/70-research/tracks/kcross-proof/cycle-1/scripts"
if SCRIPTS not in sys.path:
    sys.path.insert(0, SCRIPTS)
import kc_rig as R

M = 92
KSTAR = 205632218873398596256
GAMMA = F(325919355854421968365, 205632218873398596256)
X0_695 = 695 * 2 ** 60
X0_704 = 704 * 2 ** 60
U92_W = F(14784, 10000)          # 1.4784 = 14784/10000（SdW 常数，项目口径）


def consts(N=400):
    DLO, DHI = R.delta_bounds(N)
    L2 = R.ln2_bounds(N)
    return DLO, DHI, L2


def gauge_C(X0, N=400):
    """两种口径各自的 C 区间；X0 = 695*2^60 时与原件 C_bounds 互为独立路线。"""
    if X0 == X0_695:
        return R.C_bounds(N)
    return R.C_from_x0(X0, N)


def feasible_set(K, CIV, DLO, DHI, m=M):
    """返回 (feas, und)：精确判定的可行 m2 列表与未定列表。"""
    feas, und = [], []
    for t in range(1, m + 1):
        d = R.feasible_decision(t, m, K, DLO, DHI, CIV)
        if d is True:
            feas.append(t)
        elif d is None:
            und.append(t)
    return feas, und


def eps_opt(K, CIV, DLO, DHI, L2, X0=None, m=M):
    """约定 M 的 eps_opt 严格区间与唯一 argmin。

    返回 dict：
      feas/und      可行集、未定集
      vals          {m2: (lo, hi)}
      lo, hi        eps_opt ∈ [min lo, min hi]（两端都是合法界，见报告引理）
      argmin        若存在 m2 使 eps_hi(m2) < eps_lo(u) 对一切 u != m2 成立，则为其编号，否则 None
      e92           eps(m, m, K) 的区间（m2 = m 格；与可行性无关的形式值）
    """
    feas, und = feasible_set(K, CIV, DLO, DHI, m)
    e92 = R.eps_bounds(m, m, K, DLO, DHI, L2, X0=X0)
    if not feas:
        return {"feas": feas, "und": und, "vals": {}, "lo": None, "hi": None,
                "argmin": None, "e92": e92}
    vals = {}
    for t in feas:
        vals[t] = R.eps_bounds(t, m, K, DLO, DHI, L2, X0=X0)
    lo = min(v[0] for v in vals.values())
    hi = min(v[1] for v in vals.values())
    arg = None
    for t in feas:
        if all(vals[t][1] < vals[u][0] for u in feas if u != t):
            arg = t
            break
    return {"feas": feas, "und": und, "vals": vals, "lo": lo, "hi": hi,
            "argmin": arg, "e92": e92}


def psi_two_sided(K, CIV, DLO, DHI, L2, X0=None, m=M):
    """Psi_m(K) 的严格夹逼：返回 (q_lo, q_hi, info)；q_lo <= Psi <= q_hi。

    inner = (delta_hi, delta_lo + eps_lo) ⊆ (delta, delta+eps_opt)
    outer = (delta_lo, delta_hi + eps_hi) ⊇ (delta, delta+eps_opt)
    最小分母关于包含单调，故 minq(inner) >= Psi >= minq(outer)。"""
    info = eps_opt(K, CIV, DLO, DHI, L2, X0=X0, m=m)
    if info["lo"] is None:
        return None, None, info
    outer = (R.rd(DLO), R.ru(DHI + info["hi"]))
    inner = (R.ru(DHI), R.rd(DLO + info["lo"]))
    if not (outer[0] < outer[1]):
        return None, None, info
    q_lo = R.simplest_fraction(*outer, cap=2000).denominator
    if not (inner[0] < inner[1]):
        return q_lo, None, info
    q_hi = R.simplest_fraction(*inner, cap=2000).denominator
    return q_lo, q_hi, info


def psi_exact(K, CIV, DLO, DHI, L2, X0=None, m=M):
    """Psi 的精确值或 None（未定）。"""
    q_lo, q_hi, info = psi_two_sided(K, CIV, DLO, DHI, L2, X0=X0, m=m)
    if q_lo is not None and q_lo == q_hi:
        return q_lo, info
    return None, info


def chain(K0, CIV, DLO, DHI, L2, X0=None, m=M, max_steps=64):
    """自举链：K_{n+1} = Psi_m(K_n)。返回 (steps, status)。

    steps 为 [(K_in, q_lo, q_hi, argmin, nfeas)]；status ∈
      'fixed'（到达不动点且精确）、'fixed_interval'（不动点但夹逼未闭合）、
      'undecided'（某步 Psi 未夹住）、'cycle'（回到访问过的值）、'cap'（步数上限）。
    """
    seen = set()
    steps = []
    K = F(K0)
    for _ in range(max_steps):
        q_lo, q_hi, info = psi_two_sided(K, CIV, DLO, DHI, L2, X0=X0, m=m)
        steps.append((K, q_lo, q_hi, info.get("argmin"), len(info.get("feas", []))))
        if q_lo is None:
            return steps, "undecided"
        if q_lo == q_hi:
            if F(q_lo) == K:
                return steps, "fixed"
            if F(q_lo) in seen:
                return steps, "cycle"
            seen.add(F(q_lo))
            K = F(q_lo)
        else:
            if F(q_hi) == F(q_lo):
                pass
            return steps, "fixed_interval"
    return steps, "cap"


def root_sign(K, DLO, DHI, L2, X0=None, m=M):
    """eps(m,m,K) - (gamma - delta) 的三值符号。"""
    GD_LO, GD_HI = GAMMA - DHI, GAMMA - DLO
    e = R.eps_bounds(m, m, K, DLO, DHI, L2, X0=X0)
    if e[0] > GD_HI:
        return "above"
    if e[1] < GD_LO:
        return "below"
    return None


def root_interval(DLO, DHI, L2, X0=None, m=M, steps=150,
                  K1=F(312) * 10 ** 18, K2=F(315) * 10 ** 18):
    """方程 eps(m,K) = gamma - delta 的严格二分区间（复算 c2r5_cert.py 第 5 节）。"""
    for _ in range(steps):
        Kmid = (K1 + K2) / 2
        s = root_sign(Kmid, DLO, DHI, L2, X0=X0, m=m)
        if s == "above":
            K1 = Kmid
        elif s == "below":
            K2 = Kmid
        else:
            break
    return K1, K2


def dec(x, nd):
    """Decimal 截断打印（与 c2r5_cert.py 的 dec 相同口径）。"""
    x = F(x)
    sign = "-" if x < 0 else ""
    x = abs(x)
    ip = x.numerator // x.denominator
    rem = x.numerator - ip * x.denominator
    out = [sign + str(ip), "."]
    for _ in range(nd):
        rem *= 10
        out.append(str(rem // x.denominator))
        rem -= (rem // x.denominator) * x.denominator
    return "".join(out)


def fnum(x, digits=8):
    """区间宽度的浮点摘要（仅用于打印量级）。"""
    return "%.3e" % float(x)
