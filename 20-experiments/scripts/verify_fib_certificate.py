"""Extend and re-verify the odd-step certificate found by z3, over a much larger
range than the domain it was solved on.

Run with the project venv:
  "/Users/luna/Documents/math IA/collatz-attack/20-experiments/.venv/bin/python" \
      verify_fib_certificate.py --limit 16777216 --domain-N 262144

Background.  The SMT search (smt_certificate_search.py, variant F) found, on the
odd x of [3, N], integer weights w_0..w_L with

    V(T(x)) <= V(x) - 1,   V(z) = sum_i w_i * bit_i(z),

and in three independent instances (N = 1024, 65536, 262144) the model satisfied
w_i = -Fibonacci(i-3) for every i >= 5.  This script takes that observed closed
form as the candidate weight sequence, extends it past the solved domain, and

  1. re-verifies the exact z3 certificate (weights up to index L of the solved
     domain) on its own domain, reproducing the in-run pointwise check,
  2. verifies the extended sequence on all odd x up to --limit,
  3. counts even-step violations, to show the certificate is genuinely odd-only,
  4. cross-checks the vectorised numpy path against a plain Python loop on a
     deterministic sample.

Numbers printed come from this run.  Nothing here is a proof for all x.
"""

import argparse
import json
import time

import numpy as np


def T(x):
    return x // 2 if x % 2 == 0 else (3 * x + 1) // 2


def fibonacci_weights(Lmax):
    """w_0..w_Lmax with w = [7,4,2,1,0] for i <= 4 and w_i = -Fib(i-3) for i >= 5."""
    fib = [0, 1]
    while len(fib) <= Lmax + 1:
        fib.append(fib[-1] + fib[-2])
    w = []
    for i in range(Lmax + 1):
        if i <= 4:
            w.append([7, 4, 2, 1, 0][i])
        else:
            w.append(-fib[i - 3])
    return w


class VFast:
    """V(z) = sum_i w_i bit_i(z) via two lookup tables (low 16 bits, high bits)."""

    def __init__(self, w):
        self.w = w
        self.Lmax = len(w) - 1
        lo = np.zeros(1 << 16, dtype=np.int64)
        for i in range(min(16, self.Lmax + 1)):
            lo += np.where(
                ((np.arange(1 << 16, dtype=np.int64) >> i) & 1) == 1, w[i], 0
            )
        self.lo = lo
        hi_n = 1 << max(0, self.Lmax + 1 - 16)
        hi = np.zeros(hi_n, dtype=np.int64)
        for i in range(16, self.Lmax + 1):
            hi += np.where(
                ((np.arange(hi_n, dtype=np.int64) >> (i - 16)) & 1) == 1, w[i], 0
            )
        self.hi = hi

    def __call__(self, z):
        z = np.asarray(z, dtype=np.int64)
        return self.lo[z & 0xFFFF] + self.hi[z >> 16]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=2 ** 24)
    ap.add_argument("--domain-N", type=int, default=2 ** 18)
    ap.add_argument("--json-out", type=str, default=None)
    args = ap.parse_args()
    limit, Ndom = args.limit, args.domain_N

    out = {"limit": limit, "domain_N": Ndom}
    print("extended odd-step certificate verification")
    print("limit = %d, z3 domain N = %d" % (limit, Ndom))

    # --- 1. exact z3 certificate on its own domain -------------------------
    Ldom = 18
    w_dom = fibonacci_weights(Ldom)
    V = VFast(w_dom)
    xs = np.arange(3, Ndom + 1, 2, dtype=np.int64)
    tx = np.where(xs % 2 == 1, (3 * xs + 1) // 2, xs // 2)
    bad = int(np.sum(V(tx) > V(xs) - 1))
    print("1. exact 2^18 certificate (w_0..w_18) on odd x in [3, %d]:"
          " checked=%d violations=%d" % (Ndom, xs.size, bad))
    out["domain_check"] = {"checked": int(xs.size), "violations": bad,
                           "weights": w_dom}

    # --- 2. extended sequence on all odd x up to limit --------------------
    Lmax = ((3 * limit + 1) // 2).bit_length()
    w = fibonacci_weights(Lmax)
    V = VFast(w)
    t0 = time.time()
    checked = 0
    first_bad = None
    viol = 0
    chunk = 1 << 20
    start = 3
    while start <= limit:
        stop = min(start + chunk, limit + 1)
        xs = np.arange(start, stop, dtype=np.int64)
        xs = xs[xs % 2 == 1]
        if xs.size:
            tx = (3 * xs + 1) // 2
            viols = V(tx) > V(xs) - 1
            nv = int(np.sum(viols))
            checked += int(xs.size)
            viol += nv
            if nv and first_bad is None:
                first_bad = int(xs[np.argmax(viols)])
        start = stop
    dt = time.time() - t0
    print("2. extended sequence (w_0..w_%d = Fibonacci tail) on odd x in [3, %d]:"
          " checked=%d violations=%d first_violation=%s  (%.1fs)"
          % (Lmax, limit, checked, viol, first_bad, dt))
    out["extended_check"] = {"Lmax": Lmax, "checked": checked, "violations": viol,
                             "first_violation": first_bad, "secs": round(dt, 2)}

    # --- 3. even-step behaviour (informational) ---------------------------
    xs = np.arange(2, limit + 1, 2, dtype=np.int64)
    tx = xs // 2
    strict_bad = int(np.sum(V(tx) > V(xs) - 1))
    noninc_bad = int(np.sum(V(tx) > V(xs)))
    print("3. even x in [2, %d]: violating strict decrease: %d / %d;"
          " violating non-increase: %d" % (limit, strict_bad, xs.size, noninc_bad))
    out["even_steps"] = {"count": int(xs.size), "strict_violations": strict_bad,
                         "nonincrease_violations": noninc_bad}

    # --- 4. numpy vs plain-Python cross-check ----------------------------
    rng = np.random.default_rng(20261018)
    sample = rng.integers(3, limit + 1, size=4000)
    sample = sample + (sample % 2 == 0)
    wl = list(w)

    def V_py(z):
        return sum(wl[i] for i in range(Lmax + 1) if (z >> i) & 1)

    mism = 0
    viol_py = 0
    for x in sample.tolist():
        if V_py(T(x)) > V_py(x) - 1:
            viol_py += 1
        if V_py(x) != int(V(np.array([x]))[0]):
            mism += 1
    print("4. cross-check on %d deterministic samples: V mismatches=%d,"
          " python violations=%d" % (sample.size, mism, viol_py))
    out["cross_check"] = {"samples": int(sample.size), "V_mismatches": mism,
                          "violations": viol_py}

    if args.json_out:
        with open(args.json_out, "w") as fh:
            json.dump(out, fh, indent=1)
        print("JSON written to %s" % args.json_out)
    print("---JSON-BEGIN---")
    print(json.dumps(out))
    print("---JSON-END---")


if __name__ == "__main__":
    main()
