/* stoptime_dist.c —— 精确计算 1 至 N 的 Collatz 停时分布（三套量）
 *
 * 计算：
 *   tot[n]   总停时（OEIS A006577）：标准映射（奇走 3n+1，偶走 n/2）首次到达 1 的步数。
 *   cs[n]    Terras 停时（标准步）：首次使轨迹值严格小于 n 的步数。
 *   ca[n]    Terras 停时（加速步）：加速映射 T(n)=n/2（偶）、(3n+1)/2（奇）
 *            下首次使轨迹值严格小于 n 的加速步数。
 *
 * 记忆化：cs 与 tot 用同一趟前向扫描取得（轨迹首次跌破 n 时查表加上 tot[m]，m<n 已算过）。
 *
 * 输出（写到 argv[2] 目录）：
 *   stoptime_dist_summary.txt     汇总统计与耗时
 *   stoptime_tot_hist.csv         t,count
 *   stoptime_chistd_hist.csv      k,count
 *   stoptime_chiacc_hist.csv      k,count
 *   stoptime_tot_band2d.csv       band,t,count   （band = floor(log2 n)）
 *   stoptime_chiacc_band2d.csv    band,k,count
 *   stoptime_records.txt          n,tot（总停时纪录保持者，按 n 递增）
 *
 * 编译：cc -O3 -o stoptime_dist stoptime_dist.c
 * 用法：./stoptime_dist <N> <outdir> [dump上限] [dump文件]
 *        给出 dump 上限与 dump 文件时，额外把 n <= dump上限 的逐点数值写入该文件。
 */
#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <math.h>
#include <time.h>

#define NB 64          /* floor(log2 n) 的分带数上限 */
#define VMAX 8192      /* 直方图取值上限（实际最大停时远小于此） */
#define CAPER 1000000u /* 单条轨迹步数安全上限：触发即报错退出（可能意味着反例或程序错误） */

static double now_sec(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (double)ts.tv_sec + 1e-9 * (double)ts.tv_nsec;
}

static int band_of(uint64_t n) {
    int b = 0;
    while (n >>= 1) b++;
    return b;
}

