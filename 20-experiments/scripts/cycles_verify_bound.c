/* cycles_verify_bound.c —— 自算验证界 X0（正整数）与 Y0（负整数绝对值）
 *
 * 目的：为 Eliahou 与 Crandall 型环判据提供输入。
 *
 * 正侧：把 [1, X0) 内每个整数标为「到达 1」。判据由强归纳：
 *   n（n >= 2）到达 1  <=>  轨迹在某一时刻落到 v < n 且 v 到达 1（v = 1 是基例）。
 *   实现：按块递增处理 [A, A+BLOCK)；块内每个 n 迭代到「首次落出块外」（v < A）
 *   或「v = 1」或「回到 n 自身（出现环，报告）」；落块外时查表，因为 v 落在更早的
 *   块里且更早的块已判定完毕。
 * 负侧：三个已知环的全部元素为基例；n < 0 标为「到达已知环」。实现同上，
 *   迭代到落在环元素上（基例）、落出块外（查表）、或回到自身（新环，报告）。
 *
 * 保守性：步数上限内既未落块外也未落基例的 n 记为「未判定」，程序立即截断
 *   已验证范围到该 n 之前，不虚报。表用位表（1 bit/项）以省内存。
 *
 * 编译：cc -O3 -march=native -pthread -o cycles_verify_bound cycles_verify_bound.c
 * 运行：./cycles_verify_bound <X0> <Y0> [dump_upto]
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <pthread.h>
#include <stdatomic.h>
#include <stdint.h>
#include <time.h>

typedef unsigned __int128 u128;

static u128 Tstep(u128 x) {                 /* 加速映射 T，正数域（> 0） */
    if ((x & 1u) == 0) return x >> 1;
    return (3 * x + 1) >> 1;
}
/* 负数域：n < 0 时 T(n) = n/2（偶）或 (3n+1)/2（奇）；
   用 a = |n| 表示：偶 a -> a/2；奇 a -> (3a-1)/2。 */
static u128 Tstep_neg(u128 a) {
    if ((a & 1u) == 0) return a >> 1;
    return (3 * a - 1) >> 1;
}
static inline int getbit(const unsigned char *t, u128 i) { return (t[i >> 3] >> (i & 7)) & 1; }
static inline void setbit(unsigned char *t, u128 i) { t[i >> 3] |= (unsigned char)(1u << (i & 7)); }

static int g_steps_cap = 200000;
static u128 g_BLOCK = (u128)1 << 22;

/* ---------------- 正侧 ---------------- */
static unsigned char *g_good;
static u128 g_X0, g_blockA;
static _Atomic long long g_unres, g_newcyc, g_maxsteps;
static _Atomic u128 g_first_unres;
typedef struct { u128 lo, hi; } Task;

static void *pos_worker(void *arg) {
    Task *t = (Task *)arg;
    for (u128 n = t->lo; n < t->hi; n++) {
        u128 v = n;
        long long steps = 0;
        int resolved = 0;
        for (;;) {
            if (v == 1) { setbit(g_good, n); resolved = 1; break; }
            if (v == n && steps > 0) {
                atomic_fetch_add(&g_newcyc, 1);
                printf("CYCLE_POS n=%llu steps=%lld\n", (unsigned long long)n, steps);
                fflush(stdout);
                resolved = 1; break;
            }
            v = Tstep(v);
            steps++;
            if (v < g_blockA) {                 /* 落出块外：v 在更早的块，已判定 */
                if (getbit(g_good, v)) setbit(g_good, n);
                resolved = 1; break;
            }
            if (steps > g_steps_cap) {
                atomic_fetch_add(&g_unres, 1);
                u128 cur = atomic_load(&g_first_unres);
                while (n < cur && !atomic_compare_exchange_weak(&g_first_unres, &cur, n)) {}
                resolved = 1; break;
            }
        }
        if (steps > atomic_load(&g_maxsteps)) atomic_store(&g_maxsteps, steps);
    }
    return NULL;
}

/* ---------------- 负侧 ---------------- */
static unsigned char *g_goodn;
static unsigned char g_base[1024];         /* 三个已知环的元素（|值| < 1024） */
static u128 g_Y0, g_nblockA;
static _Atomic long long g_unres_n, g_newcyc_n;
static _Atomic u128 g_first_unres_n;

