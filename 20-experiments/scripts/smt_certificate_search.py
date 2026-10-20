"""SMT certificate search on the truncated Collatz state space [1, N].

Run with the project venv:
  "/Users/luna/Documents/math IA/collatz-attack/20-experiments/.venv/bin/python" \
      smt_certificate_search.py --N 1048576 --N-small 4096

Question.  Let T be the accelerated Collatz map  T(x) = x/2 for even x,
T(x) = (3x+1)/2 for odd x.  Search for a potential function V out of one of the
following classes such that

        V(T(x)) <= V(x) - 1        for every x in the truncation domain,

  A. V(z) = (A*z + B*popcount(z)) / D      (A, B, D integers, D >= 1; this is the
     rational class V(x) = a*x + b*popcount(x)),
  B. V(z) = sum_{i <= Lmax} w_i * bit_i(z)  (bit-additive; note a*x + b*popcount
     is the special case w_i = a*2^i + b, so B contains A),
  C. V arbitrary (one integer variable per state)  -- control instance,
  D. B-weights but the strict decrease is required only on odd x, non-increase on
     even x  -- relaxation probe,
  F. B-weights with the strict decrease required only on odd x  -- relaxation probe.

Every constraint is asserted with assert_and_track under the name "x=<v>", so an
UNSAT answer comes with an explicit, human-checkable unsat core of truncated
states.  Any SAT answer is re-verified pointwise in exact integer arithmetic over
the whole domain (and, informationally, beyond it), and stored as a certificate
in the JSON output.

All numbers printed come from this run.
"""

import argparse
import json
import time

from z3 import Int, Solver, sat, unsat


def T(x):
    return x // 2 if x % 2 == 0 else (3 * x + 1) // 2


def pc(x):
    return bin(x).count("1")


def bit_terms(x, Lmax, w):
    return sum(w[i] for i in range(Lmax + 1) if (x >> i) & 1)


def V_of_weights(w, Lmax, z):
    return sum(w[i] for i in range(Lmax + 1) if (z >> i) & 1)


# ---------------------------------------------------------------- variants


def build_linear(domain):
    """A, B, D with V = (A*x + B*popcount(x))/D, D >= 1."""
    A, B, D = Int("A"), Int("B"), Int("D")
    cons = [(D >= 1, "D>=1")]
    for x in domain:
        tx = T(x)
        cons.append((A * (tx - x) + B * (pc(tx) - pc(x)) <= -D, "x=%d" % x))
    verdict = {
        "form": "V = (A*x + B*popcount(x))/D with D>=1  [= a*x + b*popcount(x)]",
        "extract": lambda m: {"A": int(str(m[A])), "B": int(str(m[B])),
                              "D": int(str(m[D]))},
        "kind": "linear",
    }
    return cons, verdict


def build_weights(domain, lhs_rhs=None):
    """w_i with V = sum w_i bit_i(z).  lhs_rhs(x) overrides the constant -1
    (used by the relaxation probes)."""
    Nref = max(domain)
    Lmax = max(T(x) for x in range(1, Nref + 1)).bit_length() - 1
    w = [Int("w_%d" % i) for i in range(Lmax + 1)]
    cons = []
    for x in domain:
        rhs = -1 if lhs_rhs is None else lhs_rhs(x)
        cons.append((bit_terms(T(x), Lmax, w) - bit_terms(x, Lmax, w) <= rhs,
                     "x=%d" % x))
    verdict = {
        "form": "V = sum_i w_i * bit_i(x), i <= %d" % Lmax,
        "Lmax": Lmax,
        "extract": lambda m: [int(str(m[wi])) for wi in w],
        "kind": "weights",
    }
    return cons, verdict


def build_free_v(domain, Nref):
    Nmax = max(T(x) for x in range(1, Nref + 1))
    v = {y: Int("v_%d" % y) for y in range(1, Nmax + 1)}
    cons = [(v[T(x)] <= v[x] - 1, "x=%d" % x) for x in domain]
    verdict = {
        "form": "V arbitrary, one Int per state in [1, %d]" % Nmax,
        "Nmax": Nmax,
        "vmap": v,
        "extract": lambda m: None,
        "kind": "freev",
    }
    return cons, verdict


# ------------------------------------------------------------- verification


def verify_weights(w, Lmax, N, odd_only):
    """pointwise: returns (violations, checked)."""
    bad = []
    checked = 0
    for x in range(3, N + 1):
        if odd_only and x % 2 == 0:
            continue
        checked += 1
        if V_of_weights(w, Lmax, T(x)) > V_of_weights(w, Lmax, x) - 1:
            bad.append(x)
            if len(bad) >= 10:
                break
    return bad, checked


def verify_linear(Av, Bv, Dv, N, lo=1):
    bad = []
    checked = 0
    for x in range(lo, N + 1):
        checked += 1
        lhs = Av * (T(x) - x) + Bv * (pc(T(x)) - pc(x))
        if lhs > -Dv:
            bad.append(x)
            if len(bad) >= 10:
                break
    return bad, checked


