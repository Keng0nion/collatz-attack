/*
 * bl_permutation.c
 * Phi 模 2^n 的置换循环结构（Bernstein 与 Lagarias 共轭映射）。
 * Phi^{-1}(x) mod 2^n = sum_{i<n} (T^i(x) mod 2) 2^i；Phi 与 Phi^{-1} 循环结构相同。
 * 对奇残数（(Z/2^n Z)^*）做循环分解，输出每行的周期 2^j 循环个数 counts[]。
 * 编译：cc -O3 -o scripts/bl_permutation scripts/bl_permutation.c
 * 运行：scripts/bl_permutation [N]   （N 默认 26，允许 1..30）
 */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <time.h>

static int NMAX = 26;
#define VISBYTES ((1u << 26) + 16)     /* 覆盖 n <= 30 的奇残数标记 */

static unsigned char vis[VISBYTES];

static uint64_t phiinv(uint64_t x, int n) {
    uint64_t y = 0;
    for (int i = 0; i < n; i++) {
        int b = (int)(x & 1ULL);
        y |= ((uint64_t)b) << i;
        x = b ? (3 * x + 1) >> 1 : x >> 1;
    }
    return y;
}

static int lg2(int v) {
    int j = 0;
    while (j + 1 < 31 && (1 << (j + 1)) <= v) j++;
    return j;
}

int main(int argc, char **argv) {
    if (argc > 1) NMAX = atoi(argv[1]);
    if (NMAX < 1 || NMAX > 30) return 2;
    printf("# n=  counts[j] (j=0..n)  order  longcyc  reps\n");
    int bad_pow = 0, bad_ord = 0, bad_long = 0;
    for (int n = 1; n <= NMAX; n++) {
        uint64_t half = (uint64_t)1 << n;
        uint64_t nodd = half >> 1;
        for (size_t i = 0; i < (size_t)((nodd >> 3) + 1); i++) vis[i] = 0;
        int cnt[40];
        for (int i = 0; i < 40; i++) cnt[i] = 0;
        uint64_t total = 0;
        int maxlen = 0;
        uint64_t r1 = 0, r2 = 0, r3 = 0;
        int nrep = 0;
        clock_t t0 = clock();
        for (uint64_t x = 1; x < half; x += 2) {
            size_t idx = (size_t)(x >> 1);
            if (vis[idx >> 3] & (unsigned char)(1u << (idx & 7))) continue;
            int len = 0;
            uint64_t y = x;
            while (1) {
                size_t jj = (size_t)(y >> 1);
                if (vis[jj >> 3] & (unsigned char)(1u << (jj & 7))) break;
                vis[jj >> 3] |= (unsigned char)(1u << (jj & 7));
                len++;
                y = phiinv(y, n);
            }
            total += (uint64_t)len;
            int j = lg2(len);
            if ((1 << j) != len) bad_pow++;
            if (j < 40) cnt[j]++;
            if (len > maxlen) { maxlen = len; nrep = 0; r1 = r2 = r3 = 0; }
            if (len == maxlen) {
                if (nrep == 0) r1 = x;
                else if (nrep == 1) r2 = x;
                else if (nrep == 2) r3 = x;
                nrep++;
            }
        }
        double el = (double)(clock() - t0) / CLOCKS_PER_SEC;
        printf("n=%-2d ", n);
        for (int j = 0; j <= n && j < 40; j++) printf("%d ", cnt[j]);
        printf(" order=%d", maxlen);
        if (n >= 6) {
            int want = 1 << (n - 4);
            printf(" want=%d %s", want, maxlen == want ? "ok" : "NO");
            if (maxlen != want) bad_ord++;
            int lc = cnt[n - 4];
            printf(" longcnt=%d %s", lc, lc == 3 ? "ok" : "NO");
            if (lc != 3) bad_long++;
        } else {
            printf(" want=n/a longcnt=n/a");
        }
        printf(" oddtot=%llu (expect %llu) reps=%llu,%llu,%llu t=%.2fs\n",
               (unsigned long long)total, (unsigned long long)nodd,
               (unsigned long long)r1, (unsigned long long)r2, (unsigned long long)r3, el);
    }
    printf("# bad_pow=%d bad_order=%d bad_long=%d\n", bad_pow, bad_ord, bad_long);
    return 0;
}