static void *neg_worker(void *arg) {
    Task *t = (Task *)arg;
    for (u128 a = t->lo; a < t->hi; a++) {     /* a = |n| */
        u128 v = a;
        long long steps = 0;
        for (;;) {
            if (v < 1024 && g_base[v]) { setbit(g_goodn, a); break; }     /* 基例：已知环元素 */
            if (v == a && steps > 0) {
                atomic_fetch_add(&g_newcyc_n, 1);
                printf("CYCLE_NEG n=-%llu steps=%lld\n", (unsigned long long)a, steps);
                fflush(stdout);
                break;
            }
            v = Tstep_neg(v);
            steps++;
            if (v < g_nblockA) {                /* 落出块外，查更早的块 */
                if (getbit(g_goodn, v)) setbit(g_goodn, a);
                break;
            }
            if (steps > g_steps_cap) {
                atomic_fetch_add(&g_unres_n, 1);
                u128 cur = atomic_load(&g_first_unres_n);
                while (a < cur && !atomic_compare_exchange_weak(&g_first_unres_n, &cur, a)) {}
                break;
            }
        }
    }
    return NULL;
}

static double now_s(void) {
    struct timespec ts; clock_gettime(CLOCK_MONOTONIC, &ts);
    return ts.tv_sec + 1e-9 * ts.tv_nsec;
}

/* 通用分块并行驱动：blk_end 是本次上界 */
static void run_blocks(u128 limit, void *(*fn)(void *), int pos) {
    const int NT = 8 * 16;
    for (u128 A = 1; A < limit; A += g_BLOCK) {
        u128 End = A + g_BLOCK; if (End > limit) End = limit;
        if (pos) g_blockA = A; else g_nblockA = A;
        u128 span = End - A;
        u128 chunk = (span + NT - 1) / NT;
        chunk = ((chunk + 7) / 8) * 8;          /* 字节对齐，避免相邻任务写同一位组 */
        if (chunk == 0) chunk = 8;
        Task tasks[NT]; int ntor = 0;
        pthread_t th[NT];
        for (int i = 0; i < NT; i++) {
            u128 lo = A + (u128)i * chunk;
            if (lo >= End) break;
            u128 hi = lo + chunk; if (hi > End) hi = End;
            tasks[ntor].lo = lo; tasks[ntor].hi = hi; ntor++;
        }
        for (int i = 1; i < ntor; i++) pthread_create(&th[i], NULL, fn, &tasks[i]);
        fn(&tasks[0]);
        for (int i = 1; i < ntor; i++) pthread_join(th[i], NULL);
        if ((pos ? atomic_load(&g_first_unres) : atomic_load(&g_first_unres_n)) < limit) break;
    }
}

