#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""停时分布统计、随机游走加漂移启发式模型对照、Krasikov 与 Lagarias 下界缺口分析。

输入（由 scripts/stoptime_dist 这个 C 程序产出，位于 results/）：
  stoptime_dist_summary.txt, stoptime_tot_hist.csv, stoptime_chistd_hist.csv,
  stoptime_chiacc_hist.csv, stoptime_tot_band2d.csv, stoptime_chiacc_band2d.csv,
  stoptime_records.txt

输出：
  results/stoptime_stats.txt   完整文本报告（含一个文本图）
  results/stoptime_stats.png   六面板图

启发式模型（下称「漂移模型」）：加速映射 T(n) = n/2（偶）、(3n+1)/2（奇），
假定奇偶序列 iid 均匀、且 3n+1 近似为 3n。则每加速步对数增量取
  -1（概率 1/2）或 log2 3 - 1（概率 1/2），
均值 mu = (log2 3 - 2)/2 = -0.2075187496，标准差 sigma = log2 3/2 = 0.7924812504。
"""
import os
import sys
import math
from math import log, log2, log10, sqrt, pi, erfc, gamma, exp

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.normpath(os.path.join(HERE, "..", "results"))
NOTE = os.path.normpath(os.path.join(HERE, "..", "..", "10-literature", "notes", "stopping-times.md"))

OUT_TXT = os.path.join(RES, "stoptime_stats.txt")
OUT_PNG = os.path.join(RES, "stoptime_stats.png")

LOG2_3 = log2(3.0)
MU = (LOG2_3 - 2.0) / 2.0            # -0.20751874963942188
SIGMA = LOG2_3 / 2.0                 # 0.7924812503605781
ABS_MU = -MU
R = SIGMA / ABS_MU                   # 3.8188...
CHI2SCALE = R * R                    # 14.5833...（扩散极限下的 Z^2 尺度）

# 大偏差速率（比特）：事件「前 k 个加速步内不跌破起点」等价于奇步占比 >= log_3 2
X0 = 1.0 / LOG2_3                    # log_3 2 = 0.6309297536
D_BITS = X0 * log2(2 * X0) + (1 - X0) * log2(2 * (1 - X0))
EULER_GAMMA = 0.5772156649015329

# 文献值：Krasikov 与 Lagarias 2003 表 2 的 gamma_k（k = 2..11）与 k = 11 的 lambda。
# 出处：项目笔记 10-literature/notes/stopping-times.md 第 60 行（转引自 arXiv:math/0205002 表 2）。
KL_GAMMA_K = [0.4365880, 0.6112620, 0.6891080, 0.7335790, 0.7608180,
              0.7825670, 0.8031960, 0.8168300, 0.8295450, 0.8417560]
KL_K = list(range(2, 12))
KL_LAMBDA_11 = 1.7922310
KL_PUBLISHED = 0.84

# 项目笔记里另一次会话的动态规划值（非本次运行）：F(50)、F(100)、F(135)、F(200)
NOTE_DP = {50: 3.54e-3, 100: 2.64e-4, 135: 5.33e-5, 200: 3.32e-6}

_lines = []


def say(s=""):
    print(s)
    _lines.append(s)


# ---------------------------------------------------------------- 读取
def load_hist(name):
    vals, cnts = [], []
    with open(os.path.join(RES, name)) as f:
        header = next(f)
        assert "count" in header, header
        for line in f:
            a, b = line.strip().split(",")
            vals.append(int(a))
            cnts.append(int(b))
    return np.array(vals), np.array(cnts, dtype=np.int64)


def load_band2d(name):
    bs, vs, cs = [], [], []
    with open(os.path.join(RES, name)) as f:
        next(f)
        for line in f:
            a, b, c = line.strip().split(",")
            bs.append(int(a)); vs.append(int(b)); cs.append(int(c))
    return np.array(bs), np.array(vs), np.array(cs, dtype=np.int64)


tot_v, tot_c = load_hist("stoptime_tot_hist.csv")
cs_v, cs_c = load_hist("stoptime_chistd_hist.csv")
ca_v, ca_c = load_hist("stoptime_chiacc_hist.csv")
b_tot, v_tot, c_tot = load_band2d("stoptime_tot_band2d.csv")
b_ca, v_ca, c_ca = load_band2d("stoptime_chiacc_band2d.csv")


def moments(vals, cnts):
    w = cnts.astype(np.float64)
    n = w.sum()
    m = float((vals * w).sum() / n)
    var = float(((vals - m) ** 2 * w).sum() / n)
    sd = sqrt(var)
    if var <= 0:
        return m, sd, float("nan"), float("nan"), int(n)
    sk = float(((vals - m) ** 3 * w).sum() / n) / var ** 1.5
    ku = float(((vals - m) ** 4 * w).sum() / n) / var ** 2
    return m, sd, sk, ku, int(n)


def tail_from_hist(vals, cnts, t0):
    """条件分布（取值 >= t0）的计数、均值、标准差（由直方图精确算出）。"""
    msk = vals >= t0
    w = cnts[msk].astype(np.float64)
    v = vals[msk].astype(np.float64)
    n = w.sum()
    mean = float((v * w).sum() / n)
    var = float(((v - mean) ** 2 * w).sum() / n)
    return int(n), mean, sqrt(var)


def band_stats(bs, vs, cs):
    out = {}
    for j in np.unique(bs):
        msk = bs == j
        out[int(j)] = (vs[msk], cs[msk])
    return out


B_TOT = band_stats(b_tot, v_tot, c_tot)
B_CA = band_stats(b_ca, v_ca, c_ca)

N_TOP = 1 << 24
# E[log2 n]，n 在 [2^j, 2^(j+1)) 上按均匀计数加权：j + 2 - 1/ln 2 = j + 0.5573
L_BAND = lambda j: j + 2.0 - 1.0 / log(2.0)


def model_tot(L):
    """漂移模型对总停时的预测：加速步先下降到 1，再换算为标准步。"""
    t_acc = L / ABS_MU
    var_acc = SIGMA ** 2 * L / ABS_MU ** 3
    mean = 1.5 * t_acc
    var = 2.25 * var_acc + 0.25 * t_acc      # 每步奇偶另加二项噪声
    return mean, sqrt(var)


def model_chi_acclimit(t):
    """扩散极限：chi_acc 近似 (sigma/mu)^2 Z^2，Z 标准正态。"""
    return erfc(sqrt(t / CHI2SCALE) / sqrt(2.0))


def model_ld(t):
    """大偏差速率预测：P[chi_acc >= t] 近似 2^(-D t)。"""
    return 2.0 ** (-D_BITS * t)


def norm_sf(z):
    return 0.5 * erfc(z / sqrt(2.0))


# ---------------------------------------------------------------- 文本图
def ascii_plot(xs_list, ys_list, labels, width=96, height=22,
               logx=True, logy=True, title="", xname="x", yname="y"):
    def tx(x):
        return log(x) if logx else x

    def ty(y):
        return log(max(y, 1e-300)) if logy else y

    X = [[tx(v) for v in ser] for ser in xs_list]
    Y = [[ty(v) for v in ser] for ser in ys_list]
    x0, x1 = min(min(a) for a in X), max(max(a) for a in X)
    y0, y1 = min(min(a) for a in Y), max(max(a) for a in Y)
    grid = [[" " for _ in range(width)] for _ in range(height)]
    chars = "#*.o+x%@&"
    for i, (xx, yy) in enumerate(zip(X, Y)):
        ch = chars[i % len(chars)]
        for k in range(len(xx)):
            cx = int((xx[k] - x0) / (x1 - x0) * (width - 1)) if x1 > x0 else 0
            cy = int((yy[k] - y0) / (y1 - y0) * (height - 1)) if y1 > y0 else 0
            grid[height - 1 - cy][cx] = ch
    say(title)
    for r in range(height):
        say("  |" + "".join(grid[r]))
    say("  +" + "-" * width)
    say("   " + xname + " 从左到右递增；" + yname + " 自下而上递增")
    say("   图例：" + "  ".join("%s = %s" % (chars[i % len(chars)], labels[i])
                               for i in range(len(labels))))


# ================================================================ 报告
say("=" * 78)
say("停时分布实验报告（由 scripts/stoptime_stats.py 生成）")
say("=" * 78)
say()
with open(os.path.join(RES, "stoptime_dist_summary.txt")) as f:
    say("【C 程序原始汇总】")
    for line in f:
        say("  " + line.rstrip())
say()

# 直方图含 n = 1（tot[1] = 0）。此前这里只用整条直方图算矩、却把样本数标成 n = 2 至 2^24，
# 属标签与实算不一致（复核发现的缺陷）。现在两种口径分别计算、分别标注。
m_all, sd_all, sk_all, ku_all, n_all = moments(tot_v, tot_c)          # n = 1 至 2^24
msk = tot_v >= 1
m_tot, sd_tot, sk_tot, ku_tot, n_tot = moments(tot_v[msk], tot_c[msk])  # n = 2 至 2^24
say("一、总停时（A006577 意义）整体经验统计")
say("  口径 A（n = 2 至 2^24，共 %d 个值；与 C 程序汇总同口径，本报告其余部分也用这个口径）：" % n_tot)
say("    均值 = %.6f，标准差 = %.6f，偏度 = %.6f，峰度 = %.6f（正态为 3）"
    % (m_tot, sd_tot, sk_tot, ku_tot))
say("    最小值 = %d，最大值 = %d" % (int(tot_v[msk].min()), int(tot_v.max())))
say("  口径 B（n = 1 至 2^24，共 %d 个值；把 tot[1] = 0 计入）：" % n_all)
say("    均值 = %.6f，标准差 = %.6f，偏度 = %.6f，峰度 = %.6f"
    % (m_all, sd_all, sk_all, ku_all))
say("    最小值 = %d，最大值 = %d" % (int(tot_v.min()), int(tot_v.max())))
say("  两口径的均值和标准差只差第 7 位小数（相对差 %.1e 与 %.1e）；偏度峰度差第 8 位。"
    % (abs(m_all - m_tot) / m_tot, abs(sd_all - sd_tot) / sd_tot))
say("  最大值的 n = 15733191（见 stoptime_records.txt 末行）")
say()

say("二、分带统计（band j 表示 n 在 [2^j, 2^(j+1)) 内；L = E[log2 n] = j + 0.5573）")
say("  j    L      count       经验均值    经验标准差  模型均值   模型标准差  均值比  标准差比  偏度")
rows = []
for j in range(0, 25):
    if j not in B_TOT:
        continue
    vals, cnts = B_TOT[j]
    m, sd, sk, ku, n = moments(vals, cnts)
    if j >= 24:                     # 顶端带只含 n = 2^24 一个点
        say("  %2d  %5.2f  %9d  %10.4f  %10.4f      （单点，不参与模型对照）" % (j, L_BAND(j), n, m, sd))
        continue
    L = L_BAND(j)
    mm, ms = model_tot(L)
    say("  %2d  %5.2f  %9d  %10.4f  %10.4f  %9.4f  %10.4f  %6.4f  %7.4f  %7.4f"
        % (j, L, n, m, sd, mm, ms, m / mm, sd / ms, sk))
    rows.append((j, L, n, m, sd, mm, ms, sk))

# 加权线性回归：经验均值对 L
arr = np.array([(r[1], r[3], r[2]) for r in rows if r[0] >= 12], dtype=float)
Ls, means, wts = arr[:, 0], arr[:, 1], arr[:, 2]
A = np.vstack([Ls, np.ones_like(Ls)]).T * np.sqrt(wts)[:, None]
bb, aa = np.linalg.lstsq(A, means * np.sqrt(wts), rcond=None)[0]
say()
say("  加权最小二乘拟合（j = 12 至 23）：经验均值 = %.5f + %.5f * L" % (aa, bb))
say("  漂移模型的理论斜率 1.5/|mu| = %.5f；实测斜率与之相差 %+.3f%%"
    % (1.5 / ABS_MU, 100 * (bb / (1.5 / ABS_MU) - 1)))
arr2 = np.array([(r[1], r[4] ** 2, r[2]) for r in rows if r[0] >= 12], dtype=float)
Ls2, var2, wts2 = arr2[:, 0], arr2[:, 1], arr2[:, 2]
A2 = np.vstack([Ls2, np.ones_like(Ls2)]).T * np.sqrt(wts2)[:, None]
bb2, aa2 = np.linalg.lstsq(A2, var2 * np.sqrt(wts2), rcond=None)[0]
say("  方差加权拟合：经验方差 = %.5f + %.5f * L；模型的近似斜率 2.25*sigma^2/|mu|^3 + 0.25/|mu| = %.5f"
    % (aa2, bb2, 2.25 * SIGMA ** 2 / ABS_MU ** 3 + 0.25 / ABS_MU))
say("    模型斜率比经验斜率低 %.4f%%（1 减 %.5f/%.5f，本次直接算出）"
    % (100 * (1 - (2.25 * SIGMA ** 2 / ABS_MU ** 3 + 0.25 / ABS_MU) / bb2),
       2.25 * SIGMA ** 2 / ABS_MU ** 3 + 0.25 / ABS_MU, bb2))
say()

say("三、正态性检验（顶部完整带 j = 23，n 在 [2^23, 2^24) 内）")
vals, cnts = B_TOT[23]
m23, s23, sk23, ku23, n23 = moments(vals, cnts)
L23 = L_BAND(23)
mm23, ms23 = model_tot(L23)
say("  经验均值 = %.4f，经验标准差 = %.4f，偏度 = %.4f，峰度 = %.4f"
    % (m23, s23, sk23, ku23))
say("  模型均值 = %.4f，模型标准差 = %.4f" % (mm23, ms23))
say("  逆高斯（扩散首达）预测偏度 3*sigma/sqrt(L*|mu|) = %.4f"
    % (3 * SIGMA / sqrt(L23 * ABS_MU)))
# 卡方拟合优度（对经验矩的拟合正态）
edges = np.arange(60, 341, 10)
obs = np.array([int(cnts[(vals >= edges[i]) & (vals < edges[i + 1])].sum())
                for i in range(len(edges) - 1)])
lo_c = int(cnts[vals < edges[0]].sum())
hi_c = int(cnts[vals >= edges[-1]].sum())
obs = np.concatenate([[lo_c], obs, [hi_c]])
exp_c = []
for i in range(len(obs)):
    if i == 0:
        a, b = -np.inf, edges[0]
    elif i == len(obs) - 1:
        a, b = edges[-1], np.inf
    else:
        a, b = edges[i - 1], edges[i]
    p = norm_sf((a - m23) / s23) - norm_sf((b - m23) / s23)
    exp_c.append(p * n23)
exp_c = np.array(exp_c)
keep = exp_c >= 5
chi2 = float((((obs[keep] - exp_c[keep]) ** 2) / exp_c[keep]).sum())
dof = int(keep.sum()) - 1 - 2
say("  卡方拟合优度（对同均值同方差的正态，10 步分箱、去掉期望计数小于 5 的箱）：")
say("    chi2 = %.2f，自由度 = %d" % (chi2, dof))
try:
    import mpmath as mp
    mp.mp.dps = 60
    sf_mp = mp.gammainc(mp.mpf(dof) / 2, mp.mpf(chi2) / 2, mp.inf) / mp.gamma(mp.mpf(dof) / 2)
    say("    p 值（卡方上尾）= %s（高精度字符串输出，越小说明偏离正态越显著）" % mp.nstr(sf_mp, 6))
    say("    log10(p 值) = %s" % mp.nstr(mp.log10(sf_mp), 8))
    say("    注意：该 p 值远小于 double 最小正正规数（约 2.2e-308），若先转成 float 再打印会下溢成 0，"
        "所以这里直接打印多精度字符串。")
except Exception as e:  # pragma: no cover
    say("    p 值计算失败：%s" % e)
say("  偏差形状（顶部带，按 20 步分箱；正态用同均值同方差）：")
say("    区间        实测计数      正态期望     实测/期望")
for lo in range(80, 281, 20):
    hi = lo + 20
    o = int(cnts[(vals >= lo) & (vals < hi)].sum())
    p = norm_sf((lo - m23) / s23) - norm_sf((hi - m23) / s23)
    e_ = p * n23
    say("    [%3d,%3d)  %10d  %11.1f  %10.4f" % (lo, hi, o, e_, (o / e_ if e_ > 0 else float("nan"))))
say("  说明：卡方在 8.4e6 样本下几乎必然拒绝任何连续分布；要看的是效应量（上表的比值）。")
say()

say("四、极值对照：范围最大值与两种极值模型")
say("  实际最大值 = 704，在 n = 15733191 处（见 records）")
pred_norm_max = mm23 + ms23 * sqrt(2 * log(1 << 23))
say("  顶部带正态模型（模型矩）预测的期望最大值 = m + s*sqrt(2 ln M) = %.1f（M = 2^23）" % pred_norm_max)
pred_norm_max_emp = m23 + s23 * sqrt(2 * log(1 << 23))
say("  顶部带正态模型（经验矩）预测的期望最大值 = %.1f" % pred_norm_max_emp)
# 取顶部带上尾 1% 作为 Gumbel 拟合样本
csum = np.cumsum(cnts[::-1])[::-1]
t99 = int(vals[np.searchsorted(-csum, -0.01 * n23)])
cnt_t, mean_t, sd_t = tail_from_hist(vals, cnts, t99)
beta_g = sd_t * sqrt(6) / pi
mu_g = mean_t - EULER_GAMMA * beta_g
pred_gumbel = mu_g + beta_g * (log(cnt_t) + EULER_GAMMA)
say("  顶部带右尾（tot >= %d，即上尾 1%%，计数 %d，条件均值 %.2f，条件标准差 %.2f）的 Gumbel 矩拟合：" % (t99, cnt_t, mean_t, sd_t))
say("    mu_G = %.3f，beta_G = %.3f；该尾内 %d 个样本的期望最大值为 %.2f" % (mu_g, beta_g, cnt_t, pred_gumbel))
say("  三个预测都低于实测 704：正态偏低最多，Gumbel 偏低 %.1f%%；说明右尾比正态重得多。" % (100 * (1 - pred_gumbel / 704)))
say("  注意：Gumbel 用的是同一批数据的内样本拟合，不是独立验证。")
say()
say("  超越计数对照（n 全部落在 2^24 内，共 16777216 个）：")
say("    t      实测计数    逐带经验矩正态预测   逐带模型矩正态预测")
for t in (250, 300, 350, 400, 450, 500, 600, 700):
    emp = int(tot_c[tot_v >= t].sum())
    p_emp = 0.0
    p_mod = 0.0
    for j, (vv, cc) in B_TOT.items():
        if j >= 24:
            continue
        mj, sj, skj, kuj, nj = moments(vv, cc)
        if sj <= 0:
            continue
        p_emp += nj * norm_sf((t - mj) / sj)
        L = L_BAND(j)
        mmj, msj = model_tot(L)
        p_mod += nj * norm_sf((t - mmj) / msj)
    say("   %4d  %9d  %18.1f  %18.1f" % (t, emp, p_emp, p_mod))
say()

say("五、Terras 停时（加速步，chi_acc）与两种启发性尾模型")
m_ca, sd_ca, sk_ca, ku_ca, n_ca = moments(ca_v, ca_c)
say("  经验：均值 = %.6f，标准差 = %.6f，偏度 = %.6f，最大值 = %d" % (m_ca, sd_ca, sk_ca, ca_v.max()))
say("  加速与标准步的均值比 chi_std/chi_acc = %.6f（启发式预测 1.5）" % (5.2369859360 / m_ca))
say("  扩散极限模型：chi_acc 约等于 %.4f 乘上 Z^2（Z 为标准正态）" % CHI2SCALE)
say("    即 P[chi_acc >= k] 约等于 erfc(sqrt(k/%.4f)/sqrt(2))" % CHI2SCALE)
say("  大偏差速率模型：P[chi_acc >= k] 约等于 2^(−%.6f * k)（每步乘 %.4f）"
    % (D_BITS, 2.0 ** (-D_BITS)))
say("  参考（项目笔记 stopping-times.md 第 82 行，另一次会话的 DP，非本次运行）："
    "F(50) = 3.54e-3，F(100) = 2.64e-4，F(135) = 5.33e-5，F(200) = 3.32e-6")
say()
say("    k    实测计数   实测生存率     扩散模型      大偏差模型   笔记 DP 值")
ca_rev = list(zip(ca_v.tolist(), ca_c.tolist()))
suffix = {}
acc = 0
for v, c in reversed(ca_rev):
    acc += c
    suffix[v] = acc
def surv_ca(k):
    """# {n : chi_acc(n) >= k} / (n 的个数)。"""
    ks = [v for v in suffix if v >= k]
    return (suffix[min(ks)] if ks else 0) / (n_ca - 1)


