/* route2_vm_core.c — 顶点穷举器核心：两路精确求解与辅助
 * 语义锚：frozen/r2_common.py（md5 cfee819667c0883e73732f03d2dc8bef）
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "route2_vm_core.h"

static int popcount_u(unsigned x)
{
    int c = 0;
    while (x) {
        c += (int)(x & 1u);
        x >>= 1;
    }
    return c;
}

void die(const char *msg, int code)
{
    fprintf(stderr, "错误：%s\n", msg);
    exit(code);
}

void work_init(work_t *w, int tid)
{
    w->tid = tid;
    for (int i = 0; i < MAXN; i++)
        for (int j = 0; j <= MAXM; j++)
            mpq_init(w->A[i][j]);
    for (int i = 0; i < MAXM; i++) {
        mpq_init(w->sol[i]);
        mpq_init(w->y[i]);
        mpq_init(w->C[i]);
        mpq_init(w->h[i]);
    }
    mpq_init(w->acc);
    mpq_init(w->acc2);
    mpq_init(w->tmp);
    mpq_init(w->pv);
    mpq_init(w->f);
    w->ns_a = w->cnt_a = w->ns_b = w->cnt_b = 0;
    w->n_chunks = w->n_sets = 0;
    w->first_cid = w->last_cid = -1;
    w->first_lo = w->last_hi = -1;
    w->nmismatch = 0;
}

/* q 的精确字符串 "num/den"（调用方 free） */
char *frac_str(const mpq_t q)
{
    char *np = mpz_get_str(NULL, 10, mpq_numref(q));
    char *dp = mpz_get_str(NULL, 10, mpq_denref(q));
    if (!np || !dp) {
        free(np);
        free(dp);
        die("mpz_get_str 失败", 4);
    }
    size_t ln = strlen(np), ld = strlen(dp);
    char *s = (char *)malloc(ln + ld + 2);
    if (!s) {
        free(np);
        free(dp);
        die("分配失败", 4);
    }
    memcpy(s, np, ln);
    s[ln] = '/';
    memcpy(s + ln + 1, dp, ld);
    s[ln + ld + 1] = '\0';
    free(np);
    free(dp);
    return s;
}

/* y 的坐标键（分号分隔；调用方 free）。先精确算长度再一次分配。 */
char *key_of(const mpq_t *y)
{
    size_t need = 1;
    for (int j = 0; j < M; j++) {
        need += mpz_sizeinbase(mpq_numref(y[j]), 10) + 1;
        need += mpz_sizeinbase(mpq_denref(y[j]), 10) + 1;
        need += 1; /* '/' 或 ';' 或表尾 */
    }
    char *buf = (char *)malloc(need);
    if (!buf)
        die("分配失败", 4);
    size_t len = 0;
    for (int j = 0; j < M; j++) {
        if (j)
            buf[len++] = ';';
        mpz_get_str(buf + len, 10, mpq_numref(y[j]));
        len += strlen(buf + len);
        if (len + 1 >= need) {
            free(buf);
            die("键缓冲越界（分子）", 4);
        }
        buf[len++] = '/';
        mpz_get_str(buf + len, 10, mpq_denref(y[j]));
        len += strlen(buf + len);
        if (len + 1 > need) {
            free(buf);
            die("键缓冲越界（分母）", 4);
        }
    }
    buf[len] = '\0';
    return buf;
}

/* 可行性（精确；与 r2_common.feasible 同语义）
 * 链约束 y_{j+1} <= δ y_j ⟺ Q y_{j+1} <= P y_j（Q > 0），精确比较 */
char feasible_q(const mpq_t *y, mpq_t t1, mpq_t t2)
{
    for (int j = 0; j < M; j++) {
        if (mpq_cmp_ui(y[j], 1, 1) < 0)
            return 0;
    }
    for (int j = 0; j < M; j++) {
        int jn = (j + 1) % M;
        mpq_set_ui(t1, P, 1);
        mpq_mul(t1, t1, y[j]); /* P y_j */
        mpq_set_ui(t2, Q, 1);
        mpq_mul(t2, t2, y[jn]); /* Q y_{j+1} */
        if (mpq_cmp(t1, t2) < 0)
            return 0; /* y_{j+1} > δ y_j */
    }
    mpq_set_ui(t1, 0, 1);
    for (int j = 0; j < M; j++)
        mpq_add(t1, t1, y[j]);
    if (mpq_cmp(t1, Wq) < 0)
        return 0;
    return 1;
}

