#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
route-4 敌意否证探针：三类反例搜索（S0 单元测试与锚点自检 / S1 地板违反 / S2 更大不动点 /
S3 gamma 漂移）。判据与反例类定义见同目录 route4_adv_core.py 的文件头。

运行：
  /Users/luna/Documents/math IA/collatz-attack/20-experiments/.venv/bin/python \
      route4_adv_search.py
"""

import sys
import time

from mpmath import mp, mpf, floor

sys.path.insert(0, "/Users/luna/Documents/math IA/collatz-attack/70-research/cycle-2/scripts")
import route4_adv_core as C   # noqa: E402

L = mpf("7.5311e11")
K_STAR = C.K_STAR
U92 = C.U(92)


def _clo():
    return C.K_cross_lo()


def _chi():
    return C.K_cross_hi()


def sec(t):
    print("\n" + "=" * 78)
    print(t)
    print("=" * 78)


# ---------------------------------------------------------------- S0
def s0():
    sec("S0 单元测试（Psi_true 算法对拍）与锚点自检")
    C.setdps(120)
    # 1) 暴力最小分母算法在项目记录的退化例上的表现（materials.md:253）
    a, b = mpf(9) / 8, mpf(827) / 728
    r = C.brute_min_den(a, b, 200)
    print("[S0.1] 退化例 (9/8, 827/728) 的暴力最小分母 =", r[0], " 分数 =", r[1], "/", r[0],
          "  （materials.md:253 记公式给 8、真最小分母 15）")
    # 2) Psi_true 的记录序列算法 vs 暴力，在小 eps 上对拍
    d = C.delta()
    bad = 0
    for k in range(1, 9):
        eps = mpf(10) ** (-k)
        rec = C.upper_approx_records(10 ** 8)
        got = None
        for (p, q, g) in rec:
            if g < eps:
                got = q
                break
        br = C.brute_min_den(d, d + eps, 10 ** 6)
        ok = (br is not None and br[0] == got)
        bad += 0 if ok else 1
        print("[S0.2] eps=1e-%d  记录序列给 q=%s  暴力给 q=%s  一致=%s"
              % (k, got, br[0] if br else None, ok))
    print("[S0.2] 反例数 =", bad, " （上限 6 位分母；记录序列算法在小区间上与暴力一致）")
    # 3) 锚点自检（materials.md 的六处读数）
    print("\n[S0.3] 锚点自检（左：本实现；右：materials.md 记录的读数）")
    pts = [
        (mpf("7.5311e11"), 47, 5267319278509397, "materials.md:122 网格首格（L）"),
        (mpf("77692117359936589403"), 88, 77692117359936589403, "materials.md:133 m=92 链停滞点"),
        (mpf(10) ** 20, 89, K_STAR, "materials.md:134 K=1e20"),
        (mpf(K_STAR), 91, K_STAR, "materials.md:135 K=K*"),
        (mpf("3.3e20"), 92, 7941964418702608664581, "materials.md:261 m=92,3.3e20"),
        (U92, 92, 15678296618531818732906, "materials.md:261 m=92,U(92)"),
    ]
    for (K, m2x, psix, src) in pts:
        r = C.psi_true(K)
        ok = (r["psi"] == psix and r["m2"] == m2x)
        print("[S0.3] K=%-32s m2=%2s(记录 %2s) Psi=%-24s 一致=%s  <%s>"
              % (mp.nstr(K, 22), r["m2"], m2x, r["psi"], ok, src))
    # 4) K* 处 eps_opt 与 gamma 的锚点
    b = C.eps_opt_min_eps(mpf(K_STAR))
    print("\n[S0.4] eps_opt(K*) = %s   （materials.md:154 记 8.973221708617136016325725e-42）"
          % mp.nstr(b[1], 30))
    recs = C.upper_approx_records(10 ** 24)
    for (p, q, g) in recs:
        if q in (K_STAR, 7941964418702608664581, 15678296618531818732906):
            print("[S0.5] 记录序列成员 q=%s gap=%s  （materials.md:188 记 gamma-delta=6.244680669692735665906112e-43）"
                  % (q, mp.nstr(g, 30)))
    # 5) K_cross 两端的台阶值（route-4.md:203 至 :204）
    for K, tag in ((_clo(), "K_cross 左端"), (_chi(), "K_cross 右端")):
        r = C.psi_true(K, cap=10 ** 24)
        print("[S0.6] %-12s K=%s  Psi=%s  m2=%s  eps=%s"
              % (tag, mp.nstr(K, 42), r["psi"], r["m2"], mp.nstr(r["eps"], 20)))


# ---------------------------------------------------------------- S1
def s1():
    sec("S1 反例类 1：Psi(K) < K* 的点（地板违反）")
    C.setdps(100)
    recs = C.upper_approx_records(10 ** 24)
    gaps = [g for (_, _, g) in recs]

    def psi_rec(eps):
        for (p, q, g) in recs:
            if g < eps:
                return q
        return None

    # (a) 字面读法：[L, K*) 上（预期大量命中，作定义锚点，不算否证）
    C.setdps(100)
    lo_lit, ex = 0, []
    for j in range(60):
        K = L * mpf(10) ** (mpf(8.9) * j / 59)
        if K >= K_STAR:
            break
        b = C.eps_opt_min_eps(K)
        q = psi_rec(b[1])
        if q is not None and q < K_STAR:
            lo_lit += 1
            if len(ex) < 3:
                ex.append((K, q))
    print("[S1.a] 字面读法 [L, K*)：命中 %d 点（期望，不构成否证）。示例：" % lo_lit)
    for (K, q) in ex:
        print("       K=%s  Psi=%s < K*" % (mp.nstr(K, 20), q))

    # (b) 有意义读法：[K*, K_cross_hi] 上（这才是「K* 是最大不动点」的论域）
    xs = []
    N = 1200
    for j in range(N + 1):
        xs.append(K_STAR + (_chi() - K_STAR) * mpf(j) / N)
    # 加密：K* 邻域与 m2=92 可行门槛附近
    thr92 = mpf("3.025781390469742e20")
    for j in range(-50, 51):
        xs.append(K_STAR * (1 + mpf(j) / 10 ** 9))
        xs.append(thr92 * (1 + mpf(j) / 10 ** 12))
    viol = []
    conv_diff = []
    m2_track = []
    for K in xs:
        b = C.eps_opt_min_eps(K)
        if b is None:
            continue
        q = psi_rec(b[1])
        if q is not None and q < K_STAR:
            viol.append((K, q))
        b2 = C.eps_opt_max_feasible(K)
        if b2 is not None and b2[0] != b[0]:
            conv_diff.append((K, b[0], b2[0]))
        m2_track.append((K, b[0], b[1]))
    print("[S1.b] 网格点数 = %d（其中 K* 邻域与门槛邻域加密各 101 点）" % len(xs))
    print("[S1.b] 反例类 1（Psi(K) < K*）命中数 = %d" % len(viol))
    for (K, q) in viol[:10]:
        print("       见证候选：K=%s  Psi=%s" % (mp.nstr(K, 30), q))
    print("[S1.c] 两种约定（min_eps 与 max_feasible）argmin 不同的点数 = %d" % len(conv_diff))
    # (c) 门槛两侧的 m2 与 eps 跳变（结构读数）
    print("[S1.d] m2=92 可行门槛两侧的读数（门槛 c_92 = 3.025781390469742e20，route-4.md:262）：")
    for s in (-1, -0.5, -0.01, -1e-9, 0, 1e-9, 0.01, 0.5, 1, 10):
        K = thr92 * (1 + mpf(s) * mpf("1e-12")) if abs(s) < 1 else thr92 * (1 + mpf(s) / 100)
        b = C.eps_opt_min_eps(K)
        fs = C.feasible_set(K)
        q = psi_rec(b[1])
        print("       K=%s  可行 m2 上界=%2d  argmin=%2d  eps=%s  Psi=%s"
              % (mp.nstr(K, 24), fs[-1], b[0], mp.nstr(b[1], 12), q))
    # (d) 平台右端的剃刀：eps_opt(K_cross_lo) - gap(K*)
    b = C.eps_opt_min_eps(_clo())
    gstar = [g for (_, q, g) in recs if q == K_STAR][0]
    print("[S1.e] K_cross 左端：eps_opt = %s" % mp.nstr(b[1], 30))
    print("[S1.e] gap(K*)    = %s" % mp.nstr(gstar, 30))
    print("[S1.e] 余量 = eps_opt - gap(K*) = %s   （materials.md:191 记 +1.11953e-59）"
          % mp.nstr(b[1] - gstar, 8))
    b = C.eps_opt_min_eps(_chi())
    print("[S1.f] K_cross 右端：eps_opt = %s  余量 = %s"
          % (mp.nstr(b[1], 30), mp.nstr(b[1] - gstar, 8)))
    return recs


# ---------------------------------------------------------------- S2
def s2(recs):
    sec("S2 反例类 2：大于 K* 的不动点（K > K* 且 Psi(K) = K）")
    C.setdps(150)
    big = C.upper_approx_records(10 ** 40)
    cand = [(p, q, g) for (p, q, g) in big if q > K_STAR]
    print("[S2.a] 记录序列中 q > K* 的条数 = %d（分母上限 1e40）" % len(cand))
    print("[S2.a] 说明：不动点必落在记录序列的分母上（Psi 的取值只能是记录分母），故这是完备扫描。")
    # 判据（不需深挖记录序列）：记录序列分母升序、gap 严格降，故
    #     Psi(K) = q_i  <=>  gap_i < eps_opt(K) <= gap_{i-1}。
    # 于是对候选记录 q_i 只需两次比较：eps_opt(q_i) 与 gap_i、gap_{i-1}。
    hits = []
    checked = 0
    undet = []
    for idx, (p, q, g) in enumerate(big):
        if q <= K_STAR:
            continue
        g_prev = big[idx - 1][2] if idx > 0 else None
        C.setdps(60 if q < 10 ** 24 else 120)
        b = C.eps_opt_min_eps(mpf(q))
        e = b[1] if b else None
        if e is None:
            undet.append((q, "无可行 m2"))
            continue
        checked += 1
        if e <= g:
            verdict = "非不动点（Psi(q) > q）"
        elif g_prev is None or e <= g_prev:
            verdict = "★不动点（Psi(q) = q）"
            hits.append((q, e, g))
        else:
            verdict = "非不动点（Psi(q) < q）"
        if checked <= 10 or "★" in verdict:
            print("[S2.b] q=%-26s eps_opt(q)=%-12s gap_i=%-12s gap_(i-1)=%-12s 判定=%s"
                  % (q, mp.nstr(e, 8), mp.nstr(g, 8),
                     mp.nstr(g_prev, 8) if g_prev is not None else "无", verdict))
    print("[S2.b] 已判定记录分母数 = %d  真不动点命中 = %d  未能判定 = %d（分母上限 1e40）"
          % (checked, len(hits), len(undet)))
    # 直接对 K 网格做比对（含超大步长）
    print("[S2.c] K 网格：判据「Psi(K) > K ⟸ eps_opt(K) <= 分母 <= K 的记录里的最小 gap」"
          "（因 gap 沿记录序列严格降）")
    for e in (20, 21, 22, 24, 26, 30, 40):
        K = mpf(10) ** e
        C.setdps(220 if e <= 22 else 400)
        try:
            recs_k = C.upper_approx_records(10 ** e)
        except Exception as exc:                       # noqa: BLE001
            print("       K=1e%-3d 记录序列枚举失败：%s" % (e, exc))
            continue
        q_last, g_last = recs_k[-1][1], recs_k[-1][2]
        b = C.eps_opt_min_eps(K)
        if b is None:
            print("       K=1e%-3d 无可行 m2" % e)
            continue
        ok = b[1] <= g_last
        print("       K=1e%-3d 记录条数=%4d  分母≤K 的最大记录分母=%s  其 gap=%s  eps_opt=%s  "
              "⟹ Psi(K) > K 成立=%s"
              % (e, len(recs_k), q_last, mp.nstr(g_last, 8), mp.nstr(b[1], 8), ok))
    # 链式追踪：从见证起点出发的迭代
    print("[S2.d] 自举链追踪（cap = U(92)）:")
    for K0 in (mpf(K_STAR), mpf("3.3e20"), mpf("3.1e20"), mpf("2.5e20"), mpf(10) ** 20,
               mpf("1e21"), mpf("1e22")):
        C.setdps(300)
        seq, end, crossed = C.chain(K0, max_steps=12, cap=U92,
                                    psi_fn=lambda K: C.psi_true(K, records=C.upper_approx_records(10 ** 60)))
        print("       K0=%-14s 迭代 %2d 次，终值=%s  越过 U(92)=%s"
              % (mp.nstr(K0, 12), len(seq), mp.nstr(end, 6), crossed))
    return hits


# ---------------------------------------------------------------- S3
def s3():
    sec("S3 反例类 3：使 gamma 不等于 K* 的 K（K ∈ [K*, K_cross) 上 Psi(K) != K*）")
    C.setdps(150)
    recs = C.upper_approx_records(10 ** 26)
    gaps = [g for (_, _, g) in recs]

    def psi_rec(eps):
        for (p, q, g) in recs:
            if g < eps:
                return q
        return None

    xs = []
    N = 1500
    # 论域按第 1 轮口径取 [K*, K_cross)：用二分区间左端作上界（右端属于 K_cross 之外）
    for j in range(N + 1):
        xs.append(K_STAR + (_clo() - K_STAR) * mpf(j) / N)
    # 另把二分区间右端单列一行，用于标出阈值位置（不作为平台内的点计入）
    xs.append(_chi())
    # K* 的严格有理邻域：K* ± m/10^k（既取端点也取区间采样）
    for k in range(1, 7):
        for m in (1, 2, 3):
            xs.append(K_STAR + mpf(m) / 10 ** k)
            xs.append(K_STAR - mpf(m) / 10 ** k)
    for j in range(-20, 21):
        if j:
            xs.append(K_STAR + j)
    bad = []
    lem_bad = []
    hard = []
    for K in xs:
        b = C.eps_opt_min_eps(K)
        if b is None:
            continue
        q = psi_rec(b[1])
        if q != K_STAR:
            bad.append((K, q, b[0], b[1], mpf(K) >= _clo()))
        if len(hard) < 6 or (mpf(K_STAR) * mpf("0.9999") < K < K_STAR * mpf("1.0001")):
            r = C.psi_lem(K)
            if r["psi"] != K_STAR:
                lem_bad.append((K, r["psi"], r["k"], r["ck"]))
            hard.append((K, r["psi"], r["k"], r["ck"], r["gamma_den"]))
    print("[S3.a] 网格点数 = %d（含 K* ± m/10^k, k=1..6, m=1..3 与 K* ± 1..20；"
          "上界取二分区间左端）" % len(xs))
    inplat = [t for t in bad if not t[4]]
    outplat = [t for t in bad if t[4]]
    print("[S3.a] 反例类 3（Psi_true(K) != K*）命中数 = %d（其中平台论域 [K*, K_cross_lo] 内 %d 个；"
          "二分区间右端那一点 %d 个）" % (len(bad), len(inplat), len(outplat)))
    for (K, q, m2, e, beyond) in bad[:10]:
        print("       命中点：K=%s  Psi_true=%s  m2=%d  是否在 K_cross_lo 之外=%s"
              % (mp.nstr(K, 30), q, m2, beyond))
    print("[S3.b] Lemma 22 公式口径（Psi_lem）在 K* 邻域 1e-4 相对范围内的读数：")
    for (K, q, k, ck, gden) in hard[:24]:
        print("       K=%-34s Psi_lem=%-24s k=%2s ck=%-3s gamma_den=%s"
              % (mp.nstr(K, 26), q, k, ck, gden))
    print("[S3.c] K* 邻域内 Psi_lem != K* 的点数 = %d" % len(lem_bad))
    for (K, q, k, ck) in lem_bad[:10]:
        print("       K=%s  Psi_lem=%s  k=%s  ck=%s" % (mp.nstr(K, 26), q, k, ck))


if __name__ == "__main__":
    t0 = time.time()
    s0()
    recs = s1()
    s3()
    s2(recs)
    print("\n总耗时 %.1f 秒" % (time.time() - t0))
