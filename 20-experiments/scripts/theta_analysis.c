/*
 * theta_analysis.c
 * 对 Terras 系数停时猜想 tau(x) = chi(x)（x >= 2）做「向量侧」的穷举反例搜索。
 *
 * 原理（本脚本推导）：记 v = pv_k(x)、m_k = v 中 1 的个数、c_v 为仿射常数，则
 *   T^k(x) = (3^{m_k} x + c_v) / 2^k
 * 故 k = tau(x) 时 T^k(x) < x  <=>  x > theta_v := c_v / (2^k - 3^{m_k})。
 * 又 k = tau(x) 的向量必满足 3^{m_j} >= 2^j（j < k）与 3^{m_k} < 2^k（首降向量）。
 * 于是：点 x 破坏 tau = chi 当且仅当 x 属于某个首降向量的剩余类且 2 <= x <= theta_v。
 * 类元素为 r, r + 2^k, r + 2*2^k, ...（r = Phi(w) 为该类的最小非负元素），故只需对首降向量
 * 逐个检查 r <= theta_v —— 这就覆盖了所有 tau(x) <= KMAX 的 x（x 可以任意大）。
 * 只沿「尚未首降」的前缀做 DFS（一旦 3^{m_j} < 2^j 就剪枝），故代价远低于 2^K。
 * 编译：cc -O3 -o scripts/theta_analysis scripts/theta_analysis.c
 * 运行：scripts/theta_analysis [K]   （K 默认 40）
 */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <time.h>

typedef unsigned __int128 u128;

static int KMAX = 40;
static uint64_t pow2v[64];
static u128 pow3v[64];              /* 3^m，m <= 60 时 3^60 < 2^95，用 u128 */
static int bits[64];
static long long nodes = 0, tvecs = 0, danger = 0, viol = 0;
static long long best_gap_x = 0, best_gap_k = 0, zero_class = 0;
static double best_gap = 1e300;
static int best_gap_zero = 0;
static double best_gap_posc = 1e300;
static long long best_gap_posc_k = 0, best_gap_posc_x = 0;
static double best_rel = 0.0;
static long long best_rel_k = 0, best_rel_x = 0;
static unsigned long long minviol_x = 0;
static int minviol_k = 0;
static long long noncyc = 0;        /* 类内 x <= theta 的元素个数（含 x=1） */

/* 逆元 3^{-1} mod 2^{2k} */
static u128 inv3_mod(int k) {
    u128 inv = 1;
    for (int i = 0; i < 8; i++) inv = inv * (2 - (u128)3 * inv);
    return inv;
}

/* r = Phi(w) mod 2^k：从最低位剥离的递推 Phi(2z)=2Phi(z)，Phi(2z+1)=(2Phi(z)-1)/3 */
static uint64_t phi_mod(uint64_t w, int k) {
    int prec = 2 * k + 4;
    u128 MOD = ((u128)1) << prec;
    u128 iv = inv3_mod(prec);
    u128 y = 0;
    for (int i = k - 1; i >= 0; i--) {
        if ((w >> i) & 1) y = ((2 * y + MOD - 1) % MOD) * iv % MOD;
        else y = (2 * y) % MOD;
    }
    return (uint64_t)(y & ((((u128)1) << k) - 1));
}