/* 路径 A：结构分解。唯一解 ⟺（无同分量双签）且（(s=0 且签分量数=分量数) 或 (s=1 且签分量数=分量数−1)） */
char structure_solve(work_t *w, unsigned pin_mask, unsigned edge_mask, int has_sum, int *alive_out)
{
    int ne = popcount_u(edge_mask);
    int alive = 0;
    if (ne == M) {
        /* S = 全部链约束：绕行一圈得 (P^M − Q^M)y = 0，P ≠ Q，唯一解零向量（不可行） */
        for (int j = 0; j < M; j++)
            mpq_set_ui(w->y[j], 0, 1);
        alive = 1;
    } else {
        int jstar = -1;
        for (int j = 0; j < M; j++) {
            if (!((edge_mask >> j) & 1)) {
                jstar = j;
                break;
            }
        }
        int v0 = (jstar + 1) % M;
        int comp[MAXM], dist[MAXM];
        int ncomp = 1;
        comp[v0] = 0;
        dist[v0] = 0;
        for (int step = 1; step < M; step++) {
            int v = (v0 + step) % M;
            int prev = (v + M - 1) % M;
            if ((edge_mask >> prev) & 1) {
                comp[v] = comp[prev];
                dist[v] = dist[prev] + 1;
            } else {
                comp[v] = ncomp++;
                dist[v] = 0;
            }
        }
        int pin_of_comp[MAXM];
        for (int c = 0; c < ncomp; c++)
            pin_of_comp[c] = -1;
        int dup = 0;
        for (int p = 0; p < M; p++) {
            if ((pin_mask >> p) & 1) {
                int c = comp[p];
                if (pin_of_comp[c] >= 0)
                    dup = 1;
                else
                    pin_of_comp[c] = p;
            }
        }
        int npc = 0;
        for (int c = 0; c < ncomp; c++) {
            if (pin_of_comp[c] >= 0)
                npc++;
        }
        int s = has_sum;
        int k = ncomp; /* = M − ne */
        alive = (!dup) && ((s == 0 && npc == k) || (s == 1 && npc == k - 1));
        if (alive) {
            for (int c = 0; c < ncomp; c++)
                mpq_set_ui(w->C[c], 0, 1);
            for (int v = 0; v < M; v++)
                mpq_add(w->C[comp[v]], w->C[comp[v]], powd[dist[v]]);
            if (s == 0) {
                for (int c = 0; c < ncomp; c++)
                    mpq_set(w->h[c], invpowd[dist[pin_of_comp[c]]]);
            } else {
                mpq_set_ui(w->acc, 0, 1);
                int c0 = -1;
                for (int c = 0; c < ncomp; c++) {
                    if (pin_of_comp[c] >= 0) {
                        mpq_set(w->h[c], invpowd[dist[pin_of_comp[c]]]);
                        mpq_mul(w->tmp, w->C[c], w->h[c]);
                        mpq_add(w->acc, w->acc, w->tmp);
                    } else {
                        c0 = c;
                    }
                }
                mpq_sub(w->acc2, Wq, w->acc);
                mpq_div(w->h[c0], w->acc2, w->C[c0]);
            }
            for (int v = 0; v < M; v++)
                mpq_mul(w->y[v], powd[dist[v]], w->h[comp[v]]);
        }
    }
    *alive_out = alive;
    if (!alive)
        return 'S';
    return feasible_q((const mpq_t *)w->y, w->tmp, w->acc2) ? 'F' : 'I';
}

