/* route2_vm_core.h — 顶点穷举器公共声明（route2 轨道） */
#ifndef ROUTE2_VM_CORE_H
#define ROUTE2_VM_CORE_H

#include <gmp.h>

#define MAXM 16
#define MAXN (2 * MAXM + 1)

/* 全局参数（在 route2_vm_main.c 中定义） */
extern int M;
extern int N;
extern unsigned long P;
extern unsigned long Q;
extern mpq_t Wq;                          /* W */
extern mpq_t powd[MAXM + 1];              /* δ^t */
extern mpq_t invpowd[MAXM + 1];           /* δ^(−t) */

/* 每线程工作区（只堆分配，禁止放栈上） */
typedef struct {
    int tid;
    mpq_t A[MAXN][MAXM + 1]; /* 通用消元矩阵 / 活跃行秩矩阵 */
    mpq_t sol[MAXM];
    mpq_t y[MAXM];
    mpq_t C[MAXM], h[MAXM];
    mpq_t acc, acc2, tmp, pv, f;
    long long ns_a, cnt_a, ns_b, cnt_b;
    long long n_chunks, n_sets;
    long long first_cid, last_cid, first_lo, last_hi;
    long long nmismatch;
} work_t;

void work_init(work_t *w, int tid);
char feasible_q(const mpq_t *y, mpq_t t1, mpq_t t2);
char structure_solve(work_t *w, unsigned pin_mask, unsigned edge_mask, int has_sum, int *alive_out);
char generic_solve(work_t *w, unsigned pin_mask, unsigned edge_mask, int has_sum, int *alive_out);
void active_cert(work_t *w, const mpq_t *y, int *nactive_out, int *rank_out);
char *frac_str(const mpq_t q);
char *key_of(const mpq_t *y);
void die(const char *msg, int code);

#endif