for k in (1, 2, 3, 5, 10, 20, 30, 40, 50, 60, 70, 80, 100, 120):
    cnt = int(round(surv_ca(k) * (n_ca - 1)))
    emp = surv_ca(k)
    nd = NOTE_DP.get(k, float("nan"))
    nd_s = ("%.3e" % nd) if not math.isnan(nd) else "  (无)"
    say("   %4d  %9d  %11.6f  %11.6f  %11.6f   %s" % (k, cnt, emp, model_chi_acclimit(k), model_ld(k), nd_s))

# 实测尾部的有效衰减率
kk = np.array([k for k in range(35, 71)], dtype=float)
ff = np.array([surv_ca(int(k)) for k in kk])
msk = ff > 0
slope_ln = np.polyfit(kk[msk], np.log(ff[msk]), 1)[0]
say()
say("  实测生存率在 k = 35 至 70 上的对数线性斜率 = %.6f（每步对数衰减，负数即衰减）" % slope_ln)
say("    大偏差模型对应的斜率 = %.6f nats/步" % (-log(2) * D_BITS))
say("    扩散模型对应的渐近斜率 = %.6f nats/步" % (-1.0 / (2 * CHI2SCALE)))
say()


def cover_needed(gamma, x):
    return x ** (gamma - 1.0)