int main(int argc, char **argv) {
    uint64_t N = (argc > 1) ? strtoull(argv[1], NULL, 10) : (1ull << 24);
    const char *out = (argc > 2) ? argv[2] : ".";
    char path[4096];

    if (N < 2) { fprintf(stderr, "N 至少为 2\n"); return 1; }

    uint16_t *tot = (uint16_t *)malloc(((size_t)N + 1) * sizeof(uint16_t));
    uint16_t *cs  = (uint16_t *)malloc(((size_t)N + 1) * sizeof(uint16_t));
    uint16_t *ca  = (uint16_t *)malloc(((size_t)N + 1) * sizeof(uint16_t));
    uint64_t *hist_tot = (uint64_t *)calloc(VMAX, sizeof(uint64_t));
    uint64_t *hist_cs  = (uint64_t *)calloc(VMAX, sizeof(uint64_t));
    uint64_t *hist_ca  = (uint64_t *)calloc(VMAX, sizeof(uint64_t));
    uint64_t *b2_tot   = (uint64_t *)calloc((size_t)NB * VMAX, sizeof(uint64_t));
    uint64_t *b2_ca    = (uint64_t *)calloc((size_t)NB * VMAX, sizeof(uint64_t));
    if (!tot || !cs || !ca || !hist_tot || !hist_cs || !hist_ca || !b2_tot || !b2_ca) {
        fprintf(stderr, "内存分配失败\n"); return 1;
    }

    snprintf(path, sizeof path, "%s/stoptime_records.txt", out);
    FILE *frec = fopen(path, "w");
    if (!frec) { fprintf(stderr, "无法写 %s\n", path); return 1; }
    fprintf(frec, "n,tot\n1,0\n");

    double t0 = now_sec();

    tot[1] = 0; cs[1] = 0; ca[1] = 0;
    uint32_t max_tot = 0, argmax_tot = 1;
    uint32_t max_cs = 0, argmax_cs = 2;
    double s_tot = 0.0, q_tot = 0.0, s_cs = 0.0, q_cs = 0.0;

    for (uint64_t n = 2; n <= N; n++) {
        uint64_t m = n;
        uint32_t c = 0;
        while (m >= n) {
            if (m & 1ull) m = 3ull * m + 1ull; else m >>= 1;
            c++;
            if (c > CAPER) {
                fprintf(stderr, "安全上限触发：n=%llu 连续 %u 步未跌破自身（可能反例，或程序错误）\n",
                        (unsigned long long)n, c);
                return 2;
            }
        }
        uint32_t tv = c + (uint32_t)tot[m];
        tot[n] = (uint16_t)tv;
        cs[n]  = (uint16_t)c;
        if (tv > max_tot) { max_tot = tv; argmax_tot = (uint32_t)n; fprintf(frec, "%llu,%u\n", (unsigned long long)n, tv); }
        if (c > max_cs) { max_cs = c; argmax_cs = (uint32_t)n; }
        s_tot += (double)tv; q_tot += (double)tv * (double)tv;
        s_cs  += (double)c;  q_cs  += (double)c * (double)c;
    }

    double t1 = now_sec();

    uint32_t max_ca = 0, argmax_ca = 0;
    double s_ca = 0.0, q_ca = 0.0;
    for (uint64_t n = 2; n <= N; n++) {
        uint64_t m = n;
        uint32_t c = 0;
        while (m >= n) {
            if (m & 1ull) m = (3ull * m + 1ull) >> 1; else m >>= 1;
            c++;
            if (c > CAPER) { fprintf(stderr, "加速步安全上限触发：n=%llu\n", (unsigned long long)n); return 2; }
        }
        ca[n] = (uint16_t)c;
        if (c > max_ca) { max_ca = c; argmax_ca = (uint32_t)n; }
        s_ca += (double)c; q_ca += (double)c * (double)c;
    }

    double t2 = now_sec();

    /* 直方图与分带二维直方图 */
    for (uint64_t n = 1; n <= N; n++) {
        if (tot[n] >= VMAX || cs[n] >= VMAX || ca[n] >= VMAX) { fprintf(stderr, "取值超出直方图上限\n"); return 1; }
        hist_tot[tot[n]]++; hist_cs[cs[n]]++; hist_ca[ca[n]]++;
        int b = band_of(n);
        if (b >= NB) { fprintf(stderr, "分带超出上限\n"); return 1; }
        b2_tot[(size_t)b * VMAX + tot[n]]++;
        b2_ca[(size_t)b * VMAX + ca[n]]++;
    }

    snprintf(path, sizeof path, "%s/stoptime_tot_hist.csv", out);
    FILE *f = fopen(path, "w"); fprintf(f, "t,count\n");
    for (int v = 0; v < VMAX; v++) if (hist_tot[v]) fprintf(f, "%d,%llu\n", v, (unsigned long long)hist_tot[v]);
    fclose(f);

    snprintf(path, sizeof path, "%s/stoptime_chistd_hist.csv", out);
    f = fopen(path, "w"); fprintf(f, "k,count\n");
    for (int v = 0; v < VMAX; v++) if (hist_cs[v]) fprintf(f, "%d,%llu\n", v, (unsigned long long)hist_cs[v]);
    fclose(f);

    snprintf(path, sizeof path, "%s/stoptime_chiacc_hist.csv", out);
    f = fopen(path, "w"); fprintf(f, "k,count\n");
    for (int v = 0; v < VMAX; v++) if (hist_ca[v]) fprintf(f, "%d,%llu\n", v, (unsigned long long)hist_ca[v]);
    fclose(f);

    snprintf(path, sizeof path, "%s/stoptime_tot_band2d.csv", out);
    f = fopen(path, "w"); fprintf(f, "band,t,count\n");
    for (int b = 0; b < NB; b++) for (int v = 0; v < VMAX; v++) {
        uint64_t c = b2_tot[(size_t)b * VMAX + v];
        if (c) fprintf(f, "%d,%d,%llu\n", b, v, (unsigned long long)c);
    }
    fclose(f);

    snprintf(path, sizeof path, "%s/stoptime_chiacc_band2d.csv", out);
    f = fopen(path, "w"); fprintf(f, "band,k,count\n");
    for (int b = 0; b < NB; b++) for (int v = 0; v < VMAX; v++) {
        uint64_t c = b2_ca[(size_t)b * VMAX + v];
        if (c) fprintf(f, "%d,%d,%llu\n", b, v, (unsigned long long)c);
    }
    fclose(f);

    /* 可选：逐点转储 n <= dumpN 的数值，供外部逐点核对 */
    if (argc > 4) {
        uint64_t dumpN = strtoull(argv[3], NULL, 10);
        if (dumpN > N) dumpN = N;
        FILE *fd = fopen(argv[4], "w");
        if (!fd) { fprintf(stderr, "无法写 %s\n", argv[4]); return 1; }
        fprintf(fd, "n,tot,chi_std,chi_acc\n");
        for (uint64_t n = 1; n <= dumpN; n++)
            fprintf(fd, "%llu,%u,%u,%u\n", (unsigned long long)n, tot[n], cs[n], ca[n]);
        fclose(fd);
    }

    double nn = (double)(N - 1); /* n = 2 至 N 的个数 */    double m_tot = s_tot / nn, v_tot = q_tot / nn - m_tot * m_tot;
    double m_cs  = s_cs  / nn, v_cs  = q_cs  / nn - m_cs * m_cs;
    double m_ca  = s_ca  / nn, v_ca  = q_ca  / nn - m_ca * m_ca;

    snprintf(path, sizeof path, "%s/stoptime_dist_summary.txt", out);
    f = fopen(path, "w");
    fprintf(f, "stoptime_dist summary\n");
    fprintf(f, "N=%llu  (n = 1 至 %llu，含端点)\n", (unsigned long long)N, (unsigned long long)N);
    fprintf(f, "全部 n 均到达 1：是（tot[n] 全部有限且已计入直方图）\n");
    fprintf(f, "count_n_ge2=%llu\n", (unsigned long long)(N - 1));
    fprintf(f, "tot  mean=%.10f  sd=%.10f  max=%u  argmax=%u\n", m_tot, (v_tot > 0 ? sqrt(v_tot) : 0.0), max_tot, argmax_tot);
    fprintf(f, "cs   mean=%.10f  sd=%.10f  max=%u  argmax=%u\n", m_cs, (v_cs > 0 ? sqrt(v_cs) : 0.0), max_cs, argmax_cs);
    fprintf(f, "ca   mean=%.10f  sd=%.10f  max=%u  argmax=%u\n", m_ca, (v_ca > 0 ? sqrt(v_ca) : 0.0), max_ca, argmax_ca);
    fprintf(f, "chi_std/chi_acc 均值比 = %.10f\n", m_cs / m_ca);
    fprintf(f, "time_seconds_totpass=%.6f\n", t1 - t0);
    fprintf(f, "time_seconds_accpass=%.6f\n", t2 - t1);
    fprintf(f, "time_seconds_total=%.6f\n", t2 - t0);
    fclose(f);
    fclose(frec);

    printf("N=%llu\n", (unsigned long long)N);
    printf("tot: mean=%.6f sd=%.6f max=%u at n=%u\n", m_tot, sqrt(v_tot), max_tot, argmax_tot);
    printf("cs : mean=%.6f sd=%.6f\n", m_cs, sqrt(v_cs));
    printf("ca : mean=%.6f sd=%.6f max=%u at n=%u\n", m_ca, sqrt(v_ca), max_ca, argmax_ca);
    printf("ratio cs/ca = %.6f\n", m_cs / m_ca);
    printf("time: tot+cs pass %.3f s, acc pass %.3f s, total %.3f s\n", t1 - t0, t2 - t1, t2 - t0);

    free(tot); free(cs); free(ca);
    free(hist_tot); free(hist_cs); free(hist_ca); free(b2_tot); free(b2_ca);
    return 0;
}
