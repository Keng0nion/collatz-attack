/*
 * terras_density.c
 * Terras 密度定理 δ[chi >= k] = P[tau >= k] 在有限区间上的表现。
 *   chi(x) = 最小的 k >= 1 使 T^k(x) < x
 *   tau(x) = 最小的 k >= 1 使 3^{m_k} < 2^k（只依赖奇偶向量）
 *   P[tau >= k] 由精确 DP：f[j][m] = 长度 j、含 m 个 1、且从未满足 3^{m_i} < 2^i 的向量概率
 * 输出：k 从 5 到 200 每 5 一行的（实测计数 / X）与 P[tau >= k] 的对比。
 * 编译：cc -O3 -o scripts/terras_density scripts/terras_density.c
 * 运行：scripts/terras_density [X]   （X 默认 1<<26）
 */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <time.h>

#define KCAP 600
#define DPMAX 260

int main(int argc, char **argv) {
    uint64_t X = (argc > 1) ? (uint64_t)strtoull(argv[1], NULL, 10) : (1ULL << 26);
    printf("区间：1 <= x <= %llu\n", (unsigned long long)X);
    static uint64_t hist[KCAP + 2];
    clock_t t0 = clock();
    for (uint64_t x = 2; x <= X; x++) {          /* x = 1 的 chi 为无穷，计入另册 */
        uint64_t v = x;
        int k = 0, chi = 0;
        while (k <= KCAP) {
            v = (v & 1ULL) ? (3 * v + 1) >> 1 : v >> 1;
            k++;
            if (v < x) { chi = k; break; }
        }
        if (chi == 0) chi = KCAP + 1;
        if (chi <= KCAP) hist[chi]++;
    }
    printf("停时直方图耗时 %.2f 秒（x = 1 未计入）\n", (double)(clock() - t0) / CLOCKS_PER_SEC);

    /* P[tau >= k] 精确 DP（用 long double 提高精度） */
    static long double f[DPMAX + 2][DPMAX + 2];
    static long double pge[DPMAX + 2];
    for (int i = 0; i <= DPMAX + 1; i++)
        for (int j = 0; j <= DPMAX + 1; j++) f[i][j] = 0.0L;
    f[0][0] = 1.0L;
    pge[1] = 1.0L;
    for (int j = 1; j <= DPMAX; j++) {
        for (int m = 0; m <= j; m++) {
            long double p = f[j - 1][m];
            if (p == 0.0L) continue;
            /* 追加 0：长度 j、m 不变，条件 3^m >= 2^j 即 m*ln3 >= j*ln2 */
            if ((long double)m * 1.0986122886681098L >= (long double)j * 0.6931471805599453L)
                f[j][m] += p / 2.0L;
            /* 追加 1：长度 j、m+1 个 1，条件 3^{m+1} >= 2^j */
            if ((long double)(m + 1) * 1.0986122886681098L >= (long double)j * 0.6931471805599453L)
                f[j][m + 1] += p / 2.0L;
        }
        long double s = 0.0L;
        for (int m = 0; m <= j; m++) s += f[j][m];
        pge[j + 1] = s;                 /* P[tau >= j+1] = 前 j 步均未下降的概率 */
    }
    printf("\nTerras 密度定理的有限区间表现：k, 实测 #(chi>=k)/X, P[tau>=k], 比值\n");
    for (int k = 5; k <= 200; k += 5) {
        uint64_t c = 0;
        for (int j = k; j <= KCAP; j++) c += hist[j];
        long double emp = (long double)c / (long double)X;
        printf("k=%3d  count=%-10llu  emp=%.8Lf  P=%.8Lf  ratio=%.4Lf\n",
               k, (unsigned long long)c, emp, pge[k], pge[k] > 0.0L ? emp / pge[k] : 0.0L);
    }
    /* 逐 k（不只每 5 一档）的偏离上确界 */
    int kmax = 240;
    if (kmax > KCAP) kmax = KCAP;
    long double sup155 = 0.0L, sup200 = 0.0L, supall = 0.0L;
    int a155 = 0, a200 = 0, aall = 0;
    for (int k = 1; k <= kmax; k++) {
        uint64_t c = 0;
        for (int j = k; j <= KCAP; j++) c += hist[j];
        long double emp = (long double)c / (long double)X;
        if (pge[k] <= 0.0L) continue;
        long double dev = emp / pge[k] - 1.0L;
        if (dev < 0.0L) dev = -dev;
        if (k <= 155 && dev > sup155) { sup155 = dev; a155 = k; }
        if (k <= 200 && dev > sup200) { sup200 = dev; a200 = k; }
        if (dev > supall) { supall = dev; aall = k; }
    }
    printf("\n逐 k（k = 1..%d，不只每 5 一档）的偏离上确界：\n", kmax);
    printf("  k <= 155：|比值 - 1| 的上确界 = %.4Lf%%（在 k = %d）\n", 100.0L * sup155, a155);
    printf("  k <= 200：|比值 - 1| 的上确界 = %.4Lf%%（在 k = %d）\n", 100.0L * sup200, a200);
    printf("  k <= %d：|比值 - 1| 的上确界 = %.4Lf%%（在 k = %d）\n", kmax, 100.0L * supall, aall);
    printf("\n（P[tau >= k] 由精确 DP 得到；比值在 k 远小于 log2(X) 时约为 1，在 k 接近 log2(X) 时开始偏离）\n");
    return 0;
}
