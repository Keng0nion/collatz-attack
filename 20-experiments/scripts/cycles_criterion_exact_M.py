#!/Users/luna/Documents/math IA/collatz-attack/20-experiments/.venv/bin/python
"""精确求 M+(X0) 与 M-(X0)：先 numpy 双精度粗筛，再对边界附近的 m 用 mpmath 高精度定案。

排除规则（单侧窗口版判据，推导见 cycles_criterion_sides.py）：
  正环被排除  <=>  1 - frac(m*delta) >  m*w
  负环被排除  <=>      frac(m*delta) >  m*w
  其中 w = 1/((3*X0 - 1)*ln2)，delta = log2 3。
M+(X0) = 使 m = 1..M+ 全部被正侧排除的最大 M+（即第一个未被排除的 m 减一），M-(X0) 同理。

双精度误差量级：m*delta 的绝对误差约 m*1.6e-16（delta 的双精度相对误差 1e-16），
对 m <= 1e9 约 1.6e-7。凡 |(1-frac) - m*w| < 1e-5 的 m 一律用 mpmath 60 位复核。
"""
import sys
import numpy as np
import mpmath as mp

DELTA_STR = "1.58496250072115618145373894394781650875981440769248106045575265452"

def exact_frac(m, dps=60):
    mp.mp.dps = dps
    d = mp.log(3) / mp.log(2)
    x = m * d
    return x - mp.floor(x)

def compute_M(X0, scan_max, thresh_margin=1e-5, chunk=4_000_000):
    d = float(DELTA_STR)
    ln2 = float(mp.log(2))
    w = 1.0 / ((3.0 * X0 - 1.0) * ln2)
    Mp = None; Mn = None
    mp_first = None; mn_first = None
    for start in range(1, scan_max + 1, chunk):
        end = min(start + chunk - 1, scan_max)
        m = np.arange(start, end + 1, dtype=np.float64)
        fr = m * d
        fr = fr - np.floor(fr)
        t = m * w
        up = 1.0 - fr          # 正侧左边
        dn = fr                # 负侧左边
        if Mp is None:
            ratio = up - t
            idx = np.nonzero(ratio <= thresh_margin)[0]
            for i in idx:
                mm = int(m[i])
                if mm < (mp_first or 10**18):
                    frx = exact_frac(mm, 70)
                    if not (1 - frx > mm * mp.mpf(w)):
                        mp_first = mm if mp_first is None else min(mp_first, mm)
                        break
        if Mn is None:
            ratio = dn - t
            idx = np.nonzero(ratio <= thresh_margin)[0]
            for i in idx:
                mm = int(m[i])
                if mm < (mn_first or 10**18):
                    frx = exact_frac(mm, 70)
                    if not (frx > mm * mp.mpf(w)):
                        mn_first = mm if mn_first is None else min(mn_first, mm)
                        break
        if mp_first is not None and mn_first is not None:
            break
    return (mp_first - 1 if mp_first else None), (mp_first), (mn_first - 1 if mn_first else None), (mn_first)

def main():
    xs = [int(a) for a in sys.argv[1:]] or [10**12]
    scan = 300_000_000
    print(f"精确 M+ 与 M-（扫描 m 到 {scan}，边界用 70 位精度定案）")
    print(f"{'X0':>18} {'M+ (正环)':>16} {'首个未排除 m':>14} {'M- (负环)':>16} {'首个未排除 m':>14}")
    for X0 in xs:
        Mp, mpf, Mn, mnf = compute_M(X0, scan)
        print(f"{X0:>18} {str(Mp):>16} {str(mpf):>14} {str(Mn):>16} {str(mnf):>14}")
        sys.stdout.flush()

if __name__ == "__main__":
    main()
