/* route2_vm_main.c — 顶点穷举驱动器：字典序确定性分片、多线程、后处理与判定输出
 * 构建： cc -O2 -Wall -Wextra route2_vm_main.c route2_vm_core.c -lgmp -lpthread -o route2_vm_enum
 * 语义锚：frozen/r2_common.py（md5 cfee819667c0883e73732f03d2dc8bef）
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <time.h>
#include <pthread.h>
#include <gmp.h>
#include "route2_vm_core.h"

int M = 0;
int N = 0;
unsigned long P = 0;
unsigned long Q = 0;
mpq_t Wq;
mpq_t powd[MAXM + 1];
mpq_t invpowd[MAXM + 1];

static mpq_t Vq; /* v = W(δ−1)/(δ^M−1) */
static long long Total = 0;
static unsigned char *Dec = NULL;
static int CrossMode = 2; /* 0=off, 1=alive, 2=full, 3=sample */
static long long Stride = 1009;
static long long ChunkSize = 0, NChunks = 0;
static int NThreads = 1;
static const char *Tag = "route2";
static long long Ctab[48][24];
static mpq_t G1, G2, G3, G4;

static long long NextChunk = 0;
static pthread_mutex_t mu_next = PTHREAD_MUTEX_INITIALIZER;
static pthread_mutex_t mu_cands = PTHREAD_MUTEX_INITIALIZER;
static pthread_mutex_t mu_log = PTHREAD_MUTEX_INITIALIZER;

#define CAND_CAP 65536

typedef struct {
    long long idx;
    unsigned char S[MAXM];
    mpq_t y[MAXM];
    int used;
} cand_t;

static cand_t *Cands = NULL;
static long long NCands = 0;
static long long CROSS_COMPARED = 0, CROSS_MISMATCH = 0, CROSS_SOL_CMP = 0;

static long long now_ns(void)
{
    struct timespec ts;
    if (clock_gettime(CLOCK_MONOTONIC, &ts) != 0)
        die("clock_gettime 失败", 4);
    return (long long)ts.tv_sec * 1000000000LL + ts.tv_nsec;
}

static long long binom_table(int n, int k)
{
    if (k < 0 || k > n || n < 0 || n >= 48 || k >= 24)
        return 0;
    if (k == 0 || k == n)
        return 1;
    return Ctab[n][k];
}

static void build_binom(void)
{
    for (int n = 0; n < 48; n++) {
        for (int k = 0; k < 24; k++) {
            if (k == 0 || k == n)
                Ctab[n][k] = 1;
            else if (k > n)
                Ctab[n][k] = 0;
            else
                Ctab[n][k] = Ctab[n - 1][k - 1] + Ctab[n - 1][k];
        }
    }
}

/* 字典序 unrank：把 [0, C(N,M)) 的下标映到升序 M 元组 */
static void unrank(long long idx, unsigned char *S)
{
    int r = M;
    long long k = idx;
    for (int i = 0; i < N && r > 0; i++) {
        long long cnt = binom_table(N - 1 - i, r - 1);
        if (k < cnt) {
            S[M - r] = (unsigned char)i;
            r--;
        } else {
            k -= cnt;
        }
    }
}

/* 升序元组的下一个组合（字典序）；返回 0 表示已是最后一个 */
static int next_comb(unsigned char *S)
{
    int i = M - 1;
    while (i >= 0 && S[i] == (unsigned char)(N - M + i))
        i--;
    if (i < 0)
        return 0;
    S[i]++;
    for (int j = i + 1; j < M; j++)
        S[j] = (unsigned char)(S[j - 1] + 1);
    return 1;
}

/* 候选顶点登记（固定上界，超出即报错，不扩容） */
static void cand_append(long long idx, const unsigned char *S, const mpq_t *y)
{
    pthread_mutex_lock(&mu_cands);
    if (NCands >= CAND_CAP) {
        pthread_mutex_unlock(&mu_cands);
        die("候选数超出上界 CAND_CAP（属异常，请检查参数）", 4);
    }
    cand_t *c = &Cands[NCands++];
    c->idx = idx;
    for (int i = 0; i < MAXM; i++)
        c->S[i] = S[i];
    if (!c->used) {
        for (int j = 0; j < MAXM; j++)
            mpq_init(c->y[j]);
        c->used = 1;
    }
    for (int j = 0; j < M; j++)
        mpq_set(c->y[j], y[j]);
    pthread_mutex_unlock(&mu_cands);
}