say("六、Krasikov 与 Lagarias 下界与实际数据的缺口（本次范围内实际覆盖率恒为 1）")
say("  文献输入（来自项目笔记 stopping-times.md 第 60 行，转引自 arXiv:math/0205002 表 2）：")
say("    k = 11 的线性规划值 lambda = %.7f，对应 gamma = log2(lambda) = %.7f；发表表述为 x^0.84"
    % (KL_LAMBDA_11, log2(KL_LAMBDA_11)))
GAM_REC = log2(KL_LAMBDA_11)
say("  本次计算得到（我自己的运算）：log2(%.7f) = %.7f，1 减 gamma = %.7f"
    % (KL_LAMBDA_11, GAM_REC, 1 - GAM_REC))
say()
say("   x = 2^j    下界覆盖率 x^(gamma 减 1)      未覆盖比例      覆盖 50% 所需 gamma  覆盖 99% 所需 gamma")
for j in range(8, 25):
    x = 2.0 ** j
    cov = cover_needed(GAM_REC, x)
    g50 = 1.0 + log(0.5) / log(x)
    g99b = 1.0 + log(0.99) / log(x)
    say("   j = %2d  %18.6e  %14.10f  %20.6f  %20.6f" % (j, cov, 1 - cov, g50, g99b))
say("   参照：覆盖 1%% 所需 gamma，在 j = 24 处为 %.6f，低于当前记录，与当前覆盖率 %.4f 超过 1%% 一致。"
    % (1.0 + log(0.01) / log(2.0 ** 24), cover_needed(GAM_REC, 2.0 ** 24)))
