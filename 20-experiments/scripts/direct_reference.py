"""Direct (non-SMT) reference computation for the certificate experiment.

Run with the project venv:
  /Users/luna/Documents/math IA/collatz-attack/20-experiments/.venv/bin/python direct_reference.py --N 1048576

Computes, by exact integer arithmetic only (no solver):
  1. the accelerated map T on [1, N] and the count of exits,
  2. cycle detection in the functional graph of T over [1, N],
  3. total stopping time (first hit of 1) for every x <= N, its maximum and records,
  4. the per-k conflicting pairs (2^k - 1, 2^k) derived in closed form for the
     bit-additive weight class, checked by direct coefficient computation,
  5. frequency of popcount preservation popcount(T(x)) == popcount(x),
  6. pointwise re-verification of any weight vector stored in a JSON file
     (option --verify-json) over a requested range.

All numbers printed here come from this run.
"""

import argparse
import json
import sys
import time


def T(x):
    """Accelerated Collatz step: x/2 if x even, (3x+1)/2 if x odd."""
    if x % 2 == 0:
        return x // 2
    return (3 * x + 1) // 2


def popcount(x):
    return bin(x).count("1")


def bit_index_sets(x):
    return {i for i in range(x.bit_length()) if (x >> i) & 1}


def part_cycles(N):
    """Find cycles of T fully contained in [1, N] via linear-time colouring.

    A node whose image leaves [1, N] terminates its walk; such nodes cannot lie
    on a cycle contained in [1, N].  Each node joins at most one path, so the
    total work is O(N).
    """
    colour = bytearray(N + 1)  # 0 = unseen, 1 = on current path, 2 = done
    pos = [-1] * (N + 1)
    cycles = []
    for start in range(1, N + 1):
        if colour[start]:
            continue
        path = []
        x = start
        while True:
            if x > N:
                break
            c = colour[x]
            if c == 2:
                break
            if c == 1:
                cycles.append(sorted(path[pos[x]:]))
                break
            colour[x] = 1
            pos[x] = len(path)
            path.append(x)
            x = T(x)
        for y in path:
            colour[y] = 2
    exits = sum(1 for x in range(1, N + 1) if T(x) > N)
    return cycles, exits


def part_stopping_times(N, step_cap=10 ** 6):
    """total stopping time for every x in [1, N]: least k >= 0 with T^k(x) = 1.

    Exact integer arithmetic, no value horizon.  Walk each unprocessed x forward
    until the orbit hits 1, a value already resolved, or a value below the walk's
    own start (all of which have known stopping time), then backtrack.  Values
    above N are memoised in a dict.  step_cap guards against non-termination; if
    it is ever hit the affected value is reported as unresolved.
    """
    ts_arr = [-1] * (N + 1)
    ts_arr[1] = 0
    big = {}
    unresolved = []
    for x in range(2, N + 1):
        if ts_arr[x] >= 0:
            continue
        path = []
        y = x
        steps = 0
        base = None
        while True:
            steps += 1
            if steps > step_cap:
                unresolved.append(x)
                break
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
        if base is None:
            for z in path:
                if z <= N and ts_arr[z] < 0:
                    ts_arr[z] = -2
            continue
        for z in reversed(path):
            base += 1
            if z <= N:
                ts_arr[z] = base
            else:
                big[z] = base
    vals = {x: ts_arr[x] for x in range(1, N + 1) if ts_arr[x] >= 0}
    unresolved = [x for x in range(1, N + 1) if ts_arr[x] < 0]
    return vals, unresolved


def part_conflict_pairs(kmax):
    """For the bit-additive class V(z) = sum_i w_i bit_i(z), for each k the pair
    (2^k - 1, 2^k) gives two constraints on w_{k-1}, w_k.  Derive the coefficient
    vectors exactly and check the claimed closed form

        x = 2^k - 1 :  w_k - w_{k-1} <= -1
        x = 2^k     :  w_{k-1} - w_k <= -1

    where coefficient vectors are (added bits of T(x)) minus (bits of x).
    """
    out = []
    for k in range(1, kmax + 1):
        a = 2 ** k - 1
        b = 2 ** k
        add_lo = sorted(bit_index_sets(T(a)) - bit_index_sets(a))
        del_lo = sorted(bit_index_sets(a) - bit_index_sets(T(a)))
        add_hi = sorted(bit_index_sets(T(b)) - bit_index_sets(b))
        del_hi = sorted(bit_index_sets(b) - bit_index_sets(T(b)))
        pattern_ok = (add_lo == [k] and del_lo == [k - 1]
                      and add_hi == [k - 1] and del_hi == [k])
        out.append(
            {
                "k": k,
                "x_lo": a,
                "x_hi": b,
                "T_lo": T(a),
                "T_hi": T(b),
                "add_lo": add_lo,
                "del_lo": del_lo,
                "add_hi": add_hi,
                "del_hi": del_hi,
                "pattern_ok": pattern_ok,
            }
        )
    return out