/* 路径 B：通用 mpq RREF（同 r2_common.solve_exact 的算法序；行缩放不改解集） */
char generic_solve(work_t *w, unsigned pin_mask, unsigned edge_mask, int has_sum, int *alive_out)
{
    int row = 0;
    for (int j = 0; j < M; j++) {
        if ((pin_mask >> j) & 1) {
            for (int c = 0; c <= M; c++)
                mpq_set_ui(w->A[row][c], 0, 1);
            mpq_set_ui(w->A[row][j], 1, 1);
            mpq_set_ui(w->A[row][M], 1, 1);
            row++;
        }
    }
    for (int j = 0; j < M; j++) {
        if ((edge_mask >> j) & 1) {
            for (int c = 0; c <= M; c++)
                mpq_set_ui(w->A[row][c], 0, 1);
            mpq_set_si(w->A[row][j], -(long)P, 1);
            mpq_set_ui(w->A[row][(j + 1) % M], Q, 1);
            mpq_set_ui(w->A[row][M], 0, 1);
            row++;
        }
    }
    if (has_sum) {
        for (int c = 0; c < M; c++)
            mpq_set_ui(w->A[row][c], 1, 1);
        mpq_set(w->A[row][M], Wq);
        row++;
    }
    if (row != M)
        die("内部错误：行数与 M 不符", 3);

    int rank = 0;
    int pivots[MAXM];
    for (int col = 0; col < M; col++) {
        int piv = -1;
        for (int i = rank; i < M; i++) {
            if (mpq_sgn(w->A[i][col]) != 0) {
                piv = i;
                break;
            }
        }
        if (piv < 0)
            continue;
        if (piv != rank) {
            for (int c = 0; c <= M; c++)
                mpq_swap(w->A[rank][c], w->A[piv][c]);
        }
        mpq_set(w->pv, w->A[rank][col]);
        for (int c = 0; c <= M; c++)
            mpq_div(w->A[rank][c], w->A[rank][c], w->pv);
        for (int i = 0; i < M; i++) {
            if (i == rank || mpq_sgn(w->A[i][col]) == 0)
                continue;
            mpq_set(w->f, w->A[i][col]);
            for (int c = 0; c <= M; c++) {
                mpq_mul(w->tmp, w->f, w->A[rank][c]);
                mpq_sub(w->A[i][c], w->A[i][c], w->tmp);
            }
        }
        pivots[rank] = col;
        rank++;
        if (rank == M)
            break;
    }
    for (int i = rank; i < M; i++) {
        int allzero = 1;
        for (int c = 0; c < M; c++) {
            if (mpq_sgn(w->A[i][c]) != 0) {
                allzero = 0;
                break;
            }
        }
        if (allzero && mpq_sgn(w->A[i][M]) != 0) {
            *alive_out = 0;
            return 'S';
        }
    }
    if (rank < M) {
        *alive_out = 0;
        return 'S';
    }
    for (int j = 0; j < M; j++)
        mpq_set_ui(w->sol[j], 0, 1);
    for (int i = 0; i < rank; i++)
        mpq_set(w->sol[pivots[i]], w->A[i][M]);
    *alive_out = 1;
    return feasible_q((const mpq_t *)w->sol, w->tmp, w->acc2) ? 'F' : 'I';
}

/* 活跃约束集（在点 y 处取等的约束）的（条数，秩） */
void active_cert(work_t *w, const mpq_t *y, int *nactive_out, int *rank_out)
{
    int ra = 0;
    for (int j = 0; j < M; j++) {
        if (mpq_cmp_ui(y[j], 1, 1) == 0) {
            for (int c = 0; c < M; c++)
                mpq_set_ui(w->A[ra][c], 0, 1);
            mpq_set_ui(w->A[ra][j], 1, 1);
            ra++;
        }
    }
    for (int j = 0; j < M; j++) {
        int jn = (j + 1) % M;
        mpq_set_ui(w->tmp, Q, 1);
        mpq_mul(w->tmp, w->tmp, y[jn]); /* Q y_{j+1} */
        mpq_set_ui(w->acc, P, 1);
        mpq_mul(w->acc, w->acc, y[j]); /* P y_j */
        if (mpq_cmp(w->tmp, w->acc) == 0) {
            for (int c = 0; c < M; c++)
                mpq_set_ui(w->A[ra][c], 0, 1);
            mpq_set_si(w->A[ra][j], -(long)P, 1);
            mpq_set_ui(w->A[ra][jn], Q, 1);
            ra++;
        }
    }
    mpq_set_ui(w->tmp, 0, 1);
    for (int j = 0; j < M; j++)
        mpq_add(w->tmp, w->tmp, y[j]);
    if (mpq_cmp(w->tmp, Wq) == 0) {
        for (int c = 0; c < M; c++)
            mpq_set_ui(w->A[ra][c], 1, 1);
        ra++;
    }
    int rank = 0;
    for (int col = 0; col < M; col++) {
        int piv = -1;
        for (int i = rank; i < ra; i++) {
            if (mpq_sgn(w->A[i][col]) != 0) {
                piv = i;
                break;
            }
        }
        if (piv < 0)
            continue;
        if (piv != rank) {
            for (int c = 0; c < M; c++)
                mpq_swap(w->A[rank][c], w->A[piv][c]);
        }
        mpq_set(w->pv, w->A[rank][col]);
        for (int c = col; c < M; c++)
            mpq_div(w->A[rank][c], w->A[rank][c], w->pv);
        for (int i = 0; i < ra; i++) {
            if (i == rank || mpq_sgn(w->A[i][col]) == 0)
                continue;
            mpq_set(w->f, w->A[i][col]);
            for (int c = col; c < M; c++) {
                mpq_mul(w->tmp, w->f, w->A[rank][c]);
                mpq_sub(w->A[i][c], w->A[i][c], w->tmp);
            }
        }
        rank++;
    }
    *nactive_out = ra;
    *rank_out = rank;
}