/* ---------- 分片处理 ---------- */
static void process_chunk(long long cid, work_t *w)
{
    long long lo = cid * ChunkSize;
    long long hi = lo + ChunkSize;
    if (hi > Total)
        hi = Total;
    unsigned char S[MAXM];
    unrank(lo, S);
    for (long long idx = lo; idx < hi; idx++) {
        unsigned pin_mask = 0, edge_mask = 0;
        int has_sum = 0;
        for (int i = 0; i < M; i++) {
            int c = S[i];
            if (c < M)
                pin_mask |= 1u << c;
            else if (c < 2 * M)
                edge_mask |= 1u << (c - M);
            else
                has_sum = 1;
        }
        int do_time = ((idx % 277) == 0);
        long long t0 = do_time ? now_ns() : 0;
        int aliveA = 0;
        char chA = structure_solve(w, pin_mask, edge_mask, has_sum, &aliveA);
        if (do_time) {
            w->ns_a += now_ns() - t0;
            w->cnt_a++;
        }
        int wantB = 0;
        if (CrossMode == 2)
            wantB = 1;
        else if (CrossMode == 1)
            wantB = (chA != 'S');
        else if (CrossMode == 3)
            wantB = (chA != 'S') || ((idx % Stride) == 0);
        if (wantB) {
            t0 = do_time ? now_ns() : 0;
            int aliveB = 0;
            char chB = generic_solve(w, pin_mask, edge_mask, has_sum, &aliveB);
            if (do_time) {
                w->ns_b += now_ns() - t0;
                w->cnt_b++;
            }
            __sync_fetch_and_add(&CROSS_COMPARED, 1);
            if (chA != chB) {
                pthread_mutex_lock(&mu_log);
                fprintf(stderr, "MISMATCH 判定 子集#%lld chA=%c chB=%c\n", idx, chA, chB);
                fflush(stderr);
                pthread_mutex_unlock(&mu_log);
                __sync_fetch_and_add(&CROSS_MISMATCH, 1);
                w->nmismatch++;
            } else if (aliveA && aliveB) {
                int same = 1;
                for (int j = 0; j < M; j++) {
                    if (mpq_cmp(w->y[j], w->sol[j]) != 0) {
                        same = 0;
                        break;
                    }
                }
                __sync_fetch_and_add(&CROSS_SOL_CMP, 1);
                if (!same) {
                    pthread_mutex_lock(&mu_log);
                    fprintf(stderr, "MISMATCH 解向量 子集#%lld\n", idx);
                    fflush(stderr);
                    pthread_mutex_unlock(&mu_log);
                    __sync_fetch_and_add(&CROSS_MISMATCH, 1);
                    w->nmismatch++;
                }
            }
        }
        Dec[idx] = (unsigned char)chA;
        if (chA == 'F')
            cand_append(idx, S, (const mpq_t *)w->y);
        if (idx + 1 < hi)
            next_comb(S);
    }
}

static void *worker(void *arg)
{
    work_t *w = (work_t *)arg;
    for (;;) {
        pthread_mutex_lock(&mu_next);
        long long cid = NextChunk;
        if (cid >= NChunks) {
            pthread_mutex_unlock(&mu_next);
            break;
        }
        NextChunk++;
        pthread_mutex_unlock(&mu_next);
        long long lo = cid * ChunkSize;
        long long hi = lo + ChunkSize;
        if (hi > Total)
            hi = Total;
        process_chunk(cid, w);
        if (w->first_cid < 0) {
            w->first_cid = cid;
            w->first_lo = lo;
        }
        w->last_cid = cid;
        w->last_hi = hi;
        w->n_chunks++;
        w->n_sets += hi - lo;
    }
    return NULL;
}

/* ---------- 后处理 ---------- */
typedef struct {
    char *key;
    long long idx;
} keyref_t;

