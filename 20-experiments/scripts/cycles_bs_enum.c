/* cycles_bs_enum.c —— Böhm 与 Sontacchi 判据的奇偶向量搜索
 *
 * 判据（Böhm 与 Sontacchi 1978 的环方程；实现依照本项目
 * 10-literature/notes/cycles.md 第零节所记的推导）：
 *   设环在加速映射 T(n) = n/2（偶）、T(n) = (3n+1)/2（奇）下长度 k、奇数步 m 步，
 *   奇数步位置 0 = j_1 < j_2 < ... < j_m <= k-1（环从奇数项起，故 j_1 = 0），则环上元素
 *       x = c / (2^k - 3^m),   c = sum_{t=1..m} 3^(m-t) * 2^(j_t).
 *   2^k > 3^m 时 x > 0（正解），2^k < 3^m 时 x < 0（负解）。
 *
 * 搜索模式：
 *   mode 0：枚举长度 k 的全部 2^k 个向量，只做叶子整除判定，无结构性剪枝（地面真值）。
 *   mode 1：只搜 2^k > 3^m 一侧，两条剪枝：
 *     (a) 对数型必要条件给的 m 区间：任一环满足 0 < k*ln2 - m*ln3 <= m/(3*|x_min|-1)
 *         <= m/2（因 |x_min| >= 1），故 m >= k*ln2/(ln3+1/2)；又 2^k > 3^m 给
 *         m < k*ln2/ln3。前缀 (p,q) 若 q+(k-p) < m_min 或 q > m_max，剪掉。
 *     (b) 最小元定向不变式：把向量旋到环最小元（正环最小元为奇数），每个前缀的轨迹值
 *         x_p >= x_0 >= 1；由 x_p = (3^q x_0 + c_p)/2^p 得 c_p >= (2^p - 3^q)x_0，
 *         故 2^p > 3^q 时必有 c_p >= 2^p - 3^q；违反的前缀剪掉。
 *   mode 2：只搜 2^k < 3^m 一侧（负环），剪枝 (b) 换对称形式：3^q > 2^p 时
 *         必有 c_p >= (3^q - 2^p)*|x_0| >= 3^q - 2^p；违反的前缀剪掉。
 *   mode 3：两侧都搜（1 与 2 各跑一遍，结果合并）。
 *
 * 完备性论证（为什么剪枝不丢任何环）：
 *   1. 每个环的奇数步位置向量，经旋转后必可让位置 0 落在环的最小元上（正环最小元为奇数；
 *      负环最小元是绝对值最大的元素）。该旋转向量是真环的合法向量。
 *   2. 对旋转向量的任何前缀，轨迹值 x_p 是环上元素，故 x_p >= x_0（最小元），
 *      即 (3^q x_0 + c_p)/2^p >= x_0，即 c_p >= (2^p - 3^q) x_0。
 *   3. 又 x_0 >= 1（正侧）或 x_0 <= -1（负侧）。于是 2^p > 3^q 时 c_p >= 2^p - 3^q
 *      （正侧），3^q > 2^p 时 c_p >= 3^q - 2^p（负侧）。
 *   4. 剪枝 (b) 恰好剪去违反 3 的前缀——由 1、2、3，任何环的旋转向量都不会被剪；
 *      剪枝 (a) 剪去的 m 值由「环必然满足的对数型不等式」排除，同样不丢环。
 *
 * 编译：cc -O3 -march=native -pthread -o cycles_bs_enum cycles_bs_enum.c
 * 运行：./cycles_bs_enum <mode> <kmax> [threads] [kmin]
 */
#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include <time.h>
#include <stdatomic.h>
#include <stdint.h>

typedef __int128 i128;
typedef unsigned __int128 u128;

enum { MAXK = 62, MAXM = 192, MAXB = 14 };

static const double LOG2 = 0.69314718055994530942;
static const double LOG3 = 1.09861228866810969140;

/* ---------- i128 转字符串（不使用 strcpy） ---------- */
static void i128_to_str(i128 v, char *buf, size_t cap) {
    char tmp[64];
    int n = 0, neg = 0;
    unsigned __int128 u;
    if (cap < 2) return;
    if (v == 0) { buf[0] = '0'; buf[1] = 0; return; }
    if (v < 0) { neg = 1; u = (unsigned __int128)(-(v + 1)) + 1; } else { u = (unsigned __int128)v; }
    while (u > 0 && n < 63) { tmp[n++] = (char)('0' + (int)(u % 10)); u /= 10; }
    size_t p = 0;
    if (neg && p + 1 < cap) buf[p++] = '-';
    while (n > 0 && p + 1 < cap) buf[p++] = tmp[--n];
    buf[p] = 0;
}

