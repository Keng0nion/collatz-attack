"""z3 counterexample search for long Collatz orbits inside a truncation [1, N].

Run with the project venv:
  "/Users/luna/Documents/math IA/collatz-attack/20-experiments/.venv/bin/python" \
      smt_orbit_counterexample.py --N 1048576 --json-out ../results/smt_orbit.json

Query (satisfiability form, as asked):
    does there exist x with 1 <= x <= N whose accelerated Collatz orbit does not
    hit 1 within K steps?
Encoding: x is a 64-bit bit-vector; the orbit is unrolled K+1 times with
    y_{k+1} = ite(y_k odd, (3*y_k + 1) >> 1, y_k >> 1)
and the constraint set is { y_0 != 1, ..., y_K != 1 }.  A SAT answer returns a
concrete witness x, which is then re-simulated in exact Python integer arithmetic
(the true accelerated orbit) and the true total stopping time is reported.  The
encoding is also checked for faithfulness: the largest value the witness orbit
attains must stay far below 2^64, so no bit-vector wraparound can occur.

The script additionally computes, by direct integer arithmetic, the minimum x
below N whose true total stopping time exceeds K, and the maximum total stopping
time over [1, N], so the z3 witnesses can be compared against the exact records.

All numbers printed come from this run.
"""

import argparse
import json
import time

from z3 import BitVec, BitVecVal, If, LShR, Solver, UGE, ULE, sat

BITS = 64


def T(x):
    return x // 2 if x % 2 == 0 else (3 * x + 1) // 2


def orbit(x, cap=10 ** 7):
    """exact accelerated orbit until first hit of 1 (inclusive); returns
    (path, stopped) where stopped is True iff 1 was reached within cap steps."""
    path = [x]
    y = x
    for _ in range(cap):
        if y == 1:
            return path, True
        y = T(y)
        path.append(y)
    return path, False


def bv_query(N, K, timeout_ms):
    x = BitVec("x", BITS)
    s = Solver()
    s.set("timeout", timeout_ms)
    s.add(UGE(x, BitVecVal(1, BITS)), ULE(x, BitVecVal(N, BITS)))
    y = x
    cons = []
    for _ in range(K + 1):
        cons.append(y != BitVecVal(1, BITS))
        odd = (y & BitVecVal(1, BITS)) == BitVecVal(1, BITS)
        y = If(odd, LShR(y * BitVecVal(3, BITS) + BitVecVal(1, BITS), 1),
               LShR(y, 1))
    s.add(cons)
    t0 = time.time()
    r = s.check()
    dt = time.time() - t0
    out = {"N": N, "K": K, "result": str(r), "solve_secs": round(dt, 3),
           "n_constraints": K + 3}
    if r == sat:
        out["witness"] = int(str(s.model()[x]))
    return out


def max_stop_and_records(N):
    """exact total stopping times for all x <= N (same algorithm as
    direct_reference.py): returns ts array (dict) and the max."""
    ts_arr = [-1] * (N + 1)
    ts_arr[1] = 0
    big = {}
    for x in range(2, N + 1):
        if ts_arr[x] >= 0:
            continue
        path = []
        y = x
        base = None
        while True:
            if y < x and y <= N:
                base = ts_arr[y]
                break
            if y > N:
                if y in big:
                    base = big[y]
                    break
                path.append(y)
                y = T(y)
                continue
            if ts_arr[y] >= 0:
                base = ts_arr[y]
                break
            path.append(y)
            y = T(y)
        for z in reversed(path):
            base += 1
            if z <= N:
                ts_arr[z] = base
            else:
                big[z] = base
    return ts_arr


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--N", type=int, default=2 ** 20)
    ap.add_argument("--timeout-ms", type=int, default=600000)
    ap.add_argument("--json-out", type=str, default=None)
    ap.add_argument("--extra-k", type=int, nargs="*", default=[],
                    help="additional K values to test against N")
    args = ap.parse_args()
    N = args.N

    print("z3 BV orbit counterexample search, N = %d, 64-bit encoding" % N)
    print("=" * 78)
    ts_arr = max_stop_and_records(N)
    mx = max(t for t in ts_arr[1:])
    argmx = min(x for x in range(1, N + 1) if ts_arr[x] == mx)
    print("direct reference on [1, %d]: max total stopping time = %d at x = %d"
          % (N, mx, argmx))
    print()

    queries = [(N, 40), (N, 100), (N, 120), (N, 200), (N, 300),
               (2 ** 10, 200), (2 ** 16, 200)]
    queries += [(N, K) for K in args.extra_k]
    records = []
    for (Nq, K) in queries:
        q = bv_query(Nq, K, args.timeout_ms)
        exact = [z for z in range(1, Nq + 1) if ts_arr[z] > K] if Nq == N else None
        if exact is None:
            # small-N control: recompute directly
            sub = max_stop_and_records(Nq)
            exact = [z for z in range(1, Nq + 1) if sub[z] > K]
        q["exact_exists"] = bool(exact)
        q["exact_min_witness"] = min(exact) if exact else None
        line = ("z3: N=%-8d K=%-4d -> %-8s %6.2fs"
                % (Nq, K, q["result"], q["solve_secs"]))
        line += " | exact: exists=%s min=%s" % (
            q["exact_exists"], q["exact_min_witness"])
        if q["result"] == "sat":
            x = q["witness"]
            path, stopped = orbit(x)
            true_stop = None if not stopped else len(path) - 1
            peak = max(path)
            q["true_stop"] = true_stop
            q["peak"] = peak
            q["peak_below_2_64"] = peak < 2 ** 64
            seq = [x]
            y = x
            for _ in range(K + 1):
                y = (3 * y + 1) // 2 if y % 2 else y // 2
                seq.append(y)
            agree = all(a == b for a, b in zip(seq, path))
            q["bv_sequence_matches_exact"] = agree
            line += ("\n      witness x=%d  true_stop=%s  peak=%d (<2^64: %s)"
                     "  bv-seq==exact: %s"
                     % (x, true_stop, peak, peak < 2 ** 64, agree))
            line += "  witness_is_minimal: %s" % (x == q["exact_min_witness"])
        print(line)
        records.append(q)

    summary = {"N": N, "max_stop": mx, "argmax_min": argmx,
               "queries": records}
    if args.json_out:
        with open(args.json_out, "w") as fh:
            json.dump(summary, fh, indent=1)
        print("JSON written to %s" % args.json_out)
    print("---JSON-BEGIN---")
    print(json.dumps(summary))
    print("---JSON-END---")


if __name__ == "__main__":
    main()
