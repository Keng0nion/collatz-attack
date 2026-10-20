/* cycles_verify_free.c —— 无表验证界：正整数到 1，负整数到三个已知环
 *
 * 原理（比位表法省内存，可把范围推大）：
 *   正侧：n（>= 2）到达 1  <=>  轨迹某一时刻落到 v < n 且 v 到达 1。
 *   由对 n 的强归纳（基例 n = 1），只需对每个 n 检验「轨迹是否落到过 < n 的值」。
 *   负侧：n = -a（a >= 1）到达三个已知负环之一  <=>  轨迹落到 |v| < a 的 v，
 *   或直接落到三个已知环的元素上（基例集合 = {1,5,7,10,17,25,34,37,41,55,61,68,82,91,136}）。
 *   同样是对 a 的强归纳。
 * 于是完全不需要表，只需要逐步迭代；代价 = 所有 n 的 sigma(n) 之和。
 * 兜底：步数超过上限（默认 10000000）或轨迹回到 n 自身（= 出现环，报出来）时，
 *   把该 n 记为「未判定」，程序据实截断已验证范围。
 *
 * 编译：cc -O3 -march=native -pthread -o cycles_verify_free cycles_verify_free.c
 * 运行：./cycles_verify_free <X0> <Y0> [threads]
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <pthread.h>
#include <stdatomic.h>
#include <stdint.h>
#include <time.h>

typedef unsigned __int128 u128;

static u128 Tstep(u128 x) { if ((x & 1u) == 0) return x >> 1; return (3 * x + 1) >> 1; }
static u128 Tstep_neg(u128 a) { if ((a & 1u) == 0) return a >> 1; return (3 * a - 1) >> 1; }

static long long g_cap = 10000000;
static unsigned char g_base[1024];
static int g_neg;                                  /* 当前跑的是哪一侧（跑前设定，线程只读） */
static _Atomic unsigned long long g_unres, g_cyc, g_sumsteps, g_maxsteps;
static _Atomic u128 g_first_unres;
static _Atomic long long g_nextchunk;
static u128 g_limit, g_chunk;

static void *worker(void *varg) {
    (void)varg;
    const int neg = g_neg;
    unsigned long long sumsteps = 0, mx = 0;
    u128 first = g_limit;
    unsigned long long unres = 0, cyc = 0;
    for (;;) {
        long long c = atomic_fetch_add(&g_nextchunk, 1);
        u128 lo = 1 + (u128)c * g_chunk;
        if (lo >= g_limit) break;
        u128 hi = lo + g_chunk; if (hi > g_limit) hi = g_limit;
        for (u128 n = lo; n < hi; n++) {
            if (!neg && n == 1) continue;                 /* 正侧基例 */
            if (neg && n < 1024 && g_base[n]) continue;   /* 负侧基例 */
            u128 v = n;
            long long steps = 0;
            int bad = 0;
            for (;;) {
                v = neg ? Tstep_neg(v) : Tstep(v);
                steps++;
                if (neg && v < 1024 && g_base[v]) break;
                if (v < n) break;
                if (v == n) {
                    cyc++; bad = 1;
                    printf("CYCLE %s n=%llu steps=%lld\n", neg ? "NEG" : "POS",
                           (unsigned long long)n, steps);
                    fflush(stdout);
                    break;
                }
                if (steps > g_cap) { unres++; bad = 1; break; }
            }
            sumsteps += steps;
            if ((unsigned long long)steps > mx) mx = steps;
            if (bad && n < first) first = n;
        }
    }
    atomic_fetch_add(&g_sumsteps, sumsteps);
    atomic_fetch_add(&g_unres, unres);
    atomic_fetch_add(&g_cyc, cyc);
    u128 cur = atomic_load(&g_first_unres);
    while (first < cur && !atomic_compare_exchange_weak(&g_first_unres, &cur, first)) {}
    unsigned long long cm = atomic_load(&g_maxsteps);
    while (mx > cm && !atomic_compare_exchange_weak(&g_maxsteps, &cm, mx)) {}
    return NULL;
}

static double now_s(void) {
    struct timespec t; clock_gettime(CLOCK_MONOTONIC, &t);
    return t.tv_sec + 1e-9 * t.tv_nsec;
}

int main(int argc, char **argv) {
    if (argc < 3) { fprintf(stderr, "usage: %s <X0> <Y0> [threads]\n", argv[0]); return 2; }
    u128 X0 = strtoull(argv[1], NULL, 10), Y0 = strtoull(argv[2], NULL, 10);
    int nth = argc > 3 ? atoi(argv[3]) : 8;

    memset(g_base, 0, sizeof g_base);
    {
        u128 seeds[3] = {1, 5, 17};
        for (int s = 0; s < 3; s++) {
            u128 v = seeds[s];
            do { if (v < 1024) g_base[v] = 1; v = Tstep_neg(v); } while (v != seeds[s]);
        }
    }
    printf("# cycles_verify_free X0=%llu Y0=%llu threads=%d steps_cap=%lld\n",
           (unsigned long long)X0, (unsigned long long)Y0, nth, g_cap);
    fflush(stdout);

    for (int pass = 0; pass < 2; pass++) {
        g_neg = pass;
        g_limit = pass ? Y0 : X0;
        g_chunk = (u128)1 << 20;
        atomic_store(&g_nextchunk, 0);
        atomic_store(&g_unres, 0); atomic_store(&g_cyc, 0);
        atomic_store(&g_sumsteps, 0); atomic_store(&g_maxsteps, 0);
        atomic_store(&g_first_unres, g_limit);
        double t0 = now_s();
        pthread_t th[64];
        int nt = nth > 64 ? 64 : nth;
        for (int i = 1; i < nt; i++) pthread_create(&th[i], NULL, worker, NULL);
        worker(NULL);
        for (int i = 1; i < nt; i++) pthread_join(th[i], NULL);
        double dt = now_s() - t0;
        u128 first = atomic_load(&g_first_unres);
        printf("%s 已验证范围 [1, %llu)（请求上限 %llu），未判定=%llu，发现环=%llu，"
               "总步数=%llu，最大步数=%llu，用时=%.1fs，步/秒=%.3g\n",
               pass ? "NEG" : "POS",
               (unsigned long long)first, (unsigned long long)g_limit,
               atomic_load(&g_unres), atomic_load(&g_cyc),
               atomic_load(&g_sumsteps), atomic_load(&g_maxsteps), dt,
               (double)atomic_load(&g_sumsteps) / dt);
        fflush(stdout);
    }
    return 0;
}