/* ---------- 全局状态 ---------- */
static int g_prune_mode;          /* 当前子搜索的剪枝模式（0/1/2） */
static int g_k;
static u128 g_pow2k;
static i128 g_pow3[MAXM];
static i128 g_pow2p[64];           /* 2^p，p <= 63 */
static int g_mmin, g_mmax;
static int g_B;                   /* 前缀位数 */
static long long g_ntasks;        /* 2^B */
static _Atomic long long g_next_task;
static _Atomic long long g_nodes, g_leaves;
static _Atomic long long g_hits;
static pthread_mutex_t g_out_mu = PTHREAD_MUTEX_INITIALIZER;

static void emit(int k, int m, const int *ones, i128 c, i128 D, i128 x) {
    char cb[64], xb[64], db[64];
    i128_to_str(c, cb, sizeof cb);
    i128_to_str(x, xb, sizeof xb);
    i128_to_str(D, db, sizeof db);
    pthread_mutex_lock(&g_out_mu);
    printf("SOL k=%d m=%d x=%s c=%s D=%s ones=", k, m, xb, cb, db);
    for (int t = 0; t < m; t++) printf("%d%s", ones[t], (t + 1 < m) ? "," : "");
    printf("\n");
    fflush(stdout);
    pthread_mutex_unlock(&g_out_mu);
}

/* ---------- DFS ----------
 * 计数器走线程本地变量，避免热路径上的原子操作。
 * 叶子整除测试前先用一次比较跳过 |D| > c 的情形（c 是正数，|D| > c 时不可能整除，
 * 除非 c = 0，即 m = 0，那一路由单独的判定处理）。
 */
typedef struct { long long nodes, leaves, hits; } Ctr;

/* 叶子判定：c 是否被 D = 2^k - 3^m 整除（零判定用 |D| 等价）。 */
static void leaf_test(int q, i128 c, const int *ones, Ctr *ctr) {
    ctr->leaves++;
    i128 D = (i128)g_pow2k - g_pow3[q];
    if (D == 0) return;                           /* 2^k = 3^m 不会发生（一奇一偶） */
    if (q == 0 && c == 0) { ctr->hits++; emit(g_k, 0, ones, 0, D, 0); return; }
    i128 aD = (D < 0) ? -D : D;
    if (c < aD) return;                           /* |D| > c 且 c > 0：不可能整除 */
    int ok;
    const u128 U64MAX = (u128)0xFFFFFFFFFFFFFFFFULL;
    if ((u128)c <= U64MAX && (u128)aD <= U64MAX)
        ok = ((unsigned long long)c % (unsigned long long)aD == 0);   /* u64 快路径 */
    else
        ok = (c % D == 0);
    if (!ok) return;
    ctr->hits++;
    emit(g_k, q, ones, c, D, c / D);
}

static void dfs(int p, int q, i128 c, int *ones, int mode, Ctr *ctr) {
    ctr->nodes++;
    if (mode != 0) {
        if (q > g_mmax) return;
        if (q + (g_k - p) < g_mmin) return;
        i128 tq = g_pow3[q];
        if (mode == 1 && g_pow2p[p] > tq) {
            if (c < g_pow2p[p] - tq) return;      /* 剪枝 (b) 正侧 */
        } else if (mode == 2 && tq > g_pow2p[p]) {
            if (c < tq - g_pow2p[p]) return;      /* 剪枝 (b) 负侧 */
        }
    }
    if (p == g_k) {
        leaf_test(q, c, ones, ctr);
        return;
    }
    dfs(p + 1, q, c, ones, mode, ctr);            /* 位置 p 不取奇数步 */
    ones[q] = p;
    dfs(p + 1, q + 1, 3 * c + g_pow2p[p], ones, mode, ctr);
}

/* ---------- 工作线程 ---------- */
static void *worker(void *arg) {
    (void)arg;
    int ones[MAXM];
    Ctr ctr = {0, 0, 0};
    for (;;) {
        long long i = atomic_fetch_add(&g_next_task, 1);
        if (i >= g_ntasks) break;
        int q = 0; i128 c = 0;
        for (int p = 0; p < g_B; p++) {
            if ((i >> p) & 1LL) { ones[q++] = p; c = 3 * c + (i128)(((u128)1) << p); }
        }
        dfs(g_B, q, c, ones, g_prune_mode, &ctr);
    }
    atomic_fetch_add(&g_nodes, ctr.nodes);
    atomic_fetch_add(&g_leaves, ctr.leaves);
    atomic_fetch_add(&g_hits, ctr.hits);
    return NULL;
}

