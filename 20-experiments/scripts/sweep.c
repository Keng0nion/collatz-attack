/*
 * sweep.c —— 科拉茨迭代全量扫描：验证 n <= N 的「总停时」
 *
 * 计数约定与 OEIS A006577 完全一致：
 *   映射 C(n) = n/2 (n 偶)，C(n) = 3n+1 (n 奇)；
 *   总停时 len[n] = 到达 1 所需的 C 步数（每个折半与每个 3n+1 各计 1 步），len[1] = 0。
 *
 * 算法（记忆化，按 n 递增填表）：
 *   n 偶：len[n] = len[n/2] + 1；
 *   n 奇：从 n 沿轨迹步进，直到当前值 x < n，然后 len[n] = 步数 + len[x]。
 *   由于 x < n，len[x] 已在此前的迭代中填好，于是每个 len[n] 都对应一条
 *   显式的、下降到更小已核验值的有限步轨迹：这是对 n 的归纳，不是概率断言。
 *
 * 安全边界：所有循环都有显式步数上限；输入上限有硬上界 MAX_LIMIT；
 * 3x+1 之前做溢出检查；表下标只使用已填区域。
 *
 * 用法： ./sweep N records.tsv lens.tsv
 *   N 为十进制上限，16 <= N <= 2^29 = 536870912。
 */

#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <time.h>

#define MAX_LIMIT   ((uint64_t)1 << 29)
#define STEP_CAP    10000000LL
#define DIRECT_CAP  100000000LL

static uint16_t *tab = NULL;
static uint64_t n_limit = 0L;

static const uint64_t U64_MAX_3 = (UINT64_MAX - 1ULL) / 3ULL;

static double now_s(void)
{
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (double)ts.tv_sec + 1e-9 * (double)ts.tv_nsec;
}

/* 从 start 沿 C 映射步进，直到当前值 < floor（floor <= start）。
   成功：返回 0，*steps_out = 步数，*land_out = 落点（< floor）。
   异常：返回 1（超过 STEP_CAP），2（数值溢出，不应发生）。 */
static int walk_below(uint64_t start, uint64_t floor, long long *steps_out, uint64_t *land_out)
{
    uint64_t x = start;
    long long c = 0;
    while (x >= floor) {
        if (c >= STEP_CAP) return 1;
        if (x & 1ULL) {
            if (x > U64_MAX_3) return 2;
            x = 3ULL * x + 1ULL;
        } else {
            x >>= 1;
        }
        c++;
    }
    *steps_out = c;
    *land_out = x;
    return 0;
}

/* 教科书式直接模拟：只用 C 映射逐步走到 1，不查表、不加速。
   成功：返回 0，*steps_out = 步数，*peak_out = 途中最大值。
   超过 DIRECT_CAP：返回 1；溢出：返回 2。 */
static int direct_steps(uint64_t n, long long *steps_out, uint64_t *peak_out)
{
    uint64_t x = n;
    uint64_t pk = n;
    long long c = 0;
    while (x != 1ULL) {
        if (c >= DIRECT_CAP) return 1;
        if (x & 1ULL) {
            if (x > U64_MAX_3) return 2;
            x = 3ULL * x + 1ULL;
        } else {
            x >>= 1;
        }
        c++;
        if (x > pk) pk = x;
    }
    *steps_out = c;
    *peak_out = pk;
    return 0;
}

/* Terras 停时 chi：加速映射 T(n) = n/2 (偶)，(3n+1)/2 (奇)，
   chi(n) = 最小 k >= 1 使 T^k(n) < n。用于对照文献（n <= 250000 的最大值）。 */
static int chi_steps(uint64_t n, long long *k_out)
{
    uint64_t x = n;
    long long k = 0;
    while (x >= n) {
        if (k >= STEP_CAP) return 1;
        if (x & 1ULL) {
            if (x > U64_MAX_3) return 2;
            x = (3ULL * x + 1ULL) >> 1;
        } else {
            x >>= 1;
        }
        k++;
    }
    *k_out = k;
    return 0;
}