def verify_weights(w, Lmax, N, odd_only=False):
    """pointwise check of a bit-additive weight vector over x in [3, N]."""
    def V(z):
        return sum(w[i] for i in range(Lmax + 1) if (z >> i) & 1)

    bad = []
    for x in range(3, N + 1):
        if odd_only and x % 2 == 0:
            continue
        if not (V(T(x)) <= V(x) - 1):
            bad.append(x)
            if len(bad) >= 20:
                break
    return bad


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--N", type=int, default=2 ** 20)
    ap.add_argument("--verify-json", type=str, default=None)
    ap.add_argument("--odd-only", action="store_true")
    args = ap.parse_args()
    N = args.N

    report = {"N": N, "sections": []}

    t0 = time.time()
    cycles, exits = part_cycles(N)
    dt_cyc = time.time() - t0
    nontrivial = [c for c in cycles if c != [1, 2]]
    print("== 1. functional graph of T over [1, %d] ==" % N)
    print("   cycles found by colouring: %d" % len(cycles))
    for c in cycles[:10]:
        print("     cycle:", c[:12], "len=%d" % len(c))
    print("   nontrivial cycles (not [1,2]): %d" % len(nontrivial))
    print("   #{x in [1,N]: T(x) > N} = %d (orbit leaves the truncation)" % exits)
    print("   elapsed %.2fs" % dt_cyc)
    report["sections"].append(
        {"name": "cycles", "N": N, "cycles": cycles, "nontrivial": len(nontrivial),
         "exits": exits, "secs": round(dt_cyc, 3)}
    )

    t0 = time.time()
    tvals, unresolved = part_stopping_times(N)
    dt_st = time.time() - t0
    mx = max(tvals.values())
    argmx = min(x for x in tvals if tvals[x] == mx)
    print("== 2. total stopping time (first hit of 1, accelerated map) ==")
    print("   computed for %d values in [1, %d]; unresolved: %d"
          % (len(tvals), N, len(unresolved)))
    print("   max total stopping time = %d, smallest x attaining it = %d" % (mx, argmx))
    top = sorted(tvals.items(), key=lambda kv: (-kv[1], kv[0]))[:10]
    print("   top ten (x, stopping time):", top)
    print("   elapsed %.2fs" % dt_st)
    report["sections"].append(
        {"name": "stopping_time", "N": N, "counted": len(tvals),
         "unresolved": len(unresolved), "max_stop": mx, "argmax_min": argmx,
         "top10": top, "secs": round(dt_st, 3)}
    )

    kmax = (N.bit_length() - 1)
    pairs = part_conflict_pairs(kmax)
    ok = sum(1 for p in pairs if p["pattern_ok"])
    print("== 3. conflicting pairs (2^k - 1, 2^k) for the bit-additive class ==")
    print("   each row: added bits of T(x) (+), removed bits (-), for the two x")
    for p in pairs[:6] + (pairs[-3:] if kmax > 9 else []):
        print("   k=%-3d x=%-9d T=%-9d  +%-6s -%-6s  |  x=%-9d T=%-9d  +%-6s -%-6s  ok=%s"
              % (p["k"], p["x_lo"], p["T_lo"], p["add_lo"], p["del_lo"],
                 p["x_hi"], p["T_hi"], p["add_hi"], p["del_hi"], p["pattern_ok"]))
    print("   k = 1..%d checked; closed form w_k - w_{k-1} <= -1 against "
          "w_{k-1} - w_k <= -1 holds for %d of them" % (kmax, ok))
    report["sections"].append({"name": "conflict_pairs", "kmax": kmax,
                               "pattern_ok_count": ok, "pairs": pairs})

    t0 = time.time()
    same = 0
    odd_same = 0
    first_examples = []
    for x in range(1, N + 1):
        if popcount(T(x)) == popcount(x):
            same += 1
            if x % 2 == 1:
                odd_same += 1
            if len(first_examples) < 10:
                first_examples.append(x)
    dt_pc = time.time() - t0
    print("== 4. popcount preservation ==")
    print("   #{x in [1,N]: popcount(T(x)) == popcount(x)} = %d (of %d)" % (same, N))
    print("   #{odd x in [1,N]: same} = %d" % odd_same)
    print("   first examples:", first_examples)
    print("   elapsed %.2fs" % dt_pc)
    report["sections"].append(
        {"name": "popcount_preserved", "N": N, "count": same, "odd_count": odd_same,
         "examples": first_examples, "secs": round(dt_pc, 3)}
    )

    if args.verify_json:
        with open(args.verify_json) as fh:
            blob = json.load(fh)
        print("== 5. pointwise re-verification of a stored weight vector ==")
        for cert in blob.get("certificates", []):
            w = cert["weights"]
            Lmax = len(w) - 1
            odd_only = cert.get("odd_only", False)
            bad = verify_weights(w, Lmax, N, odd_only=odd_only)
            print("   cert '%s' (Lmax=%d, odd_only=%s): violations over x in [3,%d] = %d"
                  % (cert.get("name"), Lmax, odd_only, N, len(bad)))
            report["sections"].append(
                {"name": "verify", "cert": cert.get("name"), "Lmax": Lmax,
                 "odd_only": odd_only, "violations": len(bad), "first_bad": bad[:10]}
            )

    print()
    print("done. total elapsed %.2fs" % (time.time() - t0))
    print("JSON report on stdout between markers below.")
    print("---JSON-BEGIN---")
    print(json.dumps(report))
    print("---JSON-END---")


if __name__ == "__main__":
    main()
