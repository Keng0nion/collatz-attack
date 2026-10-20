/* cycle_search.c —— 奇偶向量完备环搜索（Böhm 与 Sontacchi 判据的精确实现）
 *
 * 对每个长度 k <= K 的奇偶向量 v（穷举全部 2^k 个），维护仿射常数 c（有符号 __int128）与奇步数 m，
 * 判据：x = c/(2^k - 3^m)。
 *   - 若 2^k > 3^m 且 (2^k-3^m) | c 且 x > 0 且 x 的奇偶向量恰为 v，则 x 落在正环上；
 *   - 若 2^k < 3^m 且 |2^k-3^m| | c 且 x < 0 且 x 的奇偶向量恰为 v，则 x 落在负环上。
 * 剪枝：|2^k-3^m| > c 时必有 c/|...| < 1，故无整数解（x != 0），跳过除法。
 * 同时统计「只满足整除性、不满足奇偶向量一致性」的伪命中（判据朴素使用陷阱），
 * 以及 1 圈型向量（1^m 0^j）上出现的环（Steiner 型「无 1 圈」的正面控制）。
 * 编译：cc -O3 -o scripts/cycle_search scripts/cycle_search.c
 * 运行：scripts/cycle_search [K]（默认 30）[ -d 打印每次命中 ]
 */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <time.h>

typedef __int128 i128;

static int KMAX = 30;
static int DEBUG = 0;
static uint64_t pow2v[64], pow3v[64];
static unsigned char bits[64];

#define MAXREC 16384
typedef struct { long long x; int k, m; int ok; int is1; } Rec;
static Rec recs[MAXREC];
static long long nrecs = 0;
static long long nodes = 0, hits = 0, badhits = 0, pruned = 0;
static long long npos = 0, nneg = 0;
static long long bad_min_abs = -1, bad_min_x = 0;
static int bad_min_k = 0;
static long long n1cyc_hits = 0;
static long long ndeg = 0;               /* c = 0 的节点（全零向量），对应退化解 x = 0 */
static long long onecyc_reps[256];
static int n_onecyc_reps = 0;

static void put_i128(i128 v, char *buf) {
    char tmp[64];
    int i = 0;
    if (v == 0) { buf[0] = '0'; buf[1] = 0; return; }
    int neg = v < 0;
    if (neg) v = -v;
    while (v > 0) { tmp[i++] = (char)('0' + (int)(v % 10)); v /= 10; }
    int j = 0;
    if (neg) buf[j++] = '-';
    for (int t = 0; t < i; t++) buf[j + t] = tmp[i - 1 - t];
    buf[j + i] = 0;
}

static int pv_match(long long x, int k) {
    long long z = x;
    for (int i = 0; i < k; i++) {
        int b = (int)(((unsigned long long)z) & 1ULL);
        if (b != bits[i]) return 0;
        z = b ? (3 * z + 1) / 2 : z / 2;
    }
    return 1;
}

/* 向量形如 1^m 0^j（先若干 1 再全 0）？ */
static int is_one_run(int k) {
    int seen0 = 0;
    for (int i = 0; i < k; i++) {
        if (bits[i] == 0) seen0 = 1;
        else if (seen0) return 0;
    }
    return 1;
}

static void test_node(i128 c, int k, int m) {
    if (c == 0) { ndeg++; return; }          /* 全零向量：整除性平凡成立，退化解 x = 0，按约定排除 */
    i128 d = (i128)pow2v[k] - (i128)pow3v[m];
    if (d == 0) return;
    i128 ad = (d < 0) ? -d : d;
    if (ad > c) { pruned++; return; }        /* 此时 0 < c/ad < 1，无整数解 x != 0 */
    if (c % ad != 0) return;
    hits++;
    i128 xq = c / ad;
    if (d < 0) xq = -xq;
    const i128 LIM = (((i128)1) << 62);
    if (xq > LIM || xq < -LIM) return;
    long long x = (long long)xq;
    if (x == 0) return;
    int ok = pv_match(x, k);
    int is1 = is_one_run(k);
    if (DEBUG)
        printf("[debug] k=%d m=%d c=%lld d=%lld x=%lld pv=%d is1=%d\n",
               k, m, (long long)c, (long long)d, x, ok, is1);
    if (nrecs < MAXREC) {
        recs[nrecs].x = x; recs[nrecs].k = k; recs[nrecs].m = m;
        recs[nrecs].ok = ok; recs[nrecs].is1 = is1;
    }
    nrecs++;
    if (ok) {
        if (d > 0) npos++; else nneg++;
        if (is1) {
            n1cyc_hits++;
            if (d > 0) {
                int dup = 0;
                for (int i = 0; i < n_onecyc_reps; i++) if (onecyc_reps[i] == x) dup = 1;
                if (!dup && n_onecyc_reps < 256) onecyc_reps[n_onecyc_reps++] = x;
            }
        }
    } else {
        badhits++;
        long long ax = x < 0 ? -x : x;
        if (bad_min_abs < 0 || ax < bad_min_abs) { bad_min_abs = ax; bad_min_x = x; bad_min_k = k; }
    }
}