/* 严格十进制解析：只接受数字，结果落在 [16, MAX_LIMIT]。 */
static int parse_limit(const char *s, uint64_t *out)
{
    uint64_t v = 0ULL;
    if (s == NULL || *s == '\0') return 1;
    for (const char *p = s; *p != '\0'; p++) {
        if (*p < '0' || *p > '9') return 1;
        unsigned d = (unsigned)(*p - '0');
        if (v > (MAX_LIMIT - (uint64_t)d) / 10ULL) return 1;
        v = v * 10ULL + (uint64_t)d;
    }
    if (v < 16ULL || v > MAX_LIMIT) return 1;
    *out = v;
    return 0;
}

int main(int argc, char **argv)
{
    if (argc < 2 || argc > 4) {
        fprintf(stderr, "usage: %s N [records.tsv] [lens.tsv]   (16 <= N <= 2^29)\n", argv[0]);
        return 2;
    }
    if (parse_limit(argv[1], &n_limit) != 0) {
        fprintf(stderr, "bad limit: must be decimal in [16, 2^29]\n");
        return 2;
    }
    const char *rec_path = (argc > 2) ? argv[2] : NULL;
    const char *lens_path = (argc > 3) ? argv[3] : NULL;

    const double t_start = now_s();

    printf("== Collatz full sweep (total stopping time, OEIS A006577 convention) ==\n");
    printf("command:");
    for (int i = 0; i < argc; i++) printf(" %s", argv[i]);
    printf("\nlimit N = %llu\n", (unsigned long long)n_limit);
    printf("map: n -> n/2 if even, 3n+1 if odd; every halving and tripling step counts\n");

    /* ---------- 分配 ---------- */
    double t0 = now_s();
    const size_t elems = (size_t)(n_limit + 1ULL);
    tab = (uint16_t *)calloc(elems, sizeof(uint16_t));
    if (tab == NULL) { fprintf(stderr, "calloc failed (%zu entries)\n", elems); return 3; }
    const double t_alloc = now_s() - t0;
    printf("table: %zu uint16 entries = %.1f MiB\n", elems, (double)elems * 2.0 / 1048576.0);

    /* ---------- 填表 ---------- */
    t0 = now_s();
    tab[1] = 0;
    for (uint64_t n = 2ULL; n <= n_limit; n++) {
        if ((n & 1ULL) == 0ULL) {
            tab[n] = (uint16_t)(tab[n >> 1] + 1);
            continue;
        }
        long long c = 0;
        uint64_t land = 0;
        const int r = walk_below(n, n, &c, &land);
        if (r != 0) {
            fprintf(stderr, "ABNORMAL: walk from n=%llu did not descend below n (r=%d)\n", (unsigned long long)n, r);
            return 4;
        }
        tab[n] = (uint16_t)(c + (long long)tab[land]);
    }
    const double t_fill = now_s() - t0;

    /* ---------- (a) 全部 n 有限（表无空洞） ---------- */
    t0 = now_s();
    uint64_t unknown = 0ULL, first_unknown = 0ULL;
    for (uint64_t n = 2ULL; n <= n_limit; n++) {
        if (tab[n] == 0) {
            if (unknown == 0ULL) first_unknown = n;
            unknown++;
        }
    }
    const double t_unknown = now_s() - t0;
    printf("\n(a) every n in [1, %llu] reaches 1:\n", (unsigned long long)n_limit);
    printf("    finite total stopping time: %llu of %llu entries\n", (unsigned long long)(n_limit - unknown), (unsigned long long)n_limit);
    if (unknown != 0ULL) printf("    entries still unknown after fill: %llu (first at n = %llu)\n", (unsigned long long)unknown, (unsigned long long)first_unknown);
    else printf("    entries still unknown after fill: 0\n");
    if (unknown != 0ULL) { printf("RESULT: FAIL\n"); return 5; }

    /* ---------- (b)(c) 纪录扫描 ---------- */
    t0 = now_s();
    FILE *fr = NULL;
    if (rec_path != NULL) {
        fr = fopen(rec_path, "w");
        if (fr == NULL) { fprintf(stderr, "cannot write %s\n", rec_path); return 3; }
        fprintf(fr, "# index\tn\ttotal_stopping_time\n");
    }
    long long best = -1;
    uint64_t nrec = 0ULL, argmax = 1ULL;
    printf("\n(c) record holders (strict records of total stopping time, from n = 1):\n");
    printf("    %-6s %-20s %-8s\n", "idx", "n", "steps");
    for (uint64_t n = 1ULL; n <= n_limit; n++) {
        const long long v = (long long)tab[n];
        if (v > best) {
            nrec++;
            printf("    %-6llu %-20llu %-8lld\n", (unsigned long long)nrec, (unsigned long long)n, v);
            if (fr != NULL) fprintf(fr, "%llu\t%llu\t%lld\n", (unsigned long long)nrec, (unsigned long long)n, v);
            best = v;
            argmax = n;
        }
    }
    if (fr != NULL) { fclose(fr); fr = NULL; }
    const double t_rec = now_s() - t0;
    printf("    record holders in [1, %llu]: %llu\n", (unsigned long long)n_limit, (unsigned long long)nrec);
    printf("\n(b) max total stopping time in [1, %llu]: %lld, attained at n = %llu\n", (unsigned long long)n_limit, best, (unsigned long long)argmax);

    /* ---------- 校验 A：小范围逐条直接模拟 ---------- */
    t0 = now_s();
    const uint64_t va_max = (n_limit < 1000000ULL) ? n_limit : 1000000ULL;
    uint64_t va_bad = 0ULL, va_peak_max = 0ULL;
    long long va_steps_max = 0;
    for (uint64_t n = 1ULL; n <= va_max; n++) {
        long long d = -1;
        uint64_t pk = 0ULL;
        const int r = direct_steps(n, &d, &pk);
        if (r != 0 || d != (long long)tab[n]) {
            va_bad++;
            if (va_bad <= 5ULL) printf("    MISMATCH n=%llu table=%u direct=%lld r=%d\n", (unsigned long long)n, (unsigned)tab[n], d, r);
        }
        if (pk > va_peak_max) va_peak_max = pk;
        if (d > va_steps_max) va_steps_max = d;
    }
    const double t_va = now_s() - t0;
    printf("\n[verify A] direct simulation for every n in [1, %llu]: %s (checked %llu, max steps %lld, peak %llu)\n", (unsigned long long)va_max, (va_bad == 0ULL) ? "OK" : "FAIL", (unsigned long long)va_max, va_steps_max, (unsigned long long)va_peak_max);
    if (va_bad != 0ULL) { printf("RESULT: FAIL\n"); return 5; }

    /* ---------- 校验 B：全部纪录点直接模拟 ---------- */
    t0 = now_s();
    uint64_t vb_bad = 0ULL, vb_checked = 0ULL;
    best = -1;
    for (uint64_t n = 1ULL; n <= n_limit; n++) {
        const long long v = (long long)tab[n];
        if (v > best) {
            long long d = -1;
            uint64_t pk = 0ULL;
            const int r = direct_steps(n, &d, &pk);
            vb_checked++;
            if (r != 0 || d != v) {
                vb_bad++;
                if (vb_bad <= 5ULL) printf("    MISMATCH record n=%llu table=%u direct=%lld r=%d\n", (unsigned long long)n, (unsigned)tab[n], d, r);
            }
            best = v;
        }
    }
    const double t_vb = now_s() - t0;
    printf("[verify B] direct simulation for all record holders: %s (checked %llu)\n", (vb_bad == 0ULL) ? "OK" : "FAIL", (unsigned long long)vb_checked);
    if (vb_bad != 0ULL) { printf("RESULT: FAIL\n"); return 5; }

    /* ---------- 校验 C：随机抽样直接模拟 ---------- */
    t0 = now_s();
    uint64_t rng = 0x9E3779B97F4A7C15ULL ^ n_limit;
    const uint64_t n_sample = 200000ULL;
    uint64_t vc_bad = 0ULL, vc_peak_max = 0ULL;
    long long vc_steps_max = 0;
    for (uint64_t i = 0ULL; i < n_sample; i++) {
        rng ^= rng << 13;
        rng ^= rng >> 7;
        rng ^= rng << 17;
        const uint64_t n = 1ULL + (rng % n_limit);
        long long d = -1;
        uint64_t pk = 0ULL;
        const int r = direct_steps(n, &d, &pk);
        if (r != 0 || d != (long long)tab[n]) {
            vc_bad++;
            if (vc_bad <= 5ULL) printf("    MISMATCH sample n=%llu table=%u direct=%lld r=%d\n", (unsigned long long)n, (unsigned)tab[n], d, r);
        }
        if (pk > vc_peak_max) vc_peak_max = pk;
        if (d > vc_steps_max) vc_steps_max = d;
    }
    const double t_vc = now_s() - t0;
    printf("[verify C] direct simulation for %llu xorshift64 samples in [1, %llu]: %s (max steps %lld, peak %llu)\n", (unsigned long long)n_sample, (unsigned long long)n_limit, (vc_bad == 0ULL) ? "OK" : "FAIL", vc_steps_max, (unsigned long long)vc_peak_max);
    if (vc_bad != 0ULL) { printf("RESULT: FAIL\n"); return 5; }

    /* ---------- 校验 D：偶数的表内递推一致性（全表） ---------- */
    t0 = now_s();
    uint64_t vd_bad = 0ULL, vd_cnt = 0ULL;
    for (uint64_t n = 2ULL; n <= n_limit; n += 2ULL) {
        if (tab[n] != (uint16_t)(tab[n >> 1] + 1)) {
            vd_bad++;
            if (vd_bad <= 5ULL) printf("    MISMATCH even n=%llu\n", (unsigned long long)n);
        }
        vd_cnt++;
    }
    const double t_vd = now_s() - t0;
    printf("[verify D] len[n] == len[n/2] + 1 for every even n <= N: %s (checked %llu)\n", (vd_bad == 0ULL) ? "OK" : "FAIL", (unsigned long long)vd_cnt);
    if (vd_bad != 0ULL) { printf("RESULT: FAIL\n"); return 5; }

    /* ---------- 校验 E：Terras 停时 chi 的最大值（对照文献范围 n <= 250000） ---------- */
    t0 = now_s();
    const uint64_t chi_hi = (n_limit < 250000ULL) ? n_limit : 250000ULL;
    long long chi_best = 0;
    uint64_t chi_arg = 0ULL, chi_ties = 0ULL;
    int chi_bad = 0;
    for (uint64_t n = 3ULL; n <= chi_hi; n++) {
        long long k = -1;
        const int r = chi_steps(n, &k);
        if (r != 0) { chi_bad++; continue; }
        if (k > chi_best) { chi_best = k; chi_arg = n; chi_ties = 1ULL; }
        else if (k == chi_best) chi_ties++;
    }
    const double t_chi = now_s() - t0;
    printf("[verify E] Terras stopping time chi over n in [3, %llu]: max %lld at n = %llu (ties %llu, exceptions %d)\n", (unsigned long long)chi_hi, chi_best, (unsigned long long)chi_arg, (unsigned long long)chi_ties, chi_bad);

    /* ---------- 小表导出（供 OEIS 逐条核对） ---------- */
    if (lens_path != NULL) {
        FILE *fl = fopen(lens_path, "w");
        if (fl == NULL) { fprintf(stderr, "cannot write %s\n", lens_path); return 3; }
        const uint64_t lm = (n_limit < 1000000ULL) ? n_limit : 1000000ULL;
        for (uint64_t n = 1ULL; n <= lm; n++) fprintf(fl, "%llu\t%u\n", (unsigned long long)n, (unsigned)tab[n]);
        fclose(fl);
        printf("[dump] wrote (n, len[n]) for n in [1, %llu] to %s\n", (unsigned long long)lm, lens_path);
    }
    if (rec_path != NULL) printf("[dump] wrote record table to %s\n", rec_path);

    /* ---------- 计时汇总 ---------- */
    const double t_all = now_s() - t_start;
    printf("\n== timing ==\n");
    printf("alloc %.2f s\n", t_alloc);
    printf("fill %.2f s\n", t_fill);
    printf("unknown scan %.2f s\n", t_unknown);
    printf("record scan %.2f s\n", t_rec);
    printf("verify A %.2f s\n", t_va);
    printf("verify B %.2f s\n", t_vb);
    printf("verify C %.2f s\n", t_vc);
    printf("verify D %.2f s\n", t_vd);
    printf("verify E %.2f s\n", t_chi);
    printf("total %.2f s\n", t_all);
    printf("\nRESULT: ALL CHECKS PASSED\n");
    free(tab);
    tab = NULL;
    return 0;
}