int main(int argc, char **argv) {
    if (argc < 3) { fprintf(stderr, "usage: %s <X0> <Y0> [dump_upto]\n", argv[0]); return 2; }
    g_X0 = strtoull(argv[1], NULL, 10);
    g_Y0 = strtoull(argv[2], NULL, 10);
    u128 dump_upto = argc > 3 ? strtoull(argv[3], NULL, 10) : 0;

    printf("# cycles_verify_bound X0=%llu Y0=%llu steps_cap=%d\n",
           (unsigned long long)g_X0, (unsigned long long)g_Y0, g_steps_cap);

    /* 负侧基例：三个已知环的全部元素（由环自身迭代生成） */
    memset(g_base, 0, sizeof g_base);
    {
        u128 seeds[3] = {1, 5, 17};
        for (int s = 0; s < 3; s++) {
            u128 v = seeds[s];
            do {
                printf("# 负环基例 -%llu\n", (unsigned long long)v);
                if (v < 1024) g_base[v] = 1;
                v = Tstep_neg(v);
            } while (v != seeds[s]);
        }
    }
    fflush(stdout);

    /* ---------------- 正侧 ---------------- */
    double t0 = now_s();
    size_t bytes = (size_t)(g_X0 >> 3) + 8;
    g_good = calloc(bytes, 1);
    if (!g_good) { fprintf(stderr, "正侧位表分配失败（%zu 字节）\n", bytes); return 1; }
    printf("POS 位表 %zu 字节\n", bytes);
    atomic_store(&g_first_unres, g_X0);
    run_blocks(g_X0, pos_worker, 1);
    u128 first_unres = atomic_load(&g_first_unres);
    double t1 = now_s();

    long long checked = 0, mismatch = 0;
    u128 lim = 200000; if (lim > first_unres) lim = first_unres;
    for (u128 n = 1; n <= lim; n++) {
        u128 v = n; int reached = 0;
        for (long long s = 0; s < 2000000; s++) { if (v == 1) { reached = 1; break; } v = Tstep(v); }
        checked++;
        if (getbit(g_good, n) != reached) mismatch++;
    }
    printf("POS 已验证范围 [1, %llu)，未判定数=%lld，最大步数=%lld，用时=%.3fs\n",
           (unsigned long long)first_unres, atomic_load(&g_unres),
           atomic_load(&g_maxsteps), t1 - t0);
    printf("POS 抽样自检 n in [1, %llu]（完整迭代到 1 对照）：%lld 项，不一致 %lld\n",
           (unsigned long long)lim, checked, mismatch);
    /* 全域随机抽样自检：在 [1, first_unres) 内均匀取 20000 个 n，完整迭代到 1 对照 */
    {
        long long ns = 20000, bad = 0, done = 0;
        u128 seed = 88172645463325252ULL;
        for (long long i = 0; i < ns; i++) {
            seed = seed * 6364136223846793005ULL + 1442695040888963407ULL;
            u128 n = 1 + (seed >> 20) % (first_unres > 1 ? first_unres - 1 : (u128)1);
            u128 v = n; int reached = 0; long long st = 0;
            for (; st < 2000000; st++) { if (v == 1) { reached = 1; break; } v = Tstep(v); }
            if (st >= 2000000) { bad++; continue; }
            if (getbit(g_good, n) != reached) bad++;
            done++;
        }
        printf("POS 全域随机抽样 %lld 个 n（范围 [1, %llu)）：已判 %lld，不一致 %lld\n",
               ns, (unsigned long long)first_unres, done, bad);
    }
    printf("POS 发现环的个数：%lld（应为 0）\n", atomic_load(&g_newcyc));
    fflush(stdout);

    if (dump_upto > 0) {
        if (dump_upto > first_unres) dump_upto = first_unres;
        FILE *f = fopen("results/verify_bound_dump_pos.txt", "w");
        if (f) {
            for (u128 n = 1; n <= dump_upto; n++) fprintf(f, "%llu %d\n", (unsigned long long)n, getbit(g_good, n));
            fclose(f);
            printf("POS 表已导出前 %llu 项到 results/verify_bound_dump_pos.txt\n", (unsigned long long)dump_upto);
        } else printf("POS 表导出失败（打不开 results/verify_bound_dump_pos.txt）\n");
    }
    free(g_good); g_good = NULL;

    /* ---------------- 负侧 ---------------- */
    t0 = now_s();
    size_t bytesn = (size_t)(g_Y0 >> 3) + 8;
    g_goodn = calloc(bytesn, 1);
    if (!g_goodn) { fprintf(stderr, "负侧位表分配失败（%zu 字节）\n", bytesn); return 1; }
    printf("NEG 位表 %zu 字节\n", bytesn);
    for (int v = 1; v < 1024; v++) if (g_base[v]) setbit(g_goodn, (u128)v);
    atomic_store(&g_first_unres_n, g_Y0);
    run_blocks(g_Y0, neg_worker, 0);
    u128 first_unres_n = atomic_load(&g_first_unres_n);
    t1 = now_s();

    long long checkedn = 0, mismatch_n = 0;
    u128 limn = 200000; if (limn > first_unres_n) limn = first_unres_n;
    for (u128 a = 1; a <= limn; a++) {
        u128 v = a; int reached = 0;
        for (long long s = 0; s < 2000000; s++) {
            if (v < 1024 && g_base[v]) { reached = 1; break; }
            v = Tstep_neg(v);
        }
        checkedn++;
        if (getbit(g_goodn, a) != reached) mismatch_n++;
    }
    printf("NEG 已验证范围 |n| in [1, %llu)，未判定数=%lld，用时=%.3fs\n",
           (unsigned long long)first_unres_n, atomic_load(&g_unres_n), t1 - t0);
    printf("NEG 抽样自检 |n| in [1, %llu]（独立判定到已知环）：%lld 项，不一致 %lld\n",
           (unsigned long long)limn, checkedn, mismatch_n);
    /* 全域随机抽样自检：在 [1, first_unres_n) 内均匀取 20000 个 a = |n|，独立判定 */
    {
        long long ns = 20000, bad = 0, done = 0;
        u128 seed = 1442695040888963407ULL;
        for (long long i = 0; i < ns; i++) {
            seed = seed * 6364136223846793005ULL + 1442695040888963407ULL;
            u128 a = 1 + (seed >> 20) % (first_unres_n > 1 ? first_unres_n - 1 : (u128)1);
            u128 v = a; int reached = 0; long long st = 0;
            for (; st < 2000000; st++) {
                if (v < 1024 && g_base[v]) { reached = 1; break; }
                v = Tstep_neg(v);
            }
            if (st >= 2000000) { bad++; continue; }
            if (getbit(g_goodn, a) != reached) bad++;
            done++;
        }
        printf("NEG 全域随机抽样 %lld 个 |n|（范围 [1, %llu)）：已判 %lld，不一致 %lld\n",
               ns, (unsigned long long)first_unres_n, done, bad);
    }
    if (atomic_load(&g_newcyc_n) > 0)
        printf("NEG 发现新环的个数：%lld\n", atomic_load(&g_newcyc_n));
    else
        printf("NEG 未发现三个已知负环之外的新环\n");
    fflush(stdout);
    return 0;
}