static int keyref_less(const keyref_t *a, const keyref_t *b)
{
    int c = strcmp(a->key, b->key);
    if (c)
        return c < 0;
    return a->idx < b->idx;
}

/* 迭代式自底向上归并排序（按 (key, idx)；避免递归与库回调） */
static void merge_sort_keyref(keyref_t *a, keyref_t *tmp, long long n)
{
    for (long long width = 1; width < n; width *= 2) {
        for (long long i = 0; i < n; i += 2 * width) {
            long long lo = i;
            long long mid = i + width < n ? i + width : n;
            long long hi = i + 2 * width < n ? i + 2 * width : n;
            long long p = lo, q = mid, t = lo;
            while (p < mid && q < hi) {
                if (keyref_less(&a[q], &a[p]))
                    tmp[t++] = a[q++];
                else
                    tmp[t++] = a[p++];
            }
            while (p < mid)
                tmp[t++] = a[p++];
            while (q < hi)
                tmp[t++] = a[q++];
            for (long long k = lo; k < hi; k++)
                a[k] = tmp[k];
        }
    }
}

static long long parse_ll(const char *s, const char *what, long long lo, long long hi)
{
    errno = 0;
    char *end = NULL;
    long long v = strtoll(s, &end, 10);
    if (errno != 0 || end == s || *end != '\0' || v < lo || v > hi) {
        fprintf(stderr, "参数 %s 非法：%s\n", what, s);
        exit(1);
    }
    return v;
}