def verify_free_v(vmap, model, N):
    bad = []
    checked = 0
    unresolved = 0
    for x in range(3, N + 1):
        mx, my = model[vmap[T(x)]], model[vmap[x]]
        if mx is None or my is None:
            unresolved += 1
            continue
        checked += 1
        if not (int(str(my)) - int(str(mx)) >= 1):
            bad.append(x)
            if len(bad) >= 10:
                break
    return bad, checked, unresolved


# ------------------------------------------------------------------- runner


def solve(cons, timeout_ms):
    s = Solver()
    s.set("timeout", timeout_ms)
    for cond, nm in cons:
        s.assert_and_track(cond, nm)
    t0 = time.time()
    r = s.check()
    return r, s, time.time() - t0


def report(name, cons, verdict, r, s, secs, results):
    rec = {"name": name, "form": verdict["form"],
           "n_constraints": len(cons), "result": str(r),
           "solve_secs": round(secs, 3)}
    print("[%s]  %s" % (name, verdict["form"]))
    print("    constraints=%d  solve=%.2fs  ->  %s" % (len(cons), secs, r))
    if r == unsat:
        core = sorted(str(c) for c in s.unsat_core())
        rec["core"] = core
        print("    unsat core (%d): %s%s"
              % (len(core), core[:12], " ..." if len(core) > 12 else ""))
    elif r == sat:
        rec["model"] = verdict["extract"](s.model())
        print("    model: %s" % (str(rec["model"])[:400],))
    results.append(rec)
    return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--N", type=int, default=2 ** 20)
    ap.add_argument("--N-small", type=int, default=2 ** 12,
                    help="size for the free-V control instance")
    ap.add_argument("--timeout-ms", type=int, default=900000)
    ap.add_argument("--json-out", type=str, default=None)
    ap.add_argument("--skip-heavy", action="store_true",
                    help="run only the light variants (probes and control)")
    args = ap.parse_args()

    N, Nsmall = args.N, args.N_small
    results, certificates = [], []

    print("z3 certificate search, truncation domain [1, N], N = %d" % N)
    print("map: T(x) = x/2 (x even), (3x+1)/2 (x odd)   [accelerated Collatz]")
    print("=" * 78)

    if not args.skip_heavy:
        # ---- A1: named form on the full truncation
        cons, v = build_linear(range(1, N + 1))
        r, s, dt = solve(cons, args.timeout_ms)
        rec = report("A1-linear-full", cons, v, r, s, dt, results)
        if r == sat:
            m = v["extract"](s.model())
            bad, checked = verify_linear(m["A"], m["B"], m["D"], N)
            print("    pointwise verify over [1,%d]: checked=%d violations=%d %s"
                  % (N, checked, len(bad), bad[:5]))
            rec["verify"] = {"checked": checked, "violations": len(bad)}
            certificates.append({"name": "A1-linear-full", "linear": m})

        # ---- A2: same form, trivial cycle excluded from constraint sources
        cons, v = build_linear(range(3, N + 1))
        r, s, dt = solve(cons, args.timeout_ms)
        rec = report("A2-linear-excl", cons, v, r, s, dt, results)
        if r == sat:
            m = v["extract"](s.model())
            bad, checked = verify_linear(m["A"], m["B"], m["D"], N, lo=3)
            print("    pointwise verify over [3,%d]: checked=%d violations=%d %s"
                  % (N, checked, len(bad), bad[:5]))
            rec["verify"] = {"checked": checked, "violations": len(bad)}
            certificates.append({"name": "A2-linear-excl", "linear": m})

        # ---- B1: bit-additive weights, full truncation
        cons, v = build_weights(range(1, N + 1))
        r, s, dt = solve(cons, args.timeout_ms)
        rec = report("B1-weights-full", cons, v, r, s, dt, results)
        if r == sat:
            w = v["extract"](s.model())
            bad, checked = verify_weights(w, v["Lmax"], N, odd_only=False)
            print("    pointwise verify: checked=%d violations=%d" % (checked, len(bad)))
            rec["verify"] = {"checked": checked, "violations": len(bad)}
            certificates.append({"name": "B1-weights-full", "weights": w,
                                 "odd_only": False})

        # ---- B2: bit-additive weights, trivial cycle excluded
        cons, v = build_weights(range(3, N + 1))
        r, s, dt = solve(cons, args.timeout_ms)
        rec = report("B2-weights-excl", cons, v, r, s, dt, results)
        if r == sat:
            w = v["extract"](s.model())
            bad, checked = verify_weights(w, v["Lmax"], N, odd_only=False)
            print("    pointwise verify: checked=%d violations=%d" % (checked, len(bad)))
            rec["verify"] = {"checked": checked, "violations": len(bad)}
            certificates.append({"name": "B2-weights-excl", "weights": w,
                                 "odd_only": False})

    # ---- D: weights, strict on odd x, non-increase on even x
    cons, v = build_weights(range(3, N + 1),
                            lhs_rhs=lambda x: -1 if x % 2 else 0)
    r, s, dt = solve(cons, args.timeout_ms)
    rec = report("D-odd-strict-even-noninc", cons, v, r, s, dt, results)
    if r == sat:
        w = v["extract"](s.model())
        bad, checked = verify_weights(w, v["Lmax"], N, odd_only=False)
        print("    pointwise verify (odd strict, even non-increase):"
              " checked=%d violations=%d" % (checked, len(bad)))
        rec["verify"] = {"checked": checked, "violations": len(bad)}
        certificates.append({"name": "D-odd-strict-even-noninc", "weights": w,
                             "odd_only": False})

    # ---- F: weights, strict only on odd x
    cons, v = build_weights(range(3, N + 1, 2))
    r, s, dt = solve(cons, args.timeout_ms)
    rec = report("F-odd-strict-only", cons, v, r, s, dt, results)
    if r == sat:
        w = v["extract"](s.model())
        Lmax = v["Lmax"]
        bad, checked = verify_weights(w, Lmax, N, odd_only=True)
        print("    pointwise verify (odd x only): checked=%d violations=%d %s"
              % (checked, len(bad), bad[:5]))
        rec["verify"] = {"checked": checked, "violations": len(bad)}
        # observation: does the tail follow -Fibonacci (F_0=0, F_1=1), i.e. w_i == -F_{i-3}?
        fib = [0, 1]
        while len(fib) <= Lmax + 4:
            fib.append(fib[-1] + fib[-2])
        matches_shift = [i for i in range(3, Lmax + 1) if w[i] == -fib[i - 3]]
        print("    weights = %s" % w)
        print("    indices i >= 3 where w_i == -Fibonacci(i-3): %s (of 3..%d),"
              " count %d" % (matches_shift[:40], Lmax, len(matches_shift)))
        rec["weights"] = w
        rec["neg_shifted_fibonacci_match"] = {"indices": matches_shift,
                                              "count": len(matches_shift),
                                              "range": "3..%d" % Lmax}
        # informational: how far does the certificate reach past the truncation?
        cover = 2 ** (Lmax + 1)
        limit = min(4 * N, cover - 1)
        t0 = time.time()
        first_bad = None
        reached = 0
        for x in range(3, limit + 1, 2):
            if T(x) >= cover:
                break
            reached = x
            if V_of_weights(w, Lmax, T(x)) > V_of_weights(w, Lmax, x) - 1:
                first_bad = x
                break
        print("    beyond-truncation scan (odd x up to %d, coverage limit %d,"
              " %.1fs): reached %d, first violation = %s"
              % (limit, cover, time.time() - t0, reached, first_bad))
        rec["beyond"] = {"limit": limit, "cover": cover, "reached": reached,
                         "first_violation": first_bad}
        certificates.append({"name": "F-odd-strict-only", "weights": w,
                             "odd_only": True})

    # ---- C: free V control (small N)
    cons, v = build_free_v(range(3, Nsmall + 1), Nsmall)
    r, s, dt = solve(cons, args.timeout_ms)
    rec = report("C-free-V-excl", cons, v, r, s, dt, results)
    if r == sat:
        m = s.model()
        bad, checked, unresolved = verify_free_v(v["vmap"], m, Nsmall)
        print("    pointwise verify over [3,%d]: checked=%d unresolved=%d"
              " violations=%d" % (Nsmall, checked, unresolved, len(bad)))
        rec["verify"] = {"checked": checked, "unresolved": unresolved,
                         "violations": len(bad)}

    # ---- P: per-k conflicting pairs (weights only), one solver per k
    print()
    print("per-k pair probe: x = 2^k - 1 and x = 2^k, weight class only")
    kmax = N.bit_length() - 1
    pair_records = []
    for k in range(1, kmax + 1):
        cons, v = build_weights([2 ** k - 1, 2 ** k])
        r, s, dt = solve(cons, args.timeout_ms)
        core = sorted(str(c) for c in s.unsat_core()) if r == unsat else []
        pair_records.append({"k": k, "result": str(r), "core": core})
    n_unsat = sum(1 for p in pair_records if p["result"] == "unsat")
    sample = {p["k"]: p["core"] for p in pair_records
              if p["k"] in (1, 2, kmax)}
    print("    k = 1..%d : %d unsat, %d other; sample cores: %s"
          % (kmax, n_unsat, kmax - n_unsat, sample))
    results.append({"name": "P-per-k-pairs", "kmax": kmax, "n_unsat": n_unsat,
                    "samples": sample, "pairs": pair_records})

    summary = {"N": N, "N_small": Nsmall, "timeout_ms": args.timeout_ms,
               "results": results, "certificates": certificates}
    if args.json_out:
        with open(args.json_out, "w") as fh:
            json.dump(summary, fh, indent=1)
        print("JSON written to %s" % args.json_out)
    print("---JSON-BEGIN---")
    print(json.dumps(summary))
    print("---JSON-END---")


if __name__ == "__main__":
    main()
