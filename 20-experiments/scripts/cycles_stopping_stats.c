/* cycles_stopping_stats.c —— 统计「落到自身以下所需步数」sigma(n) 的代价，用于标定
 * 无表验证（iterate-until-below-start）能推到多大的 X0。
 *
 * 无表验证的原理：n（>= 2）到达 1  <=>  轨迹某一时刻落到 v < n 且 v 到达 1。
 * 由强归纳，只需对每个 n 检查「轨迹是否落到 < n」（可用步数上限兜底），
 * 不需要任何表——这是把验证界推大的关键（表法受内存限制）。
 *
 * 本程序给出 sigma 的和、均值、最大值与分位数，用以估算目标范围的总步数。
 *
 * 编译：cc -O3 -march=native -pthread -o cycles_stopping_stats cycles_stopping_stats.c
 * 运行：./cycles_stopping_stats <X0> [samples]
 */
#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include <stdatomic.h>
#include <stdint.h>
#include <time.h>

typedef unsigned __int128 u128;

static u128 Tstep(u128 x) { if ((x & 1u) == 0) return x >> 1; return (3 * x + 1) >> 1; }
static u128 Tstep_neg(u128 a) { if ((a & 1u) == 0) return a >> 1; return (3 * a - 1) >> 1; }

static u128 g_hi;                     /* 覆盖 [1, g_hi) */
static int g_cap = 1000000;
static _Atomic unsigned long long g_sum, g_max, g_over, g_cnt;
static _Atomic unsigned long long g_hist[64];   /* 按 2 的幂分桶 */

static void *worker(void *arg) {
    long long tid = (long long)(intptr_t)arg;
    int nt = 8;
    u128 sum = 0; unsigned long long mx = 0, over = 0, cnt = 0;
    unsigned long long hist[64] = {0};
    for (u128 n = 1 + tid; n < g_hi; n += nt) {
        u128 v = n; int steps = 0;
        for (;;) {
            v = Tstep(v); steps++;
            if (v < n) break;
            if (steps > g_cap) { over++; break; }
        }
        sum += steps; if ((unsigned long long)steps > mx) mx = steps;
        int b = 0; int s = steps; while (s > 1) { s >>= 1; b++; }
        hist[b]++; cnt++;
    }
    atomic_fetch_add(&g_sum, (unsigned long long)sum);
    atomic_fetch_add(&g_cnt, cnt);
    atomic_fetch_add(&g_over, over);
    for (int i = 0; i < 64; i++) if (hist[i]) atomic_fetch_add(&g_hist[i], hist[i]);
    unsigned long long cur = atomic_load(&g_max);
    while (mx > cur && !atomic_compare_exchange_weak(&g_max, &cur, mx)) {}
    return NULL;
}

int main(int argc, char **argv) {
    if (argc < 2) { fprintf(stderr, "usage: %s <X0>\n", argv[0]); return 2; }
    g_hi = strtoull(argv[1], NULL, 10);
    printf("# cycles_stopping_stats X0=%llu（正侧 sigma(n)：首次 T^i(n) < n 的 i）\n",
           (unsigned long long)g_hi);
    struct timespec t0, t1; clock_gettime(CLOCK_MONOTONIC, &t0);
    pthread_t th[8];
    for (long long i = 1; i < 8; i++) pthread_create(&th[i], NULL, worker, (void *)(intptr_t)i);
    worker((void *)(intptr_t)0);
    for (int i = 1; i < 8; i++) pthread_join(th[i], NULL);
    clock_gettime(CLOCK_MONOTONIC, &t1);
    double dt = (t1.tv_sec - t0.tv_sec) + 1e-9 * (t1.tv_nsec - t0.tv_nsec);
    unsigned long long sum = atomic_load(&g_sum), cnt = atomic_load(&g_cnt);
    printf("计数=%llu 总步数=%llu 均值=%.4f 最大=%llu 超上限=%llu 用时=%.3fs 步/秒=%.3g\n",
           cnt, sum, (double)sum / (double)cnt, atomic_load(&g_max), atomic_load(&g_over),
           dt, (double)sum / dt);
    printf("sigma 分布（桶 [2^b, 2^(b+1))）：\n");
    unsigned long long cum = 0;
    for (int i = 0; i < 40; i++) {
        unsigned long long h = atomic_load(&g_hist[i]);
        if (!h) continue;
        cum += h;
        printf("  2^%d..2^%d: %llu  (累计占比 %.4f)\n", i, i + 1, h, (double)cum / (double)cnt);
    }
    return 0;
}