say()
say("  把下界推到 1 所需的定量增益（本次范围内的观察）：")
say("    1) 指数必须从 %.7f 抬到 1；等价地 lambda 从 %.7f 抬到 2，即乘 %.6f。"
    % (GAM_REC, KL_LAMBDA_11, 2.0 / KL_LAMBDA_11))
say("    2) 若只要求在 x = 2^24 处覆盖到 1 减 1e-3，则需 1 减 gamma <= %.3e；"
    % (abs(log(0.999) / log(2.0 ** 24))))
say("       若只要求覆盖一半，需 1 减 gamma <= %.6f（即 gamma >= %.6f）。"
    % (1.0 / 24, 1 - 1.0 / 24))
say("    3) 该框架内每级 k 的上限由 k = 11 的 0.8418 起，逐级增量见下节外推。")
say()

say("七、逐级指数 gamma_k 的外推（文献十点，拟合为本次计算）")
say("  k    gamma_k      1 减 gamma_k")
for k, g in zip(KL_K, KL_GAMMA_K):
    say("  %2d  %.7f  %.7f" % (k, g, 1 - g))
say("  相邻增量：" + "、".join("%.6f" % (KL_GAMMA_K[i + 1] - KL_GAMMA_K[i]) for i in range(len(KL_GAMMA_K) - 1)))
y = np.log(np.array([1 - g for g in KL_GAMMA_K]))
karr = np.array(KL_K, dtype=float)
c1 = np.polyfit(karr, y, 1)
r2_1 = 1 - ((y - np.polyval(c1, karr)) ** 2).sum() / ((y - y.mean()) ** 2).sum()
c2 = np.polyfit(np.log(karr), y, 1)
r2_2 = 1 - ((y - np.polyval(c2, np.log(karr))) ** 2).sum() / ((y - y.mean()) ** 2).sum()
say("  拟合 A（几何）：ln(1 减 gamma_k) = %.5f %+.5f * k，R^2 = %.6f" % (c1[1], c1[0], r2_1))
say("     隐含 1 减 gamma_k 每级乘 %.5f" % exp(c1[0]))
say("  拟合 B（幂律）：ln(1 减 gamma_k) = %.5f %+.5f * ln(k)，R^2 = %.6f" % (c2[1], c2[0], r2_2))
say("     即 1 减 gamma_k 约等于 %.6f * k^(%.5f)" % (exp(c2[1]), c2[0]))
say()
say("  按拟合 B 外推（纯数学外推，无证明价值）：")
targets = [(1.0 / 24, "x = 2^24 处覆盖 50%"), (0.006334, "x = 2^24 处覆盖 90%"),
           (6.04e-4, "x = 2^24 处覆盖 99%"), (6.04e-5, "x = 2^24 处覆盖 99.9%")]
