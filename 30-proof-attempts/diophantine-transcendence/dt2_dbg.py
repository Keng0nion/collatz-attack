# dt2_dbg.py -- 调试上方逼近记录表（检查精度/完整性）
import mpmath as mp

mp.mp.dps = 400
d400 = mp.log(3) / mp.log(2)
mp.mp.dps = 150
d = mp.log(3) / mp.log(2)

def build_up(Qmax, prec):
    mp.mp.dps = prec
    dd = mp.log(3) / mp.log(2)
    rec = []; best = None
    lo_n, lo_d, hi_n, hi_d = 0, 1, 1, 0
    while True:
        mn, md = lo_n + hi_n, lo_d + hi_d
        if md > Qmax:
            break
        if mp.mpf(mn) / md > dd:
            hi_n, hi_d = mn, md
            g = (mp.mpf(mn) - md * dd) / md
            if best is None or g < best:
                best = g; rec.append((md, g))
        else:
            lo_n, lo_d = mn, md
    return rec

for prec in (150, 400):
    UP = build_up(10 ** 25, prec)
    print("prec=%d: 记录数=%d 最大q=%s" % (prec, len(UP), mp.nstr(UP[-1][0], 6)))
    bad = [(q, mp.nstr(g, 4)) for q, g in UP if g == 0]
    print("    gap+ == 0 的记录数 =", len(bad))
    print("   q 在 [1e18, 1e20] 的记录：")
    for q, g in UP:
        if 10 ** 18 <= q <= 10 ** 20:
            print("      q=%-22d gap+=%s" % (q, mp.nstr(g, 6)))
    # 三个测试 eff 的 q_min
    for eff in (mp.mpf('6.595e-41'), mp.mpf('2.653e-40'), mp.mpf('4.274e-38')):
        ans = None
        for q, g in UP:
            if g < eff:
                ans = q; break
        print("   eff=%s -> q_min=%s" % (mp.nstr(eff, 4), ans))

print()
print("手算核对：q=77692117359936589403 处的真实 gap+")
mp.mp.dps = 200
dd = mp.log(3) / mp.log(2)
for q in (77692117359936589403, 205632218873398596256, 397560349370386783):
    # 用高精度直接算 (⌈qδ⌉ - qδ)/q
    qd = mp.mpf(q) * dd
    p = mp.ceil(qd)
    g = (p - qd) / q
    print("   q=%-24d gap+ = %s" % (q, mp.nstr(g, 8)))