static void check_first_descent(u128 c, int k, int m) {
    tvecs++;
    u128 d = (u128)pow2v[k] - pow3v[m];       /* > 0 */
    if (d == 0) return;
    /* 类的最小非负残数 r；类内最小正元素 xmin_pos（r = 0 时为 2^k，即该类只含 2^k 的倍数） */
    uint64_t w = 0;
    for (int i = 0; i < k; i++) if (bits[i]) w |= (uint64_t)1 << i;
    uint64_t r = phi_mod(w, k);
    uint64_t xmin_pos = (r == 0) ? (uint64_t)pow2v[k] : r;
    if (r == 0) zero_class++;
    /* xmin_pos <= theta_v  <=>  xmin_pos*d <= c */
    u128 rd = (u128)xmin_pos * d;
    if (rd > c) {
        /* 记录最接近反例的差距 gap = xmin_pos - theta（theta = c/d），
           以及归一化接近度 theta / xmin_pos（违反当且仅当它 >= 1） */
        long double th = (long double)c / (long double)d;
        double gap = (double)xmin_pos - (double)th;
        double rel = (double)(th / (long double)xmin_pos);
        if (gap < best_gap) { best_gap = gap; best_gap_x = (long long)xmin_pos; best_gap_k = k; best_gap_zero = (r == 0); }
        if (c > 0 && gap < best_gap_posc) { best_gap_posc = gap; best_gap_posc_k = k; best_gap_posc_x = (long long)xmin_pos; }
        if (rel > best_rel) { best_rel = rel; best_rel_k = k; best_rel_x = (long long)xmin_pos; }
        return;
    }
    danger++;
    /* 类内满足 x <= theta 的元素个数：x = r + j*2^k <= theta（r = 0 时含退化解 x = 0） */
    u128 num = c - rd;
    u128 den = d * (u128)pow2v[k];
    long long cnt = (long long)(num / den) + 1;
    noncyc += cnt;
    if (xmin_pos >= 2) {
        viol += cnt;
        if (minviol_x == 0 || xmin_pos < minviol_x) { minviol_x = xmin_pos; minviol_k = k; }
    }
}

static void dfs(int k, u128 c, int m) {
    if (k >= 1) {
        nodes++;
        u128 p3 = pow3v[m];
        if (p3 < (u128)pow2v[k]) {          /* 在本节点首降 */
            check_first_descent(c, k, m);
            return;                          /* 一旦首降，后代不再是首降向量，剪枝 */
        }
    }
    if (k == KMAX) return;
    bits[k] = 0;
    dfs(k + 1, c, m);
    bits[k] = 1;
    dfs(k + 1, 3 * c + (u128)pow2v[k], m + 1);
}

int main(int argc, char **argv) {
    if (argc > 1) KMAX = atoi(argv[1]);
    if (KMAX < 1 || KMAX > 60) { fprintf(stderr, "K 越界（1..60）\n"); return 2; }
    pow2v[0] = 1;
    pow3v[0] = 1;
    for (int i = 1; i < 64; i++) pow2v[i] = pow2v[i - 1] * 2;
    for (int i = 1; i < 64; i++) pow3v[i] = pow3v[i - 1] * 3;
    clock_t t0 = clock();
    dfs(0, 0, 0);
    double el = (double)(clock() - t0) / CLOCKS_PER_SEC;
    printf("K = %d：对全部首降向量（即全部 tau(x) <= %d 的 x 的奇偶向量）做反例搜索\n", KMAX, KMAX);
    printf("访问节点数 = %lld；首降向量数（= sum_{k<=K} A(k)）= %lld\n", nodes, tvecs);
    printf("（其中零残数类，即类元素为 2^k 的倍数的向量，共 %lld 个）\n", zero_class);
    printf("其中 theta_v >= x_min（即类内存在 x <= theta_v）的向量数 = %lld\n", danger);
    printf("这些类内满足 x_min <= x <= theta_v 的元素个数（不含 x = 0，含 x = 1）= %lld\n", noncyc);
    printf("破坏 tau = chi 的 x 个数（要求 x >= 2）= %lld\n", viol);
    if (viol) printf("  最小反例 x = %llu（k = %d）\n", minviol_x, minviol_k);
    printf("最接近反例的差距（口径甲：全部首降向量，x_min 取类内最小正元素）：\n");
    printf("   最小 gap = x_min - theta = %.6f，在 k = %lld, x_min = %lld（零残数类？%s）\n",
           best_gap, best_gap_k, best_gap_x, best_gap_zero ? "是" : "否");
    printf("口径乙：只看 c > 0 的向量，最小 gap = %.6f，在 k = %lld, x_min = %lld\n",
           best_gap_posc, best_gap_posc_k, best_gap_posc_x);
    printf("口径丙：归一化接近度 theta / x_min 的最大值 = %.6f（违反当且仅当它不小于 1），在 k = %lld, x_min = %lld\n", best_rel, best_rel_k, best_rel_x);
    printf("耗时 = %.2f 秒\n", el);
    return 0;
}