for tgt, lab in targets:
    kk_need = (tgt / exp(c2[1])) ** (1.0 / c2[0])
    say("    目标 1 减 gamma = %.3e（%s）：需 k 约 %.1f，对应 3^(k 减 1) 约 10^%.1f 个同余类"
        % (tgt, lab, kk_need, (kk_need - 1) * log10(3)))
q = exp(c1[0])
tail_sum = (1 - KL_GAMMA_K[-1]) * q / (1 - q)
say("  按拟合 A 外推：1 减 gamma_k 每级乘 %.5f，则 k 大于 11 的级数和 = %.6f * %.5f/(1 减 %.5f) = %.5f，"
    % (q, 1 - KL_GAMMA_K[-1], q, q, tail_sum))
say("     于是 gamma_inf 约 = %.5f + %.5f = %.5f。该级数和 %.5f 已经超过 1 减 gamma_11 = %.5f，"
    % (KL_GAMMA_K[-1], tail_sum, KL_GAMMA_K[-1] + tail_sum, tail_sum, 1 - KL_GAMMA_K[-1]))
say("     即按该几何比外推会给出 gamma_inf 远大于 1，而 gamma_k = log2(lambda_k) 且 lambda_k <= 2 使 gamma_k <= 1，")
say("     两者矛盾：说明「几何衰减」不是该序列的正确渐近形式（这是本次数值观察，不是定理）。")
say()