int main(int argc, char **argv)
{
    if (argc < 7) {
        fputs("用法： route2_vm_enum <M> <P> <Q> <Wstr> <threads> <decisions_out> "
              "[--cross full|alive|off|sample:K] [--chunkmap PATH] "
              "[--expect-total N] [--expect-vertices N] [--tag STR]\n",
              stderr);
        return 1;
    }
    M = (int)parse_ll(argv[1], "M", 2, MAXM);
    P = (unsigned long)parse_ll(argv[2], "P", 1, 1000000000LL);
    Q = (unsigned long)parse_ll(argv[3], "Q", 1, 1000000000LL);
    N = 2 * M + 1;
    mpq_init(Wq);
    if (mpq_set_str(Wq, argv[4], 10) != 0) {
        fputs("W 解析失败\n", stderr);
        return 1;
    }
    mpq_canonicalize(Wq);
    if (mpq_sgn(Wq) < 0) {
        fputs("W 必须非负\n", stderr);
        return 1;
    }
    NThreads = (int)parse_ll(argv[5], "threads", 1, 64);
    const char *dec_path = argv[6];
    const char *chunkmap_path = NULL;
    long long expect_total = -1, expect_vertices = -1;

    for (int i = 7; i < argc; i++) {
        if (!strcmp(argv[i], "--cross") && i + 1 < argc) {
            const char *v = argv[++i];
            if (!strcmp(v, "full"))
                CrossMode = 2;
            else if (!strcmp(v, "alive"))
                CrossMode = 1;
            else if (!strcmp(v, "off"))
                CrossMode = 0;
            else if (!strncmp(v, "sample:", 7)) {
                CrossMode = 3;
                Stride = parse_ll(v + 7, "sample:K", 1, (long long)1 << 40);
            } else {
                fputs("未知 --cross 值\n", stderr);
                return 1;
            }
        } else if (!strcmp(argv[i], "--chunkmap") && i + 1 < argc) {
            chunkmap_path = argv[++i];
        } else if (!strcmp(argv[i], "--expect-total") && i + 1 < argc) {
            expect_total = parse_ll(argv[++i], "expect-total", 0, (long long)1 << 40);
        } else if (!strcmp(argv[i], "--expect-vertices") && i + 1 < argc) {
            expect_vertices = parse_ll(argv[++i], "expect-vertices", 0, (long long)1 << 40);
        } else if (!strcmp(argv[i], "--tag") && i + 1 < argc) {
            Tag = argv[++i];
        } else {
            fputs("未知选项\n", stderr);
            return 1;
        }
    }

    build_binom();
    for (int t = 0; t <= MAXM; t++) {
        mpq_init(powd[t]);
        mpq_init(invpowd[t]);
    }
    mpq_init(G1);
    mpq_init(G2);
    mpq_init(G3);
    mpq_init(G4);
    mpq_init(Vq);
    mpq_set_ui(powd[0], 1, 1);
    mpq_set_ui(invpowd[0], 1, 1);
    for (int t = 1; t <= MAXM; t++) {
        mpq_set_ui(G1, P, Q);
        mpq_mul(powd[t], powd[t - 1], G1);
        mpq_set_ui(G1, Q, P);
        mpq_mul(invpowd[t], invpowd[t - 1], G1);
    }
    mpq_set_ui(G1, P, Q); /* δ */
    mpq_set_ui(G4, 1, 1);
    mpq_sub(G2, G1, G4);      /* δ − 1 */
    mpq_sub(G3, powd[M], G4); /* δ^M − 1 */
    mpq_mul(Vq, Wq, G2);
    mpq_div(Vq, Vq, G3);

    long long t_mult = 1;
    for (int i = 0; i < M; i++)
        t_mult = t_mult * (N - i) / (i + 1);
    long long t_pas = binom_table(N, M);
    Total = t_mult;

    printf("[%s] route2_vm_enum — 全活跃子集顶点精确穷举\n", Tag);
    printf("PARAMS M=%d N=%d delta=%lu/%lu W=", M, N, P, Q);
    {
        char *w_str = frac_str(Wq);
        printf("%s threads=%d cross=%s\n", w_str, NThreads,
               CrossMode == 2 ? "full" : CrossMode == 1 ? "alive" : CrossMode == 3 ? "sample" : "off");
        free(w_str);
    }
    printf("TOTAL_SUBSETS mult=%lld pascal=%lld equal=%s\n", t_mult, t_pas,
           t_mult == t_pas ? "True" : "False");
    if (t_mult != t_pas || Total <= 0 || Total > ((long long)1 << 31)) {
        printf("EXIT_FAIL\n");
        return 2;
    }
    if (expect_total >= 0) {
        printf("EXPECT_TOTAL %s (%lld)\n", Total == expect_total ? "PASS" : "FAIL", expect_total);
        if (Total != expect_total) {
            printf("EXIT_FAIL\n");
            return 2;
        }
    }
    ChunkSize = (Total + 511) / 512;
    if (ChunkSize < 4096)
        ChunkSize = 4096;
    NChunks = (Total + ChunkSize - 1) / ChunkSize;

    {
        unsigned char a[MAXM], b[MAXM];
        int ok = 1;
        for (long long cid = 1; cid < NChunks; cid++) {
            long long b0 = cid * ChunkSize;
            unrank(b0 - 1, a);
            unrank(b0, b);
            if (!next_comb(a)) {
                ok = 0;
                break;
            }
            if (memcmp(a, b, (size_t)M) != 0) {
                ok = 0;
                break;
            }
        }
        printf("ENUM_CONTINUITY_CHECK %s\n", ok ? "PASS" : "FAIL");
        if (!ok) {
            printf("EXIT_FAIL\n");
            return 2;
        }
    }

    Dec = (unsigned char *)malloc((size_t)Total);
    if (!Dec)
        die("内存不足（Dec）", 4);
    memset(Dec, '?', (size_t)Total);
    Cands = (cand_t *)malloc(sizeof(cand_t) * CAND_CAP);
    if (!Cands)
        die("内存不足（Cands）", 4);
    for (long long i = 0; i < CAND_CAP; i++)
        Cands[i].used = 0;

    long long t_start = now_ns();
    pthread_t *th = (pthread_t *)malloc(sizeof(pthread_t) * (size_t)NThreads);
    work_t **ws = (work_t **)malloc(sizeof(work_t *) * (size_t)NThreads);
    if (!th || !ws)
        die("分配失败", 4);
    for (int t = 0; t < NThreads; t++) {
        ws[t] = (work_t *)malloc(sizeof(work_t));
        if (!ws[t])
            die("分配失败（work_t）", 4);
        work_init(ws[t], t);
        if (pthread_create(&th[t], NULL, worker, ws[t]) != 0)
            die("pthread_create 失败", 4);
    }
    for (int t = 0; t < NThreads; t++)
        pthread_join(th[t], NULL);
    long long t_enum = now_ns() - t_start;

    long long nS = 0, nI = 0, nF = 0, nq = 0;
    for (long long i = 0; i < Total; i++) {
        if (Dec[i] == 'S')
            nS++;
        else if (Dec[i] == 'I')
            nI++;
        else if (Dec[i] == 'F')
            nF++;
        else
            nq++;
    }
    printf("DECISIONS_COMPLETE %s (undecided=%lld)\n", nq == 0 ? "PASS" : "FAIL", nq);
    printf("DECISION_COUNTS S=%lld I=%lld F=%lld total=%lld\n", nS, nI, nF, nS + nI + nF);
    printf("CROSSCHECK compared=%lld sol_cmp=%lld mismatches=%lld mode=%d\n", CROSS_COMPARED, CROSS_SOL_CMP,
           CROSS_MISMATCH, CrossMode);
    for (int t = 0; t < NThreads; t++) {
        work_t *w = ws[t];
        long long fend = (w->first_cid < 0) ? -1
                          : (w->first_lo + ChunkSize > Total ? Total : w->first_lo + ChunkSize);
        printf("THREAD %d chunks=%lld sets=%lld first_chunk=%lld first_range=[%lld,%lld) last_chunk=%lld last_range=[%lld,%lld)\n",
               t, w->n_chunks, w->n_sets, w->first_cid, w->first_lo, fend, w->last_cid,
               w->last_cid < 0 ? -1 : w->last_cid * ChunkSize, w->last_hi);
    }
    long long sum_sets = 0;
    for (int t = 0; t < NThreads; t++)
        sum_sets += ws[t]->n_sets;
    printf("THREAD_SETS_SUM %lld (== total : %s)\n", sum_sets, sum_sets == Total ? "True" : "False");
    {
        long long ta = 0, tb = 0, ca = 0, cb = 0;
        for (int t = 0; t < NThreads; t++) {
            ta += ws[t]->ns_a;
            tb += ws[t]->ns_b;
            ca += ws[t]->cnt_a;
            cb += ws[t]->cnt_b;
        }
        if (ca)
            printf("TIME_SAMPLE pathA n=%lld avg_ns=%.1f\n", ca, (double)ta / (double)ca);
        if (cb)
            printf("TIME_SAMPLE pathB n=%lld avg_ns=%.1f\n", cb, (double)tb / (double)cb);
    }
    printf("ENUM_WALL_SEC %.3f\n", (double)t_enum / 1e9);

    if (chunkmap_path) {
        FILE *f = fopen(chunkmap_path, "w");
        if (!f) {
            fputs("无法写 chunkmap\n", stderr);
        } else {
            fprintf(f, "# 分片范围（cid lo hi；范围与线程调度无关）\n");
            for (long long cid = 0; cid < NChunks; cid++) {
                long long lo = cid * ChunkSize;
                long long hi = lo + ChunkSize;
                if (hi > Total)
                    hi = Total;
                fprintf(f, "%lld %lld %lld\n", cid, lo, hi);
            }
            fclose(f);
            printf("CHUNKMAP %s chunks=%lld\n", chunkmap_path, NChunks);
        }
    }

    printf("FEASIBLE_SUBSETS %lld\n", NCands);
    keyref_t *kr = (keyref_t *)malloc(sizeof(keyref_t) * (size_t)(NCands ? NCands : 1));
    keyref_t *ktmp = (keyref_t *)malloc(sizeof(keyref_t) * (size_t)(NCands ? NCands : 1));
    if (!kr || !ktmp)
        die("分配失败（keyref）", 4);
    for (long long i = 0; i < NCands; i++) {
        kr[i].key = key_of((const mpq_t *)Cands[i].y);
        kr[i].idx = i;
    }
    merge_sort_keyref(kr, ktmp, NCands);
    long long nverts = 0;
    long long *group_start = (long long *)malloc(sizeof(long long) * (size_t)(NCands ? NCands : 1));
    if (!group_start)
        die("分配失败（group_start）", 4);
    for (long long i = 0; i < NCands;) {
        long long j = i;
        while (j < NCands && strcmp(kr[j].key, kr[i].key) == 0)
            j++;
        group_start[nverts++] = i;
        i = j;
    }
    printf("VERTEX_COUNT %lld\n", nverts);
    if (expect_vertices >= 0)
        printf("EXPECT_VERTICES %s (%lld)\n", nverts == expect_vertices ? "PASS" : "FAIL", expect_vertices);

    {
        work_t *w = (work_t *)malloc(sizeof(work_t));
        if (!w)
            die("分配失败（work_t 后处理）", 4);
        work_init(w, -1);
        for (long long g = 0; g < nverts; g++) {
            long long i = group_start[g];
            long long j = (g + 1 < nverts) ? group_start[g + 1] : NCands;
            cand_t *c0 = &Cands[kr[i].idx];
            int nact = 0, rk = 0;
            active_cert(w, (const mpq_t *)c0->y, &nact, &rk);
            printf("VERTEX %lld coords=", g);
            for (int v = 0; v < M; v++) {
                char *fs = frac_str(c0->y[v]);
                printf("%s%s", v ? ";" : "", fs);
                free(fs);
            }
            printf("\n");
            printf("VERTEX %lld certs=%lld cert_subset_idxs=", g, j - i);
            for (long long k = i; k < j; k++) {
                cand_t *c = &Cands[kr[k].idx];
                printf("%s%lld[", k > i ? "," : "", c->idx);
                for (int v = 0; v < M; v++)
                    printf(v ? ",%u" : "%u", (unsigned)c->S[v]);
                printf("]");
            }
            printf("\n");
            printf("VERTEX %lld active_count=%d active_rank=%d\n", g, nact, rk);
        }
    }

    {
        char *vs = frac_str(Vq);
        printf("ANALYTIC v=%s\n", vs);
        free(vs);
    }
    {
        char **ak = (char **)malloc(sizeof(char *) * (size_t)M);
        if (!ak)
            die("分配失败（ak）", 4);
        for (int r = 0; r < M; r++) {
            mpq_t yy[MAXM];
            for (int j = 0; j < M; j++) {
                mpq_init(yy[j]);
                mpq_mul(yy[j], Vq, powd[(j + r) % M]);
            }
            ak[r] = key_of((const mpq_t *)yy);
            for (int j = 0; j < M; j++)
                mpq_clear(yy[j]);
        }
        long long match = 0;
        unsigned char *found = (unsigned char *)malloc((size_t)(nverts ? nverts : 1));
        if (!found)
            die("分配失败（found）", 4);
        for (long long g = 0; g < nverts; g++)
            found[g] = 0;
        for (int r = 0; r < M; r++) {
            int hit = 0;
            for (long long g = 0; g < nverts; g++) {
                if (strcmp(ak[r], kr[group_start[g]].key) == 0) {
                    hit = 1;
                    found[g] = 1;
                    break;
                }
            }
            if (hit)
                match++;
            else
                printf("ANALYTIC_MISSING r=%d key=%s\n", r, ak[r]);
        }
        for (long long g = 0; g < nverts; g++) {
            if (!found[g])
                printf("ANALYTIC_EXTRA vertex=%lld key=%s\n", g, kr[group_start[g]].key);
        }
        printf("ANALYTIC_COUNT %d VERTEX_COUNT %lld MATCH %lld SETS_EQUAL %s\n", M, nverts, match,
               (match == M && nverts == M) ? "True" : "False");
        free(found);
    }

    {
        FILE *f = fopen(dec_path, "wb");
        if (!f)
            die("无法写判定文件", 4);
        size_t wr = fwrite(Dec, 1, (size_t)Total, f);
        if (fclose(f) != 0)
            die("关闭判定文件失败", 4);
        printf("DECISIONS_FILE %s bytes=%zu\n", dec_path, wr);
    }
    printf("MISMATCHES_TOTAL %lld\n", CROSS_MISMATCH);
    printf("%s\n", CROSS_MISMATCH == 0 ? "EXIT_OK" : "EXIT_FAIL");
    return CROSS_MISMATCH == 0 ? 0 : 5;
}