/* 跑一次子搜索，返回叶子数 */
static void run_subsearch(int mode, int k, int mmin, int mmax) {
    g_prune_mode = mode;
    g_k = k;
    g_pow2k = ((u128)1) << k;
    g_mmin = mmin;
    g_mmax = mmax;
    g_B = 0;
    while (g_B < k && g_B < MAXB && (((long long)1) << (g_B + 1)) <= 4096) g_B++;
    g_ntasks = ((long long)1) << g_B;
    atomic_store(&g_next_task, 0);
    pthread_t th[64];
    int nt = 8;
    for (int t = 1; t < nt; t++) pthread_create(&th[t], NULL, worker, NULL);
    worker(NULL);
    for (int t = 1; t < nt; t++) pthread_join(th[t], NULL);
}

int main(int argc, char **argv) {
    if (argc < 3) {
        fprintf(stderr, "usage: %s <mode:0|1|2|3> <kmax> [kmin]\n", argv[0]);
        return 2;
    }
    int mode = atoi(argv[1]);
    int kmax = atoi(argv[2]);
    int kmin = argc > 3 ? atoi(argv[3]) : 1;
    if (kmax > MAXK) kmax = MAXK;

    printf("# cycles_bs_enum mode=%d k=%d..%d threads=8\n", mode, kmin, kmax);
    printf("# SOL 行：k 环长、m 奇数步数、x 判据给出的环上元素、c 由奇偶向量决定、\n");
    printf("#        D = 2^k - 3^m、ones 奇数步位置（升序，逗号分隔）\n");
    fflush(stdout);

    g_pow3[0] = 1;
    for (int m = 1; m < MAXM; m++) g_pow3[m] = g_pow3[m - 1] * 3;
    g_pow2p[0] = 1;
    for (int p = 1; p < 64; p++) g_pow2p[p] = g_pow2p[p - 1] * 2;

    struct timespec t0, t1;
    clock_gettime(CLOCK_MONOTONIC, &t0);

    for (int k = kmin; k <= kmax; k++) {
        /* 精确判定分界：m_max_pos = 满足 3^m < 2^k 的最大 m（用整数比较，不用浮点） */
        i128 p2 = (i128)(((u128)1) << k);
        int m_max_pos = 0;
        while (m_max_pos + 1 < MAXM && g_pow3[m_max_pos + 1] < p2) m_max_pos++;
        /* 正侧（2^k > 3^m）m 属于 [0, m_max_pos]；负侧（2^k < 3^m）m 属于 [m_max_pos+1, k]。 */
        /* 剪枝 (a) 的下界：正侧由 |Lambda| <= m/(3|x_min|-1) <= m/2 得
           m >= k*ln2/(ln3 + 1/2) = 0.4336*k。取下取整以免出错（更弱的界仍然合法）。 */
        int m_min_pos = (int)((double)k * LOG2 / (LOG3 + 0.5));
        if (m_min_pos < 0) m_min_pos = 0;

        atomic_store(&g_nodes, 0); atomic_store(&g_leaves, 0); atomic_store(&g_hits, 0);
        struct timespec ka, kb;
        clock_gettime(CLOCK_MONOTONIC, &ka);

        if (mode == 0) {
            run_subsearch(0, k, 0, k);
        } else if (mode == 1) {
            run_subsearch(1, k, m_min_pos, m_max_pos);
        } else if (mode == 2) {
            run_subsearch(2, k, m_max_pos + 1, k);
        } else {
            run_subsearch(1, k, m_min_pos, m_max_pos);
            run_subsearch(2, k, m_max_pos + 1, k);
        }
        clock_gettime(CLOCK_MONOTONIC, &kb);
        double dt = (kb.tv_sec - ka.tv_sec) + 1e-9 * (kb.tv_nsec - ka.tv_nsec);
        printf("# k=%d nodes=%lld leaves=%lld hits=%lld sec=%.3f\n",
               k, atomic_load(&g_nodes), atomic_load(&g_leaves), atomic_load(&g_hits), dt);
        fflush(stdout);
    }
    clock_gettime(CLOCK_MONOTONIC, &t1);
    printf("# total_sec=%.3f\n", (t1.tv_sec - t0.tv_sec) + 1e-9 * (t1.tv_nsec - t0.tv_nsec));
    fflush(stdout);
    return 0;
}