# 文本图：缺口形状
say("八、缺口形状（文本图）")
xs = [2.0 ** j for j in np.linspace(8, 80, 200)]
ascii_plot([xs, xs, xs, xs],
           [np.ones_like(xs), [cover_needed(KL_PUBLISHED, x) for x in xs],
            [cover_needed(GAM_REC, x) for x in xs], [cover_needed(0.99, x) for x in xs]],
           ["实际覆盖率（本次范围 1.0）", "x^0.84 下界", "x^0.8417560 下界", "x^0.99"],
           title="  覆盖率对 x 的依赖（双对数）", xname="x（2^8 至 2^80）", yname="覆盖率")
say()

# ---------------------------------------------------------------- 出图
try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib import font_manager as fm
    avail = {f.name for f in fm.fontManager.ttflist}
    for cand in ("PingFang SC", "Heiti TC", "Songti SC", "Arial Unicode MS", "Hiragino Sans GB"):
        if cand in avail:
            plt.rcParams["font.sans-serif"] = [cand]
            break
    plt.rcParams["axes.unicode_minus"] = False
    say("画图使用字体：%s" % plt.rcParams["font.sans-serif"][0])

    fig, axes = plt.subplots(2, 3, figsize=(19, 10))

    # 面板 1：顶部带分布与两条正态
    ax = axes[0][0]
    ax.bar(vals, cnts, width=0.9, color="0.75", label="经验（n 在 [2^23, 2^24)）")
    xs2 = np.linspace(40, 360, 400)
    pdf = lambda m, s: np.exp(-0.5 * ((xs2 - m) / s) ** 2) / (s * sqrt(2 * pi))
    ax.plot(xs2, pdf(m23, s23) * n23, "C3", label="正态（经验矩 %.1f, %.1f）" % (m23, s23))
    ax.plot(xs2, pdf(mm23, ms23) * n23, "C0", label="漂移模型（%.1f, %.1f）" % (mm23, ms23))
    ax.set_yscale("log")
    ax.set_title("总停时分布（顶部带）与正态对照")
    ax.set_xlabel("总停时")
    ax.set_ylabel("计数（对数）")
    ax.legend(fontsize=8)

    # 面板 2：顶部带内的超越计数（三条曲线同一口径：都以顶部带 8.4e6 个样本为基数）
    ax = axes[0][1]
    ts = np.arange(150, 721, 5)
    emp_curve = [max(int(cnts[vals >= t].sum()), 0.5) for t in ts]
    empr_curve = [max(n23 * norm_sf((t - m23) / s23), 0.5) for t in ts]
    mod_curve = [max(n23 * norm_sf((t - mm23) / ms23), 0.5) for t in ts]
    gum = [max(cnt_t * (1.0 - exp(-exp(-(t - mu_g) / beta_g))), 0.5) for t in ts]
    ax.semilogy(ts, emp_curve, "k", label="实测计数")
    ax.semilogy(ts, empr_curve, "C3", label="正态（经验矩 %d, %d）" % (round(m23), round(s23)))
    ax.semilogy(ts, mod_curve, "C0", label="正态（模型矩 %d, %d）" % (round(mm23), round(ms23)))
    ax.semilogy(ts, gum, "C4", ls="--", label="上尾 1%% Gumbel 拟合（t >= %d）" % t99)
    ax.axvline(704, color="C2", ls="--", label="实测最大值 704")
    ax.set_xlabel("总停时阈值 t")
    ax.set_ylabel("计数（对数）")
    ax.set_title("右尾超越计数：实测对正态模型")
    ax.legend(fontsize=8)

    # 面板 3：chi_acc 生存函数
    ax = axes[0][2]
    ks = np.arange(1, 121)
    emp_surv = [surv_ca(int(k)) if surv_ca(int(k)) > 0 else 1e-300 for k in ks]
    ax.semilogy(ks, emp_surv, "k", label="实测 chi_acc 生存率")
    ax.semilogy(ks, [model_chi_acclimit(k) for k in ks], "C0",
                label="扩散模型 erfc(sqrt(k/%.2f)/sqrt(2))" % CHI2SCALE)
    ax.semilogy(ks, [model_ld(k) for k in ks], "C3", label="大偏差 2^(-%.4f k)" % D_BITS)
    for k, v in NOTE_DP.items():
        if k <= 120:
            ax.plot([k], [v], "C2o", ms=4)
    ax.plot([], [], "C2o", label="项目笔记 DP 值（非本次运行）")
    ax.set_xlabel("k（加速步）")
    ax.set_ylabel("P[chi_acc >= k]（对数）")
    ax.set_title("Terras 停时尾部与两种启发模型")
    ax.legend(fontsize=8)

    # 面板 4：KL 缺口（对数横轴）
    ax = axes[1][0]
    xx = np.linspace(8, 64, 400)   # 指数 j，x = 2^j
    ax.loglog(2.0 ** xx, [1.0] * len(xx), "k", lw=1.6, label="实际覆盖率（n <= 2^24 内为 1）")
    ax.loglog(2.0 ** xx, [cover_needed(KL_PUBLISHED, 2.0 ** t) for t in xx], "C3",
              label="KL 发表表述 x^0.84")
    ax.loglog(2.0 ** xx, [cover_needed(GAM_REC, 2.0 ** t) for t in xx], "C0",
              label="KL 线性规划值 x^%.7f" % GAM_REC)
    for gg in (0.95, 0.99):
        ax.loglog(2.0 ** xx, [cover_needed(gg, 2.0 ** t) for t in xx], "C2", ls=":",
                  label="假设 gamma = %.2f" % gg)
    ax.axvline(2.0 ** 24, color="0.4", ls="--", lw=1)
    cov24 = cover_needed(GAM_REC, 2.0 ** 24)
    ax.plot([2.0 ** 24], [cov24], "ko", ms=5)
    ax.annotate("x = 2^24 处覆盖率 %.4f" % cov24, xy=(2.0 ** 24, cov24),
                xytext=(2.0 ** 26, cov24 * 5), fontsize=8,
                arrowprops=dict(arrowstyle="->", lw=0.8))
    ax.set_xlabel("x = 2^j")
    ax.set_ylabel("下界覆盖率 x^(gamma 减 1)")
    ax.set_title("下界与实际覆盖率的缺口形状")
    ax.legend(fontsize=8)

    # 面板 5：1 - gamma_k 与拟合
    ax = axes[1][1]
    yg = np.array([1 - g for g in KL_GAMMA_K])
    ax.semilogy(KL_K, yg, "ko", label="文献 gamma_k 的 1 - gamma_k")
    kkk = np.linspace(2, 40, 200)
    ax.semilogy(kkk, np.exp(np.polyval(c1, kkk)), "C3", ls="--",
                label="几何拟合（每级乘 %.3f）" % exp(c1[0]))
    ax.semilogy(kkk, np.exp(np.polyval(c2, np.log(kkk))), "C0",
                label="幂律拟合 k^(%.3f)" % c2[0])
    for tgt, lab in [(1.0 / 24, "2^24 处覆盖 50%"), (6.04e-4, "2^24 处覆盖 99%")]:
        ax.axhline(tgt, color="C2", ls=":", lw=1)
        ax.text(20.4, tgt, lab, fontsize=7, va="bottom")
    ax.set_xlabel("k")
    ax.set_ylabel("1 - gamma_k（对数）")
    ax.set_title("逐级指数的衰减与外推目标")
    ax.legend(fontsize=8)

    # 面板 6：所需 gamma 随 x（按覆盖目标），改画 1 - gamma 的对数
    ax = axes[1][2]
    xx2 = np.linspace(14, 64, 300)
    for frac, stl in [(0.5, "-"), (0.9, "--"), (0.99, ":"), (0.999, "-.")]:
        gs = [-log(frac) / log(2.0 ** t) for t in xx2]     # 1 - gamma 的需求
        ax.semilogy(2.0 ** xx2, gs, "C0", ls=stl, label="覆盖 %g%%" % (100 * frac))
    ax.axhline(1 - GAM_REC, color="C3", lw=1.4,
               label="当前记录 1 减 gamma = %.4f" % (1 - GAM_REC))
    for frac in (0.5, 0.9, 0.99):
        v = -log(frac) / log(2.0 ** 24)
        ax.plot([2.0 ** 24], [v], "C0", "o", ms=4)
    ax.plot([2.0 ** 24], [1 - GAM_REC], "C3", "o", ms=5)
    ax.set_xscale("log")
    ax.set_xlabel("x = 2^j")
    ax.set_ylabel("所需 1 - gamma（对数）")
    ax.set_title("把下界推到 1 所需的指数缺口")
    ax.legend(fontsize=8)

    fig.tight_layout()
    fig.savefig(OUT_PNG, dpi=110)
    say("图已保存：%s" % OUT_PNG)
except Exception as e:
    import traceback
    say("出图失败：%s" % e)
    say(traceback.format_exc())

with open(OUT_TXT, "w") as f:
    f.write("\n".join(_lines) + "\n")
print("文本报告已写入：%s" % OUT_TXT)
