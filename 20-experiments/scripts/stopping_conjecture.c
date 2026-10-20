/*
 * stopping_conjecture.c
 * Terras 系数停时猜想 tau(x) = chi(x)（x >= 2）在区间 1..X 上的检验。
 *   chi(x) = 最小的 k >= 1 使 T^k(x) < x（真停时，用轨道实际数值判定）
 *   tau(x) = 最小的 k >= 1 使 3^{m_k} < 2^k（m_k 为前 k 步中的奇步数，只依赖奇偶向量）
 * 编译：cc -O3 -o scripts/stopping_conjecture scripts/stopping_conjecture.c
 * 运行：scripts/stopping_conjecture [X]   （X 默认 1<<26）
 */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <time.h>

#define KCAP 400

int main(int argc, char **argv) {
    uint64_t X = (argc > 1) ? (uint64_t)strtoull(argv[1], NULL, 10) : (1ULL << 26);
    printf("区间：1 <= x <= %llu\n", (unsigned long long)X);
    uint64_t hist[KCAP + 1];
    for (int i = 0; i <= KCAP; i++) hist[i] = 0;
    uint64_t n_mismatch = 0, first_mismatch = 0;
    uint64_t maxchi = 0, argmax = 0, ninf = 0, novf = 0;
    clock_t t0 = clock();
    for (uint64_t x = 1; x <= X; x++) {
        uint64_t v = x;
        int k = 0, chi = 0, tau = 0;
        double ratio = 1.0;
        while (k <= KCAP) {
            int b = (int)(v & 1ULL);
            v = b ? (3 * v + 1) >> 1 : v >> 1;
            k++;
            if (b) ratio = ratio * 3.0 / 2.0; else ratio = ratio / 2.0;
            if (!chi && v < x) chi = k;
            if (!tau && ratio < 1.0) tau = k;
            if (chi && tau) break;
            if (v > (1ULL << 61)) { novf++; break; }
        }
        if (chi == 0) { ninf++; continue; }
        if (chi > KCAP) chi = KCAP;
        hist[chi]++;
        if ((uint64_t)chi > maxchi) { maxchi = (uint64_t)chi; argmax = x; }
        if (tau != chi) {
            n_mismatch++;
            if (!first_mismatch) first_mismatch = x;
        }
    }
    double el = (double)(clock() - t0) / CLOCKS_PER_SEC;
    printf("耗时 %.2f 秒\n", el);
    printf("chi 无穷（永不降到自身之下）的 x 个数 = %llu（预期 1，即 x=1）\n", (unsigned long long)ninf);
    printf("chi 的最大值 = %llu，首次出现在 x = %llu\n", (unsigned long long)maxchi, (unsigned long long)argmax);
    printf("tau != chi 的 x 个数 = %llu\n", (unsigned long long)n_mismatch);
    if (n_mismatch) {
        printf("  最小不符的 x = %llu\n", (unsigned long long)first_mismatch);
        printf("  （x=1 是已知例外：tau=2, chi=无穷；猜想只声明 x >= 2）\n");
        printf("  落在 x >= 2 的不符个数 = %llu\n",
               (unsigned long long)(first_mismatch == 1 ? n_mismatch - 1 : n_mismatch));
    } else {
        printf("  x >= 2 全部相符\n");
    }
    printf("溢出防护触发次数 = %llu（预期 0）\n", (unsigned long long)novf);
    printf("chi 直方图（前 40 个非零项）：");
    int printed = 0;
    for (int j = 1; j <= KCAP && printed < 40; j++) {
        if (hist[j]) { printf(" %d:%llu", j, (unsigned long long)hist[j]); printed++; }
    }
    printf("\n");
    return 0;
}