static void dfs(int k, i128 c, int m) {
    if (k >= 1) { nodes++; test_node(c, k, m); }
    if (k == KMAX) return;
    bits[k] = 0;
    dfs(k + 1, c, m);
    bits[k] = 1;
    dfs(k + 1, 3 * c + (i128)pow2v[k], m + 1);
}

static int verify_cycle(long long x, int k) {
    long long z = x;
    for (int i = 0; i < k; i++) z = (z & 1) ? (3 * z + 1) / 2 : z / 2;
    return z == x;
}

int main(int argc, char **argv) {
    if (argc > 1) KMAX = atoi(argv[1]);
    if (argc > 2 && strcmp(argv[2], "-d") == 0) DEBUG = 1;
    if (KMAX < 1 || KMAX > 40) { fprintf(stderr, "K 越界\n"); return 2; }
    pow2v[0] = 1; pow3v[0] = 1;
    for (int i = 1; i < 64; i++) { pow2v[i] = pow2v[i - 1] * 2; pow3v[i] = pow3v[i - 1] * 3; }

    clock_t t0 = clock();
    dfs(0, 0, 0);
    double el = (double)(clock() - t0) / CLOCKS_PER_SEC;

    printf("K = %d（穷举长度 1..%d 的全部奇偶向量）\n", KMAX, KMAX);
    printf("枚举节点数（向量数）= %lld\n", nodes);
    printf("被剪枝（|2^k-3^m| > c，必无解）的节点数 = %lld\n", pruned);
    printf("满足整除性 |2^k-3^m| | c 的命中数 = %lld（不含退化解 x = 0）\n", hits);
    printf("退化解节点（c = 0 的全零向量，x = 0，按约定排除在外）= %lld 个；含之则整除成立节点共 %lld 个\n", ndeg, hits + ndeg);
    printf("其中奇偶向量一致性通过（真环）= %lld：正环 %lld 次、负环 %lld 次\n", npos + nneg, npos, nneg);
    printf("奇偶向量一致性失败（判据朴素使用下的伪命中）= %lld\n", badhits);
    if (bad_min_abs >= 0)
        printf("  最小伪命中：|x| = %lld（x = %lld，k = %d）\n", bad_min_abs, bad_min_x, bad_min_k);
    printf("1 圈型向量（1^m 0^j）上命中的真环次数 = %lld，涉及的正环 x 值 = ", n1cyc_hits);
    if (n_onecyc_reps == 0) printf("（无）");
    for (int i = 0; i < n_onecyc_reps; i++) printf("%lld%s", onecyc_reps[i], i + 1 < n_onecyc_reps ? ", " : "");
    printf("\n耗时 = %.2f 秒\n", el);

    char buf[64];
    long long seen[16384]; int nseen = 0;
    printf("\n命中的环（按 |x| 最小代表元去重）：\n");
    for (long long i = 0; i < nrecs && i < MAXREC; i++) {
        if (!recs[i].ok) continue;
        long long x = recs[i].x; int k = recs[i].k;
        if (k > 63) continue;
        long long orb[64];
        long long z = x;
        for (int t = 0; t < k; t++) { orb[t] = z; z = (z & 1) ? (3 * z + 1) / 2 : z / 2; }
        long long rep = orb[0], repsz = llabs(orb[0]);
        for (int t = 1; t < k; t++) if (llabs(orb[t]) < repsz) { repsz = llabs(orb[t]); rep = orb[t]; }
        int dup = 0;
        for (int t = 0; t < nseen; t++) if (seen[t] == rep) { dup = 1; break; }
        if (dup) continue;
        if (nseen < 16384) seen[nseen++] = rep;
        put_i128((i128)x, buf);
        char db[64];
        put_i128((i128)pow2v[k] - (i128)pow3v[recs[i].m], db);
        printf("  环代表元 %-6lld（命中 x = %-8s k = %2d, m = %2d, 2^k-3^m = %s, T^k(x)=x 直验 = %s）\n",
               rep, buf, k, recs[i].m, db, verify_cycle(x, k) ? "通过" : "失败");
    }
    printf("\n不同的环总数 = %d\n", nseen);
    return 0;
}
